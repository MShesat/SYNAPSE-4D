# ADR-002: Esquema Relacional SQLite D3, Concurrencia WAL y Decaimiento Lazy

- **Estado:** Aceptado e Implementado
- **Fecha:** 2026-10-28
- **Contexto:**
  La persistencia anterior en archivos monolíticos JSON (`chronos_lattice.json`) provocaba bloqueos de escritura $O(N)$, riesgo de corrupción ante múltiples procesos simultáneos (CLI, MCP, plugins) y amplificación de escrituras por decaimiento hebbiano artificial.

- **Decisión:**
  1. **SQLite en modo WAL (`synapse_state.db`):**
     - `PRAGMA journal_mode = WAL;`, `busy_timeout = 5000;`, `foreign_keys = ON;`.
     - Bloqueo entre procesos mediante `filelock.FileLock` en `.synapse/synapse.lock`.
  2. **Esquema Relacional Bi-temporal:**
     - `consolidation_sessions`: registro histórico de sesiones con status (`pending`, `committed`, `rolled_back`).
     - `facts`: soporte bi-temporal con `valid_from`, `valid_to`, `invalidated_at`, `superseded_by`, bandera de revisión `needs_review` y blob de embedding vector.
     - `edges`: grafo asociativo con `base_weight`, `last_retrieved_epoch` y `last_modified_session`.
     - `stub_references`: catálogo de entidades creadas como stubs mínimos para trazabilidad de rollback.
  3. **Decaimiento Hebbiano Lazy vía UDF SQLite:**
     - En lugar de reescribir la base de datos periódicamente, se registra la UDF `eff_weight(base_weight, last_epoch, now_epoch, half_life)`.
     - Complejidad de escritura del decaimiento: $O(0)$. El peso efectivo se evalúa al vuelo en tiempo de consulta.
  4. **Separación Open-Core:**
     - `dashboard.py` extraído del repositorio público MIT y reservado exclusivamente para el paquete comercial Pro Edition.

- **Consecuencias y Validación:**
  - 100% de tests unitarios aprobados en `tests/test_storage.py`.
  - Operaciones de lectura y escritura concurrentes sin corrupción de datos.
