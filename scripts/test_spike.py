import numpy as np
from chromadb.utils import embedding_functions
from synapse4d.nlp.polarity import (
    detect_polarity,
    has_polar_opposition,
    classify_relation,
)

def main():
    fn = embedding_functions.DefaultEmbeddingFunction()
    
    pairs = [
        # (A, B, expected_type)
        ("usar PostgreSQL para persistencia", "evitar PostgreSQL para persistencia", "conflict"),
        ("usar PostgreSQL para persistencia", "usar base de datos PostgreSQL para almacenamiento persistente", "redundant"),
        ("usar PostgreSQL para persistencia", "el cielo es azul y despejado", "orthogonal"),
        ("enable async synchronization", "disable async synchronization", "conflict"),
        ("hacer backup diario a medianoche", "hacer copia de seguridad diaria por las noches", "redundant"),
        ("permitir acceso root sin contrasena", "prohibir acceso root sin credenciales", "conflict"),
    ]

    print("=== SPIKE EMBEDDINGS & POLARIDAD ===")
    for text_a, text_b, expected in pairs:
        embs = fn([text_a, text_b])
        vec_a, vec_b = np.array(embs[0]), np.array(embs[1])
        sim = float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))
        
        pol_a = detect_polarity(text_a)
        pol_b = detect_polarity(text_b)
        opp = has_polar_opposition(text_a, text_b)
        classification = classify_relation(sim, text_a, text_b)
        
        status = "PASS" if classification == expected else "FAIL"
        print(f"[{status}] A: '{text_a}' vs B: '{text_b}'")
        print(f"       sim={sim:.4f} | pol_A={pol_a:+d} | pol_B={pol_b:+d} | polar_opp={opp} | class={classification} (exp: {expected})\n")

if __name__ == "__main__":
    main()
