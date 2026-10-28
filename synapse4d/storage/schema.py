"""
Pydantic Schemas and API Contract v2.0 for Synapse 4D.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FactRecord(BaseModel):
    id: str
    entity: str
    attribute: str
    value: str
    status: str = "active"  # active, superseded, provisional, rolled_back
    confidence: float = 1.0
    session_id: str
    valid_from: str
    valid_to: Optional[str] = None
    invalidated_at: Optional[str] = None
    superseded_by: Optional[str] = None
    needs_review: int = 0
    embedding: Optional[List[float]] = None


class EdgeRecord(BaseModel):
    source_entity: str
    target_entity: str
    relation: str = "relacionado_con"
    base_weight: float = 1.0
    last_retrieved_epoch: float
    session_id: str
    last_modified_session: str
    status: str = "active"  # active, rolled_back


class ConsolidationSession(BaseModel):
    session_id: str
    started_at: str
    finished_at: Optional[str] = None
    status: str = "pending"  # pending, committed, rolled_back
    strategy: str = "standard"
    facts_extracted: int = 0
    facts_superseded: int = 0
    health_score: float = 1.0


class StateResponse(BaseModel):
    api_version: str = "2.0"
    vault_name: str
    health_score: float = 1.0
    broken_bindings: int = 0
    needs_review_count: int = 0
    last_consolidation_id: Optional[str] = None
    tiers: Dict[str, Any] = Field(default_factory=dict)
    active_facts_count: int = 0
    total_edges_count: int = 0
