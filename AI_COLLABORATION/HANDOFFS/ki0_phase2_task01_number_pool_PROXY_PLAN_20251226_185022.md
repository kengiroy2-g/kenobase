---
status: APPROVED
task: phase2_task01_number_pool
role: PROXY
phase: PROXY_PLAN
reviewed_handoff: "ki1_phase2_task01_number_pool_ARCHITECT_20251226_184522.md"
summary:
  - Legacy function generiere_zahlenpool_optimiert() correctly identified at V9:45-85
  - Plan correctly proposes NumberPoolGenerator class with 4 public methods
  - Integration with existing DataLoader (DrawResult, list[int] numbers) is coherent
  - AnalysisConfig already has windows=[5,10,20,50] for period sizing - plan should use this
  - __init__.py exports need updating (currently only config + data_loader)
  - Algorithm migration: 3 periods x 10 draws, Top-11, intersections - well understood
  - Test coverage plan (8 cases) is adequate for MVP
  - No BUG-001/003 violations detected (module is per-game, no global thresholds)
---

# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED
- Rule 2 (granularity stated): per-game
- Rule 3 (semantics defined): NumberPool = set[int], DrawResult.numbers = list[int]
- Rule 4 (target metric): pool-quality
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): pytest tests/unit/test_number_pool.py -v

**Handoff-Datei erstellt:** `AI_COLLABORATION/HANDOFFS/ki0_phase2_task01_number_pool_PROXY_PLAN_20251226_185022.md`
