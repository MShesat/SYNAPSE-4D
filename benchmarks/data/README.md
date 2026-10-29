# Golden Pairs Dataset v2.0 (`golden_pairs_v2.jsonl`)

Conjunto de datos de referencia (Ground Truth) calibrado empíricamente para evaluar y certificar la precisión del motor semántico y de polaridad en **Synapse 4D** (Dimensión 2: *Fact Distiller* y reconciliación epistemológica).

---

## 1. Esquema del Formato JSONL

Cada línea del archivo `golden_pairs_v2.jsonl` es un objeto JSON autónomo que define una relación semántica entre dos proposiciones atómicas:

```json
{
  "id": "pair_001",
  "text_a": "usar PostgreSQL para persistencia de datos",
  "text_b": "no usar PostgreSQL para persistencia de datos",
  "expected": "conflict",
  "language": "es",
  "domain": "software"
}
```

### Campos y Especificación de Tipos

| Campo | Tipo | Obligatorio | Valores Permitidos / Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `string` | Sí | Identificador único secuencial con formato `pair_XXX` (de 3 dígitos con ceros a la izquierda). |
| `text_a` | `string` | Sí | Primera proposición o hecho atómico a contrastar. |
| `text_b` | `string` | Sí | Segunda proposición o hecho atómico a contrastar. |
| `expected` | `string` | Sí | Clase de relación esperada: `"conflict"`, `"redundant"` u `"orthogonal"`. |
| `language` | `string` | Sí | Código ISO 639-1 del idioma: `"es"` (Español) o `"en"` (Inglés). |
| `domain` | `string` | Sí | Dominio temático: `"software"`, `"science"`, `"business"` o `"personal"`. |

---

## 2. Taxonomía de Relaciones Epistémicas

El dataset contiene **100 pares** balanceados rigurosamente:

1. **`conflict` (35 pares)**: Colisión semántica directa o contradicción lógica entre proposiciones dirigidas al mismo objeto o directriz. Exige arbitraje epistémico y supersesión bi-temporal en Dimensión 2.
   - **Negación explícita:** Partículas negativas sintácticas (`no`, `never`, `not`, `sin`, `without`, `jamás`).
   - **Negación implícita:** Choque léxico mediante pares de antónimos canónicos (`usar`/`evitar`, `activar`/`desactivar`, `allow`/`deny`, `verdadero`/`falso`, `mandatory`/`forbidden`).
   - **Condicionales contrapuestos:** Cláusulas condicionales con consecuencias opuestas ante el mismo disparador contextual (`"si la latencia supera 200ms, escalar pods"` vs `"si la latencia supera 200ms, no escalar pods"`).

2. **`redundant` (30 pares)**: Paráfrasis o afirmaciones semánticamente equivalentes con idéntica polaridad afirmativa o restrictiva. Son candidatas a consolidación por refuerzo Hebbiano sin supersesión destructiva.
   - Utilizan sinónimos canónicos (`activar`/`habilitar`, `usar`/`utilizar`, `backup`/`copia de seguridad`) o reestructuraciones sintácticas densas.

3. **`orthogonal` (35 pares)**: Hechos complementarios o completamente independientes de dominios dispares. No colisionan ni se sustituyen; deben coexistir simultáneamente en la malla asociativa (Dimensión 4).

### Distribución por Idioma y Dominio

- **Distribución de Idiomas:**
  - Español (`es`): 50 pares (18 conflict, 15 redundant, 17 orthogonal).
  - Inglés (`en`): 50 pares (17 conflict, 15 redundant, 18 orthogonal).
- **Distribución por Dominio:**
  - `software`: Arquitectura, ingeniería de software, DevOps y bases de datos.
  - `science`: Física, biología, química, medicina y metodología experimental.
  - `business`: Finanzas, gestión corporativa, recursos humanos y contratos.
  - `personal`: Salud, hábitos, rutinas diarias y vida cotidiana.

---

## 3. Cómo se Usa

### Calibración y Evaluación Empírica

El conjunto de datos es consumido automáticamente por el script de calibración `scripts/calibrate_embeddings_v2.py`:

```bash
python scripts/calibrate_embeddings_v2.py
```

El flujo de procesamiento:
1. Lee línea a línea `golden_pairs_v2.jsonl`.
2. Genera los vectores densos de `text_a` y `text_b` mediante ONNX Runtime (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones).
3. Calcula la similitud coseno $S_C(\mathbf{a}, \mathbf{b})$.
4. Invoca la función híbrida `classify_relation(sim, text_a, text_b)`.
5. Compara la predicción con el campo `expected` y genera:
   - Matriz de confusión global ($3 \times 3$).
   - Precisión, Recall y F1-Score por clase.
   - Intervalos de confianza al 95% mediante remuestreo Bootstrap (1,000 iteraciones).
6. Si la exactitud global es menor a **0.85** o el F1 de cualquiera de las tres clases es menor a **0.70**, el script finaliza con código de salida `1` (`Exit 1`), bloqueando la certificación en pipelines CI.

---

## 4. Cómo se Amplía el Dataset

Para incorporar nuevos pares al benchmark sin comprometer la validez estadística, se debe seguir el siguiente protocolo:

1. **Equilibrio de Clases:** Toda adición de pares debe mantener proporciones equiparables entre `conflict`, `redundant` y `orthogonal`.
2. **Equilibrio Bilingüe:** Cada par añadido en español (`es`) debe acompañarse de su equivalente temático en inglés (`en`).
3. **Validación de Doble Ciego:** Los pares añadidos deben someterse a revisión independiente de dos anotadores humanos con un índice de concordancia Kappa de Cohen $\kappa \ge 0.80$.
4. **Verificación de Formato y Sintaxis:** Validar que el archivo continúe siendo un JSONL estricto (una línea por objeto, sin saltos de línea internos en las cadenas de texto):
   ```bash
   python -c "import json; [json.loads(line) for line in open('benchmarks/data/golden_pairs_v2.jsonl', encoding='utf-8')]"
   ```
5. **Comprobación de Calibración:** Ejecutar `python scripts/calibrate_embeddings_v2.py` para asegurar que el motor mantenga una precisión superior al umbral crítico del 85%.
