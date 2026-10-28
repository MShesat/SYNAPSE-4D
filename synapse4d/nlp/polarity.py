"""
Polarity and Antonym Opposition Engine for Synapse 4D.

Addresses the semantic cosine pitfall where contradictory statements
(e.g., "use postgresql" vs "avoid postgresql") yield high vector similarity (>0.85).
Combines dense embeddings with syntactic negation and canonical antonym detection.
"""

from __future__ import annotations
import re
import unicodedata
from typing import Dict, Set, Tuple


def normalize_text(text: str) -> str:
    """Normalize text: lowercase, strip accents, remove excess whitespace."""
    text = text.lower().strip()
    nfkd = unicodedata.normalize("NFKD", text)
    without_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r"[^\w\s]", " ", without_accents)


# Canonical paired antonyms (symmetric mapping)
_ANTONYM_PAIRS: list[Tuple[str, str]] = [
    # ES
    ("usa", "evita"),
    ("usar", "evitar"),
    ("utiliza", "evita"),
    ("utilizar", "evitar"),
    ("activar", "desactivar"),
    ("activa", "desactiva"),
    ("habilitar", "deshabilitar"),
    ("habilita", "deshabilita"),
    ("permitir", "prohibir"),
    ("permite", "prohibe"),
    ("sincrono", "asincrono"),
    ("sync", "async"),
    ("local", "cloud"),
    ("local", "nube"),
    ("verdadero", "falso"),
    ("incluir", "excluir"),
    ("incluye", "excluye"),
    ("siempre", "nunca"),
    ("obliga", "prohibe"),
    ("obligatorio", "prohibido"),
    # EN
    ("use", "avoid"),
    ("enable", "disable"),
    ("enabled", "disabled"),
    ("allow", "deny"),
    ("allow", "forbid"),
    ("allows", "forbids"),
    ("true", "false"),
    ("include", "exclude"),
    ("includes", "excludes"),
    ("always", "never"),
    ("mandatory", "forbidden"),
    ("required", "prohibited"),
]

# Build symmetric lookup dict
CANONICAL_ANTONYMS: Dict[str, Set[str]] = {}
for word_a, word_b in _ANTONYM_PAIRS:
    norm_a = normalize_text(word_a).strip()
    norm_b = normalize_text(word_b).strip()
    CANONICAL_ANTONYMS.setdefault(norm_a, set()).add(norm_b)
    CANONICAL_ANTONYMS.setdefault(norm_b, set()).add(norm_a)

# Syntactic negation markers (tokens indicating restrictive or inverted polarity)
NEGATION_MARKERS: Set[str] = {
    # ES
    "no",
    "nunca",
    "jamas",
    "sin",
    "tampoco",
    "evitar",
    "evita",
    "prohibido",
    "prohibir",
    "desactivar",
    "desactiva",
    "deshabilitar",
    "deshabilita",
    "desaconsejar",
    "desaconsejado",
    # EN
    "not",
    "never",
    "without",
    "neither",
    "nor",
    "avoid",
    "forbid",
    "forbidden",
    "disable",
    "disabled",
    "deny",
    "denied",
    "deprecate",
    "deprecated",
}


def stem_token(word: str) -> str:
    """Minimal Spanish/English suffix normalizer for common inflectional variants."""
    w = word.lower()
    if len(w) > 4:
        # Common Spanish gender and plural inflections
        if w.endswith(("os", "as", "es")):
            return w[:-2]
        if w.endswith(("o", "a", "e")):
            return w[:-1]
        # English plurals/gerunds
        if w.endswith("ing") and len(w) > 5:
            return w[:-3]
        if w.endswith("ed") and len(w) > 4:
            return w[:-2]
        if w.endswith("s") and len(w) > 3:
            return w[:-1]
    return w


def get_tokens(text: str) -> list[str]:
    """Tokenize normalized text into word tokens."""
    return [w for w in normalize_text(text).split() if w]


def get_stemmed_tokens(text: str) -> list[str]:
    """Tokenize and stem words for high-recall lexical matching."""
    return [stem_token(w) for w in get_tokens(text)]


def detect_polarity(text: str) -> int:
    """
    Detect semantic polarity of a proposition.
    
    Returns:
        +1: Affirmative / constructive assertion
        -1: Negative / prohibitive / restrictive assertion
    """
    tokens = get_tokens(text)
    neg_count = sum(1 for t in tokens if t in NEGATION_MARKERS)
    
    # Odd number of negations = negative polarity (-1)
    # Even or 0 negations = positive polarity (+1)
    return -1 if (neg_count % 2 == 1) else 1


def find_antonym_clash(text_a: str, text_b: str) -> Tuple[bool, str, str]:
    """
    Check if text_a and text_b contain explicit antonym pairs.
    Returns: (has_clash, word_a, word_b)
    """
    tokens_a = set(get_tokens(text_a))
    tokens_b = set(get_tokens(text_b))

    for token in tokens_a:
        if token in CANONICAL_ANTONYMS:
            opponents = CANONICAL_ANTONYMS[token]
            matched = opponents.intersection(tokens_b)
            if matched:
                return True, token, next(iter(matched))

    return False, "", ""


def has_polar_opposition(text_a: str, text_b: str) -> bool:
    """
    Determine whether proposition A and proposition B are polar opposites.
    True if:
    1. One is affirmative and the other is negative, OR
    2. They contain direct canonical antonym words targeting the same domain.
    """
    pol_a = detect_polarity(text_a)
    pol_b = detect_polarity(text_b)

    if pol_a != pol_b:
        return True

    has_clash, _, _ = find_antonym_clash(text_a, text_b)
    return has_clash


# Canonical paired synonyms (ES/EN)
_SYNONYM_PAIRS: list[Tuple[str, str]] = [
    ("activar", "habilitar"),
    ("activa", "habilita"),
    ("usar", "utilizar"),
    ("usa", "utiliza"),
    ("backup", "copia"),
    ("backup", "seguridad"),
    ("backup", "respaldo"),
    ("realizar", "hacer"),
    ("realiza", "hace"),
    ("mantener", "asegurar"),
    ("baja", "minima"),
    ("enable", "activate"),
    ("use", "utilize"),
]

CANONICAL_SYNONYMS: Dict[str, Set[str]] = {}
for word_a, word_b in _SYNONYM_PAIRS:
    norm_a = normalize_text(word_a).strip()
    norm_b = normalize_text(word_b).strip()
    CANONICAL_SYNONYMS.setdefault(norm_a, set()).add(norm_b)
    CANONICAL_SYNONYMS.setdefault(norm_b, set()).add(norm_a)


def token_similarity_boost(text_a: str, text_b: str) -> float:
    """Calculate token overlap Jaccard score with synonym expansion and stemming."""
    raw_a = get_tokens(text_a)
    raw_b = get_tokens(text_b)
    
    tokens_a = set(raw_a)
    tokens_b = set(raw_b)
    
    # Expand synonyms
    exp_a = set(tokens_a)
    for t in tokens_a:
        if t in CANONICAL_SYNONYMS:
            exp_a.update(CANONICAL_SYNONYMS[t])

    exp_b = set(tokens_b)
    for t in tokens_b:
        if t in CANONICAL_SYNONYMS:
            exp_b.update(CANONICAL_SYNONYMS[t])

    # Add stemmed versions (using static list to avoid mutation during iteration)
    stems_a = [stem_token(t) for t in list(exp_a)]
    stems_b = [stem_token(t) for t in list(exp_b)]
    exp_a.update(stems_a)
    exp_b.update(stems_b)

    intersect = len(exp_a.intersection(exp_b))
    union = len(exp_a.union(exp_b))
    if union == 0:
        return 0.0
    return intersect / union


def compute_hybrid_similarity(cos_sim: float, text_a: str, text_b: str) -> float:
    """Combine vector cosine similarity with token synonym overlap."""
    tok_score = token_similarity_boost(text_a, text_b)
    # Blend: 70% vector dense + 30% lexical/synonym boost
    return 0.70 * cos_sim + 0.30 * tok_score


def classify_relation(
    sim: float,
    text_a: str,
    text_b: str,
    theta_redundant: float = 0.70,
    theta_conflict: float = 0.50,
) -> str:
    """
    Classify the relationship between two facts using both cosine similarity and polarity.
    
    Returns:
        'redundant': Same meaning and polarity (safe to merge / reinforce weight).
        'conflict': Semantic collision requiring D2 logical arbitration (supersession).
        'orthogonal': Complementary, coexisting or unrelated facts (no supersession).
    """
    is_polar_opp = has_polar_opposition(text_a, text_b)
    hybrid_sim = compute_hybrid_similarity(sim, text_a, text_b)

    # 1. Semantic overlap + Polar opposition = Direct Conflict (requiring arbitration)
    if (sim >= theta_conflict or hybrid_sim >= theta_conflict) and is_polar_opp:
        return "conflict"

    # 2. Polar opposition with reasonable similarity = Conflict
    if is_polar_opp and (sim >= 0.40 or hybrid_sim >= 0.40):
        return "conflict"

    # 3. High vector similarity OR high hybrid similarity without polar opposition = Redundant
    if (sim >= theta_redundant or hybrid_sim >= theta_redundant) and not is_polar_opp:
        return "redundant"

    # 4. Same polarity and moderate similarity: complementary or orthogonal (coexist in graph)
    return "orthogonal"
