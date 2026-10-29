# Changelog

Todas las modificaciones notables en el proyecto **Synapse 4D** estarán documentadas en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-10-28

### Added
- **Persistencia Relacional SQLite WAL:** Implementación del motor de almacenamiento transaccional `SynapseDatabase` (`.synapse/synapse_state.db`) operando en modo Write-Ahead Logging (`WAL`), `busy_timeout=5000` y control de concurrencia inter-proceso mediante `FileLock`.
- **Decaimiento Hebbiano Lazy en UDF:** Función definida por el usuario (`eff_weight_udf`) integrada en SQLite para evaluar pesos dinámicos en tiempo de consulta con cero amplificación de escritura en disco.
- **Modelo Epistémico Bi-Temporal:** Hechos atómicos auditables con campos temporales explícitos (`valid_from`, `valid_to`, `invalidated_at`, `superseded_by`), permitiendo auditorías de viaje en el tiempo y preservación de historia.
- **Journal Atómico de Dos Fases (2PC):** Módulo `AtomicJournal` con fases de preparación y confirmación (`prepare` / `commit`) y reconciliación determinista en arranque (`reconcile_on_startup`) para total resiliencia ante caídas forzadas (`SIGKILL`).
- **Motor de Embeddings ONNX Local:** Sustitución de dependencias pesadas por inferencia local en CPU con `fastembed` (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones) y empaquetado binario `BLOB` ultrarrápido.
- **Motor Híbrido de Polaridad y Antónimos:** Filtro léxico-sintáctico de negaciones y antónimos canónicos simétricos (ES/EN) para neutralizar el *cosine pitfall* en contradicciones lógicas.
- **Comando y Flujo de Reversión (`undo`):** Capacidad para revertir sesiones de consolidación completas de forma determinista, restableciendo hechos obsoletos y depurando registros inválidos.
- **Revisión Epistémica Supervisada (`review`):** Marcado proactivo de hechos extraídos heurísticamente (`needs_review=1`) y consulta selectiva para validación humana o por modelo supervisor.
- **Migración Automática de Bóvedas (`migrate`):** Comando CLI y rutina de migración para convertir estructuras y archivos v1.x hacia la base de datos relacional v2.0 preservando integridad referencial.
- **Servidor Nativo MCP (Model Context Protocol v2.5):** Exposición de 6 herramientas (`synapse_get_working_memory`, `synapse_search_memory`, `synapse_consolidate`, `synapse_audit_vault`, `synapse_undo_session`, `synapse_review_facts`) sobre stdio JSON-RPC 2.0 para Claude Desktop, Cursor y Antigravity.
- **Dataset de Referencia Calibrado (`golden_pairs_v2.jsonl`):** 100 pares bilingües balanceados con certificación estadística por remuestreo Bootstrap (IC 95%) y scripts de análisis de latencia en percentiles SLA.

### Changed
- **`dashboard.py` retirado de la versión base MIT:** El panel web interactivo ha sido desacoplado del repositorio de código abierto y trasladado a la edición Synapse 4D Pro según la hoja de ruta comercial.
- **Evaluación Hebbiana bajo Demanda:** Desacoplado el decaimiento de procesos periódicos en segundo plano (cron/daemons) hacia evaluación puramente matemática en sentencias SQL.
- **Estructura de Índices y Búsqueda:** Búsqueda híbrida unificada que prioriza concordancia textual exacta en entidades antes de la evaluación de similitud vectorial densa.

### Fixed
- **README y Documentación Honesta:** Eliminadas todas las afirmaciones de latencias teóricas o garantías no demostradas empíricamente de la v1.0, sustituyéndolas por benchmarks auditables con SLA p95 verificados.
- **Corrección del Cosine Pitfall:** Resuelto el falso positivo de redundancia entre frases afirmativas y negativas sobre el mismo sujeto (ej. "usar X" vs "evitar X").
- **Tolerancia a Fallos e Interrupciones:** Eliminada la corrupción silenciosa en archivos JSON planos ante desconexiones o terminaciones abruptas del proceso.

### Removed
- **`chronos_lattice.json` eliminado:** Retirado definitivamente el archivo monolítico JSON de estado de la v1.0, migrando toda la persistencia a tablas normalizadas en SQLite WAL.

---

## [1.0.0] - 2026-09-15

### Added
- Versión inicial experimental de Synapse 4D con soporte para las 4 dimensiones teóricas.
- Persistencia preliminar en archivo JSON plano (`chronos_lattice.json`).
- Extracción heurística básica de hechos atómicos y generación de enlaces Markdown en bóvedas de Obsidian.
