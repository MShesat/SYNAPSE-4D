"""
SQLite Relational Storage Engine for Synapse 4D (Dimension 3 Chronos & Storage).

Features:
- WAL mode, busy_timeout=5000, foreign_keys=ON.
- Process-level locking with filelock (.synapse/synapse.lock).
- Custom SQLite UDF for zero-write-amplification lazy Hebbian decay.
- Bi-temporal facts and audit logs for time-travel debugging.
"""

from __future__ import annotations
import os
import json
import time
import sqlite3
import struct
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from filelock import FileLock

from .schema import FactRecord, EdgeRecord, ConsolidationSession, StateResponse

DEFAULT_HALF_LIFE_SECONDS = 7 * 86400.0  # 7 days half-life


def eff_weight_udf(base_weight: float, last_epoch: float, now_epoch: float, half_life: float = DEFAULT_HALF_LIFE_SECONDS) -> float:
    """SQLite UDF: Compute lazy Hebbian decayed weight at query time."""
    try:
        if not base_weight:
            return 0.0
        bw = float(base_weight)
        le = float(last_epoch) if last_epoch else now_epoch
        ne = float(now_epoch)
        hl = float(half_life) if half_life and half_life > 0 else DEFAULT_HALF_LIFE_SECONDS
        dt = max(0.0, ne - le)
        return bw * (2.0 ** (-dt / hl))
    except Exception:
        return float(base_weight or 0.0)


def serialize_embedding(vec: Optional[List[float]]) -> Optional[bytes]:
    """Pack float array into binary blob for SQLite storage."""
    if not vec:
        return None
    return struct.pack(f"{len(vec)}f", *vec)


def deserialize_embedding(blob: Optional[bytes]) -> Optional[List[float]]:
    """Unpack binary blob into float list."""
    if not blob:
        return None
    num_floats = len(blob) // 4
    return list(struct.unpack(f"{num_floats}f", blob))


class SynapseDatabase:
    def __init__(self, vault_path: Path | str):
        self.vault_path = Path(vault_path)
        self.synapse_dir = self.vault_path / ".synapse"
        self.synapse_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.synapse_dir / "synapse_state.db"
        self.lock_path = self.synapse_dir / "synapse.lock"
        self._lock = FileLock(str(self.lock_path), timeout=10.0)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a SQLite connection with WAL and custom UDFs."""
        conn = sqlite3.connect(str(self.db_path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.create_function("eff_weight", 3, lambda bw, le, ne: eff_weight_udf(bw, le, ne))
        conn.create_function("eff_weight", 4, eff_weight_udf)
        return conn

    def _init_db(self):
        """Initialize database schema with idempotent tables and indexes."""
        with self._lock:
            with self.get_connection() as conn:
                conn.executescript("""
                CREATE TABLE IF NOT EXISTS consolidation_sessions (
                    session_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL DEFAULT 'pending', -- pending, committed, rolled_back
                    strategy TEXT DEFAULT 'standard',
                    facts_extracted INTEGER DEFAULT 0,
                    facts_superseded INTEGER DEFAULT 0,
                    health_score REAL DEFAULT 1.0
                );

                CREATE TABLE IF NOT EXISTS facts (
                    id TEXT PRIMARY KEY,
                    entity TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    value TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active', -- active, superseded, provisional, rolled_back
                    confidence REAL DEFAULT 1.0,
                    session_id TEXT NOT NULL,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT,
                    invalidated_at TEXT,
                    superseded_by TEXT,
                    needs_review INTEGER NOT NULL DEFAULT 0,
                    embedding BLOB,
                    FOREIGN KEY(session_id) REFERENCES consolidation_sessions(session_id)
                );

                CREATE INDEX IF NOT EXISTS idx_facts_entity_status ON facts(entity, status);
                CREATE INDEX IF NOT EXISTS idx_facts_session ON facts(session_id);
                CREATE INDEX IF NOT EXISTS idx_facts_needs_review ON facts(needs_review) WHERE needs_review = 1;

                CREATE TABLE IF NOT EXISTS edges (
                    source_entity TEXT NOT NULL,
                    target_entity TEXT NOT NULL,
                    relation TEXT NOT NULL DEFAULT 'relacionado_con',
                    base_weight REAL NOT NULL DEFAULT 1.0,
                    last_retrieved_epoch REAL NOT NULL,
                    session_id TEXT NOT NULL,
                    last_modified_session TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active', -- active, rolled_back
                    PRIMARY KEY(source_entity, target_entity, relation)
                );

                CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_entity);
                CREATE INDEX IF NOT EXISTS idx_edges_last_mod ON edges(last_modified_session);

                CREATE TABLE IF NOT EXISTS stub_references (
                    stub_path TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    source_file TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY(stub_path, session_id)
                );
                """)
                conn.commit()

    # --- SESSION MANAGEMENT ---
    def begin_session(self, session_id: str, strategy: str = "standard") -> ConsolidationSession:
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO consolidation_sessions (session_id, started_at, status, strategy) VALUES (?, ?, 'pending', ?)",
                    (session_id, now_iso, strategy),
                )
                conn.commit()
        return ConsolidationSession(session_id=session_id, started_at=now_iso, status="pending", strategy=strategy)

    def commit_session(self, session_id: str, facts_extracted: int, facts_superseded: int, health_score: float = 1.0):
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    UPDATE consolidation_sessions 
                    SET status = 'committed', finished_at = ?, facts_extracted = ?, facts_superseded = ?, health_score = ?
                    WHERE session_id = ?
                    """,
                    (now_iso, facts_extracted, facts_superseded, health_score, session_id),
                )
                conn.commit()

    def get_session(self, session_id: str) -> Optional[ConsolidationSession]:
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM consolidation_sessions WHERE session_id = ?", (session_id,)).fetchone()
            if not row:
                return None
            return ConsolidationSession(**dict(row))

    # --- FACTS API ---
    def add_fact(self, fact: FactRecord):
        blob = serialize_embedding(fact.embedding)
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO facts (
                        id, entity, attribute, value, status, confidence, 
                        session_id, valid_from, valid_to, invalidated_at, 
                        superseded_by, needs_review, embedding
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        fact.id, fact.entity, fact.attribute, fact.value, fact.status,
                        fact.confidence, fact.session_id, fact.valid_from, fact.valid_to,
                        fact.invalidated_at, fact.superseded_by, fact.needs_review, blob
                    ),
                )
                conn.commit()

    def supersede_fact(self, old_fact_id: str, new_fact_id: str, invalidated_at_session: str):
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    UPDATE facts 
                    SET status = 'superseded', superseded_by = ?, invalidated_at = ?, valid_to = ?
                    WHERE id = ? AND status = 'active'
                    """,
                    (new_fact_id, invalidated_at_session, now_iso, old_fact_id),
                )
                conn.commit()

    def get_active_facts(self, entity: Optional[str] = None) -> List[FactRecord]:
        with self.get_connection() as conn:
            if entity:
                cursor = conn.execute("SELECT * FROM facts WHERE entity = ? AND status = 'active'", (entity,))
            else:
                cursor = conn.execute("SELECT * FROM facts WHERE status = 'active'")
            records = []
            for r in cursor.fetchall():
                d = dict(r)
                d["embedding"] = deserialize_embedding(d.pop("embedding", None))
                records.append(FactRecord(**d))
            return records

    def get_needs_review_facts(self) -> List[FactRecord]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM facts WHERE needs_review = 1 AND status IN ('active', 'provisional')")
            records = []
            for r in cursor.fetchall():
                d = dict(r)
                d["embedding"] = deserialize_embedding(d.pop("embedding", None))
                records.append(FactRecord(**d))
            return records

    # --- EDGES API ---
    def upsert_edge(
        self,
        source: str,
        target: str,
        relation: str = "relacionado_con",
        weight_delta: float = 0.5,
        session_id: str = "init",
    ):
        now_epoch = time.time()
        with self._lock:
            with self.get_connection() as conn:
                row = conn.execute(
                    "SELECT base_weight, last_retrieved_epoch FROM edges WHERE source_entity = ? AND target_entity = ? AND relation = ?",
                    (source, target, relation),
                ).fetchone()

                if row:
                    # Update with Hebbian reinforcement
                    old_base = row["base_weight"]
                    old_epoch = row["last_retrieved_epoch"]
                    eff_w = eff_weight_udf(old_base, old_epoch, now_epoch)
                    new_base = min(10.0, eff_w + weight_delta)
                    conn.execute(
                        """
                        UPDATE edges 
                        SET base_weight = ?, last_retrieved_epoch = ?, last_modified_session = ?, status = 'active'
                        WHERE source_entity = ? AND target_entity = ? AND relation = ?
                        """,
                        (new_base, now_epoch, session_id, source, target, relation),
                    )
                else:
                    # Insert new edge
                    conn.execute(
                        """
                        INSERT INTO edges (source_entity, target_entity, relation, base_weight, last_retrieved_epoch, session_id, last_modified_session, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                        """,
                        (source, target, relation, max(1.0, weight_delta), now_epoch, session_id, session_id),
                    )
                conn.commit()

    def get_active_edges(self) -> List[EdgeRecord]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM edges WHERE status = 'active'")
            return [EdgeRecord(**dict(r)) for r in cursor.fetchall()]

    # --- STUB REFERENCES ---
    def record_stub_reference(self, stub_path: str, session_id: str, source_file: str):
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO stub_references (stub_path, session_id, source_file, created_at) VALUES (?, ?, ?, ?)",
                    (stub_path, session_id, source_file, now_iso),
                )
                conn.commit()

    def get_stubs_by_session(self, session_id: str) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT stub_path FROM stub_references WHERE session_id = ?", (session_id,))
            return [row["stub_path"] for row in cursor.fetchall()]

    # --- STATE & HEALTH CONTRACT ---
    def get_state_summary(self) -> StateResponse:
        with self.get_connection() as conn:
            facts_count = conn.execute("SELECT COUNT(*) FROM facts WHERE status = 'active'").fetchone()[0]
            needs_review_count = conn.execute("SELECT COUNT(*) FROM facts WHERE needs_review = 1 AND status IN ('active', 'provisional')").fetchone()[0]
            edges_count = conn.execute("SELECT COUNT(*) FROM edges WHERE status = 'active'").fetchone()[0]
            last_sess = conn.execute("SELECT session_id, health_score FROM consolidation_sessions WHERE status = 'committed' ORDER BY started_at DESC LIMIT 1").fetchone()
            
            last_id = last_sess["session_id"] if last_sess else None
            h_score = last_sess["health_score"] if last_sess else 1.0

            tiers = {
                "working_memory": {"status": "healthy"},
                "episodic_memory": {"status": "healthy"},
                "semantic_memory": {"facts_active": facts_count, "needs_review": needs_review_count},
                "associative_mesh": {"edges_active": edges_count},
            }

            return StateResponse(
                api_version="2.0",
                vault_name=self.vault_path.name,
                health_score=h_score,
                broken_bindings=0,
                needs_review_count=needs_review_count,
                last_consolidation_id=last_id,
                tiers=tiers,
                active_facts_count=facts_count,
                total_edges_count=edges_count,
            )


_DB_REGISTRY: Dict[str, SynapseDatabase] = {}


def get_database(vault_path: Path | str) -> SynapseDatabase:
    """Singleton-per-vault helper."""
    key = str(Path(vault_path).resolve())
    if key not in _DB_REGISTRY:
        _DB_REGISTRY[key] = SynapseDatabase(vault_path)
    return _DB_REGISTRY[key]
