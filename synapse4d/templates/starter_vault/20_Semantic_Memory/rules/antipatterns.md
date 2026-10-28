---
title: "Universal Antipatterns Catalog"
type: rules
---

# Universal Antipatterns Catalog

## Cognitive & Architectural Antipatterns

### Anti-PARA Dilution
- Context: Traditional PARA folders mixing working drafts with immutable rules.
- Issue: Attention dilution and LLM hallucination across expired session logs.
- Fix: Segregate into CoALA layers (00_Working, 10_Episodic, 20_Semantic).
