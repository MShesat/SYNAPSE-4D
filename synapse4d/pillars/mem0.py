"""
Synapse 4D - Pillar 2: Mem0 (Fact Extraction & Deduplication Engine)
Inspired by Mem0 architecture: Atomic fact extraction, CRUD diffing,
and contradiction detection.
"""

import re
from typing import List, Dict, Any, Tuple

class Mem0FactExtractor:
    """Extracts atomic facts and detects conflicts/redundancies with existing knowledge."""

    def __init__(self):
        pass

    def extract_atomic_facts(self, raw_text: str) -> List[str]:
        """Extracts standalone atomic declarative statements from conversational or markdown text."""
        facts = []
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        for line in lines:
            # Look for bullet points, bold headers, or key takeaway lines
            if line.startswith(("-", "*", "•")) or line.startswith(("#", "###", "##")):
                clean = re.sub(r"^[-*•#\s]+", "", line).strip()
                # Skip pure headings or very short snippets
                if len(clean) > 15 and not clean.startswith("http"):
                    facts.append(clean)
            elif any(verb in line.lower() for verb in ["es ", "tiene ", "usa ", "requiere ", "soporta ", "is ", "uses ", "has ", "requires "]):
                if len(line) > 20 and not line.startswith("```"):
                    facts.append(line)

        # Fallback if no bullets: split into sentences
        if not facts:
            sentences = re.split(r'(?<=[.!?]) +', raw_text)
            facts = [s.strip() for s in sentences if len(s.strip()) > 20]

        return facts[:15]  # Cap to top 15 most salient per chunk

    def diff_facts(self, new_facts: List[str], existing_knowledge: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Classifies facts into ADD, UPDATE (contradiction resolved), or NOOP (duplicate).
        Returns a dict with 'add', 'update', 'noop'.
        """
        results = {"add": [], "update": [], "noop": []}

        for nf in new_facts:
            nf_lower = nf.lower()
            nf_words = set(re.findall(r'\w+', nf_lower))

            matched = False
            for ex in existing_knowledge:
                ex_lower = ex.lower()
                ex_words = set(re.findall(r'\w+', ex_lower))

                # Jaccard word similarity
                overlap = len(nf_words & ex_words)
                union = len(nf_words | ex_words)
                ratio = overlap / max(union, 1)

                if ratio > 0.8:
                    # High overlap -> Duplicate
                    results["noop"].append({"fact": nf, "matched_with": ex, "reason": "Exact duplicate"})
                    matched = True
                    break
                elif ratio > 0.45:
                    # Partial overlap: check for negation or conflict markers
                    neg_markers = [" no ", " not ", " deprecated ", " reemplaza ", " obsoleto ", " replaced "]
                    has_conflict = any(m in nf_lower for m in neg_markers) or any(m in ex_lower for m in neg_markers)

                    if has_conflict:
                        results["update"].append({
                            "old_fact": ex,
                            "new_fact": nf,
                            "reason": "Supersedes previous knowledge"
                        })
                    else:
                        results["add"].append({"fact": nf, "context": f"Refines: {ex}"})
                    matched = True
                    break

            if not matched:
                results["add"].append({"fact": nf, "context": "New knowledge"})

        return results
