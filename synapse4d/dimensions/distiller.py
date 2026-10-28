"""
Synapse 4D - Dimension 2: Fact Distiller (D2 v2.5)
Atomic fact extraction, epistemic authority arbitration, and bi-temporal logical supersession.
"""

from __future__ import annotations
import re
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple

from synapse4d.storage.db import SynapseDatabase
from synapse4d.storage.schema import FactRecord
from synapse4d.nlp.embeddings import EmbeddingEngine, compute_similarity
from synapse4d.nlp.polarity import (
    detect_polarity,
    has_polar_opposition,
    classify_relation,
)


class FactDistiller:
    """Dimension 2: Distills raw unstructured experiences into verified atomic declarative facts."""

    def __init__(self, db: Optional[SynapseDatabase] = None):
        self.db = db
        self.embedding_engine = EmbeddingEngine.get_instance()
        # Epistemic Authority: 1=Axiom, 2=Preference, 3=Observation
        self.authority_weights = {
            "axiom": 1.0,
            "preference": 0.8,
            "observation": 0.5,
        }

    def distill_atomic_facts(self, raw_text: str, session_id: str = "default") -> List[FactRecord]:
        """
        Extract atomic facts with fallback morpheme heuristics and epistemic classification.
        Marks facts with needs_review=1 when extracted via local fallback heuristics.
        """
        extracted_facts: List[FactRecord] = []
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        for line in lines:
            if line.startswith(("-", "*", "•")) or line.startswith(("#", "###", "##")):
                clean = re.sub(r"^[-*•#\s]+", "", line).strip()
                if len(clean) > 12 and not clean.startswith("http"):
                    authority = "observation"
                    lower = clean.lower()
                    if any(k in lower for k in ["regla", "ley", "rule", "mandatory", "prohibido", "axiom"]):
                        authority = "axiom"
                    elif any(k in lower for k in ["prefiere", "prefer", "default", "predeterminado", "siempre"]):
                        authority = "preference"

                    # Parse candidate entity and value
                    entity, attr, val = self._parse_entity_attribute_value(clean)
                    fact_id = f"f_{uuid.uuid4().hex[:12]}"
                    vec = self.embedding_engine.embed_text(clean)

                    record = FactRecord(
                        id=fact_id,
                        entity=entity,
                        attribute=attr,
                        value=val,
                        status="active",
                        confidence=self.authority_weights[authority],
                        session_id=session_id,
                        valid_from=now_iso,
                        needs_review=1 if authority != "axiom" else 0,
                        embedding=vec,
                    )
                    extracted_facts.append(record)

            elif any(v in line.lower() for v in [" es ", " usa ", " tiene ", " is ", " uses ", " has ", " requires "]):
                if len(line) > 18 and not line.startswith("```"):
                    entity, attr, val = self._parse_entity_attribute_value(line)
                    fact_id = f"f_{uuid.uuid4().hex[:12]}"
                    vec = self.embedding_engine.embed_text(line)

                    record = FactRecord(
                        id=fact_id,
                        entity=entity,
                        attribute=attr,
                        value=val,
                        status="active",
                        confidence=0.5,
                        session_id=session_id,
                        valid_from=now_iso,
                        needs_review=1,
                        embedding=vec,
                    )
                    extracted_facts.append(record)

        return extracted_facts[:30]

    def _parse_entity_attribute_value(self, statement: str) -> Tuple[str, str, str]:
        """Extract coarse-grained (entity, attribute, value) triple."""
        parts = re.split(r"[:=-]\s*", statement, maxsplit=1)
        if len(parts) == 2 and len(parts[0].split()) <= 4:
            entity = parts[0].strip().lower().replace(" ", "_")
            return entity, "directriz", parts[1].strip()

        words = statement.split()
        if len(words) >= 3:
            entity = words[0].strip().lower().replace(" ", "_")
            return entity, "observacion", statement.strip()

        return "sistema", "general", statement.strip()

    def arbitrate_and_persist(
        self,
        incoming_facts: List[FactRecord],
        db: SynapseDatabase,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Arbitrate incoming facts against existing active facts in SQLite database.
        Persists active facts and executes logical supersession without physical deletion.
        """
        results = {
            "retained": [],
            "superseded": [],
            "redundant": [],
        }

        existing_active = db.get_active_facts()

        for incoming in incoming_facts:
            incoming_text = f"{incoming.entity} {incoming.attribute} {incoming.value}"
            incoming_vec = incoming.embedding or self.embedding_engine.embed_text(incoming_text)
            
            matched = False
            for existing in existing_active:
                existing_text = f"{existing.entity} {existing.attribute} {existing.value}"
                existing_vec = existing.embedding or self.embedding_engine.embed_text(existing_text)

                sim = compute_similarity(incoming_vec, existing_vec)
                rel = classify_relation(sim, incoming_text, existing_text)

                if rel == "redundant":
                    # Same proposition, reinforce / merge without duplicate creation
                    results["redundant"].append({
                        "incoming_id": incoming.id,
                        "matched_id": existing.id,
                        "similarity": sim,
                    })
                    matched = True
                    break

                elif rel == "conflict":
                    # Logical conflict: evaluate epistemic authority
                    # Protected axiom policy: provisional facts cannot supersede axioms
                    if incoming.needs_review == 1 and existing.confidence >= 1.0:
                        results["redundant"].append({
                            "incoming_id": incoming.id,
                            "matched_id": existing.id,
                            "reason": "Rejected: Provisional fact cannot supersede established axiom",
                        })
                        matched = True
                        break

                    if incoming.confidence >= existing.confidence:
                        # Incoming fact supersedes existing fact
                        db.supersede_fact(
                            old_fact_id=existing.id,
                            new_fact_id=incoming.id,
                            invalidated_at_session=session_id,
                        )
                        results["superseded"].append({
                            "old_fact_id": existing.id,
                            "new_fact_id": incoming.id,
                            "reason": f"Authority {incoming.confidence} >= {existing.confidence}",
                        })
                    else:
                        # Existing fact holds higher authority
                        results["redundant"].append({
                            "incoming_id": incoming.id,
                            "matched_id": existing.id,
                            "reason": f"Rejected: Existing authority {existing.confidence} > {incoming.confidence}",
                        })
                    matched = True
                    break

            if not matched:
                # Orthogonal new fact
                db.add_fact(incoming)
                results["retained"].append(incoming.id)
            elif incoming.id in [s["new_fact_id"] for s in results["superseded"]]:
                # If incoming superseded an older fact, it becomes active
                db.add_fact(incoming)
                results["retained"].append(incoming.id)

        return results

    @staticmethod
    def undo_session(db: SynapseDatabase, session_id: str) -> Dict[str, int]:
        """
        Deterministically undo all effects of a consolidation session.
        - Restores facts superseded during this session (only if superseded_by belongs to session).
        - Marks facts inserted in this session as 'rolled_back'.
        - Reverts edge modifications made in this session.
        """
        with db._lock:
            with db.get_connection() as conn:
                # 1. Facts inserted in this session -> rolled_back
                conn.execute(
                    "UPDATE facts SET status = 'rolled_back' WHERE session_id = ?",
                    (session_id,),
                )
                facts_rolled_back = conn.total_changes

                # 2. Restore facts superseded by this session
                # Rule: Only restore if superseded_by points to a fact from this session
                cursor = conn.execute(
                    """
                    SELECT id FROM facts 
                    WHERE invalidated_at = ? AND status = 'superseded'
                    """,
                    (session_id,),
                )
                superseded_ids = [r["id"] for r in cursor.fetchall()]

                for f_id in superseded_ids:
                    conn.execute(
                        "UPDATE facts SET status = 'active', superseded_by = NULL, invalidated_at = NULL, valid_to = NULL WHERE id = ?",
                        (f_id,),
                    )
                facts_restored = len(superseded_ids)

                # 3. Rollback edges modified by this session
                conn.execute(
                    "UPDATE edges SET status = 'rolled_back' WHERE last_modified_session = ?",
                    (session_id,),
                )

                # 4. Mark session as rolled_back
                conn.execute(
                    "UPDATE consolidation_sessions SET status = 'rolled_back' WHERE session_id = ?",
                    (session_id,),
                )
                conn.commit()

        return {
            "facts_rolled_back": facts_rolled_back,
            "facts_restored": facts_restored,
        }
