"""
Calibration script for Synapse 4D Embeddings & Polarity Engine.

Validates:
- Direct polar conflicts (cos > 0.50 + polar opposition -> conflict)
- Paraphrases / Redundant facts (cos >= 0.75 + same polarity -> redundant)
- Orthogonal / Unrelated facts (cos < 0.50 -> orthogonal)
- Complementary facts (moderate cos + same polarity -> orthogonal / coexisting)
"""

import sys
import numpy as np
from synapse4d.nlp.embeddings import EmbeddingEngine, compute_similarity
from synapse4d.nlp.polarity import (
    detect_polarity,
    has_polar_opposition,
    classify_relation,
)


def run_calibration():
    engine = EmbeddingEngine.get_instance()
    
    test_suite = [
        # --- POLAR CONFLICTS (Should be 'conflict') ---
        ("usar PostgreSQL para persistencia", "evitar PostgreSQL para persistencia", "conflict"),
        ("enable async synchronization", "disable async synchronization", "conflict"),
        ("permitir acceso root sin contrasena", "prohibir acceso root sin credenciales", "conflict"),
        ("guardar archivos en la nube", "guardar archivos en local", "conflict"),
        ("activar modo depuracion en produccion", "desactivar modo depuracion en produccion", "conflict"),
        ("always validate input schemas", "never validate input schemas", "conflict"),
        ("es obligatorio incluir token jwt", "esta prohibido incluir token jwt", "conflict"),

        # --- REDUNDANCIES / PARAPHRASES (Should be 'redundant') ---
        ("usar PostgreSQL para persistencia", "usar base de datos PostgreSQL para almacenamiento persistente", "redundant"),
        ("activar autenticacion de dos factores", "habilitar autenticacion de dos factores", "redundant"),
        ("hacer backup diario del sistema", "realizar copia de seguridad diaria del sistema", "redundant"),
        ("write unit tests before code", "write unit tests prior to implementation code", "redundant"),
        ("mantener baja latencia en consultas", "asegurar latencia minima en consultas", "redundant"),

        # --- ORTHOGONAL / COMPLEMENTARY (Should be 'orthogonal') ---
        ("usar PostgreSQL para persistencia", "el cielo es azul y despejado", "orthogonal"),
        ("configurar servidor con nginx", "escribir documentacion en markdown", "orthogonal"),
        ("habilitar conexion por websocket", "optimizar algoritmos de ordenamiento", "orthogonal"),
        ("usar Python para scripting", "usar Tailwind para estilos de frontend", "orthogonal"),
    ]

    print("======================================================================")
    print("      SYNAPSE 4D - CALIBRACION EMPIRICA DE EMBEDDINGS Y POLARIDAD     ")
    print("======================================================================")

    passed = 0
    total = len(test_suite)

    for idx, (text_a, text_b, expected) in enumerate(test_suite, start=1):
        vec_a = engine.embed_text(text_a)
        vec_b = engine.embed_text(text_b)
        sim = compute_similarity(vec_a, vec_b)
        
        opp = has_polar_opposition(text_a, text_b)
        pol_a = detect_polarity(text_a)
        pol_b = detect_polarity(text_b)
        pred = classify_relation(sim, text_a, text_b)

        is_ok = (pred == expected)
        if is_ok:
            passed += 1
            status_tag = "[PASS]"
        else:
            status_tag = "[FAIL]"

        print(f"{status_tag} Test {idx:02d}: {expected.upper()} | Pred: {pred.upper()} | sim={sim:.4f} | opp={opp}")
        print(f"       A: '{text_a}' (pol: {pol_a:+d})")
        print(f"       B: '{text_b}' (pol: {pol_b:+d})")
        if not is_ok:
            print(f"       >>> ERROR: Esperado {expected}, obtenido {pred}")
        print("----------------------------------------------------------------------")

    accuracy = (passed / total) * 100
    print(f"\nRESULTADO FINAL: {passed}/{total} tests aprobados ({accuracy:.1f}%)")
    print("======================================================================\n")

    if accuracy < 90.0:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    run_calibration()
