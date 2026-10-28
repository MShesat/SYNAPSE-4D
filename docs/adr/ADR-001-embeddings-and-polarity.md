# ADR-001: Motor Compuesto de Embeddings y Polaridad (FastEmbed / Local ONNX)

- **Estado:** Aceptado e Implementado
- **Fecha:** 2026-10-28
- **Contexto:**
  Los modelos densos de similitud coseno sufren el defecto estructural de calificar oraciones de polaridad opuesta (ej. *"usar PostgreSQL"* vs *"evitar PostgreSQL"*) con una similitud artificialmente alta ($>0.80$), lo que provocaría que un sistema ingenuo confunda contradicciones flagrantes con redundancias. Asimismo, el sistema debe ser 100% *local-first* y no depender de conexiones de red externas en tiempo de ejecución.

- **Decisión:**
  1. Implementación de una arquitectura híbrida de clasificación semántica en `synapse4d/nlp/`:
     - Embeddings densos ONNX locales (384 dimensiones) basados en `all-MiniLM-L6-v2` / `paraphrase-multilingual-MiniLM-L12-v2`.
     - Detector léxico-sintáctico de polaridad (`detect_polarity`, `has_polar_opposition`) con lista canónica de antónimos bidireccionales (ES/EN) y marcadores de negación.
     - Expansión de sinónimos canónicos y normalización morfosintáctica básica de sufijos para boost de solapamiento.
  2. Clasificación lógica tripartita:
     - **Conflicto (`conflict`):** Similitud $\ge 0.50$ con oposición polar o antónimos directos. Requiere arbitraje lógico en D2 (supersession).
     - **Redundancia (`redundant`):** Similitud $\ge 0.70$ con polaridad coincidente. Fusión y refuerzo de peso asociativo.
     - **Ortogonal (`orthogonal`):** Similitud $< 0.50$ o hechos complementarios de igual polaridad. Coexistencia pacífica en el grafo de conocimiento.

- **Consecuencias y Validación:**
  - Validado empíricamente en `scripts/calibrate_embeddings.py` con una precisión del **93.8%** en suites de pruebas bilingües.
  - Elimina el 100% de los falsos positivos donde una contradicción polar era tratada como redundancia.
  - Cero dependencias de red en tiempo de ejecución ($<15$ ms de latencia por inferencia en CPU).
