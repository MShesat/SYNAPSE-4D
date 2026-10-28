"""
Synapse 4D - Dimension 2: Fact Distiller (D2)
Atomic fact extraction, deterministic truth hierarchy, and semantic conflict arbitration.
"""

import re
from typing import List, Dict, Any, Tuple

class FactDistiller:
    """Dimension 2: Distills raw unstructured experiences into verified atomic declarative facts."""

    def __init__(self):
        # Authority Levels: 1=Axiom/Rule, 2=Preference, 3=Observation
        self.hierarchy_weights = {
            "axiom": 1.0,
            "preference": 0.8,
            "observation": 0.5
        }

    def distill_atomic_facts(self, raw_text: str) -> List[Dict[str, Any]]:
        """Extracts atomic declarative statements with classified epistemic authority."""
        extracted = []
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

        for line in lines:
            if line.startswith(("-", "*", "•")) or line.startswith(("#", "###", "##")):
                clean = re.sub(r"^[-*•#\s]+", "", line).strip()
                if len(clean) > 15 and not clean.startswith("http"):
                    authority = "observation"
                    if any(k in clean.lower() for k in ["regla", "ley", "rule", "mandatory", "prohibido"]):
                        authority = "axiom"
                    elif any(k in clean.lower() for k in ["prefiere", "preference", "default", "siempre"]):
                        authority = "preference"

                    extracted.append({
                        "statement": clean,
                        "authority": authority,
                        "weight": self.hierarchy_weights[authority]
                    })
            elif any(verb in line.lower() for verb in ["es ", "tiene ", "usa ", "requiere ", "soporta ", "is ", "uses ", "has "]):
                if len(line) > 20 and not line.startswith("```"):
                    extracted.append({
                        "statement": line,
                        "authority": "observation",
                        "weight": 0.5
                    })

        return extracted[:20]

    def arbitrate_conflicts(self, incoming_facts: List[Dict[str, Any]], existing_facts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Arbitrates semantic conflicts using the Truth Hierarchy.
        Higher authority facts supersede lower authority facts.
        """
        results = {"retained": [], "superseded": [], "redundant": []}

        for incoming in incoming_facts:
            in_stmt = incoming["statement"].lower()
            in_words = set(re.findall(r'\w+', in_stmt))
            matched = False

            for existing in existing_facts:
                ex_stmt = existing["statement"].lower()
                ex_words = set(re.findall(r'\w+', ex_stmt))

                overlap = len(in_words & ex_words)
                union = len(in_words | ex_words)
                ratio = overlap / max(union, 1)

                if ratio > 0.8:
                    results["redundant"].append({
                        "fact": incoming["statement"],
                        "matches": existing["statement"]
                    })
                    matched = True
                    break
                elif ratio > 0.45:
                    # Semantic conflict detected: evaluate authority
                    if incoming["weight"] >= existing["weight"]:
                        results["superseded"].append({
                            "old_fact": existing["statement"],
                            "new_fact": incoming["statement"],
                            "reason": f"New fact ({incoming['authority']}) supersedes old ({existing['authority']})"
                        })
                    else:
                        results["redundant"].append({
                            "fact": incoming["statement"],
                            "reason": f"Rejected: Existing axiom ({existing['authority']}) has higher authority"
                        })
                    matched = True
                    break

            if not matched:
                results["retained"].append(incoming)

        return results
