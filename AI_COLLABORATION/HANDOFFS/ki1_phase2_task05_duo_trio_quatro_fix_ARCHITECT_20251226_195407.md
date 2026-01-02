---
status: COMPLETE
task: phase2_task05_duo_trio_quatro_fix
role: ARCHITECT
phase: ARCHITECT
files_changed: []
summary:
  - Bug identified in V9:130-135: exclusive elif loses sub-combinations
  - 4-match only extracts quatro (loses 4 trios + 6 duos)
  - 3-match only extracts trio (loses 3 duos)
  - Fix: Use parallel if statements instead of exclusive elif
  - Create kenobase/analysis/pattern.py with PatternResult dataclass
  - Integrate with existing frequency.py module structure
  - Add comprehensive unit tests in tests/unit/test_pattern.py
  - Update analysis/__init__.py exports
---

# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): UNVERIFIED (no git repo, no SYSTEM_STATUS.json)
- Rule 2 (granularity stated): per-combination
- Rule 3 (semantics defined): duo=(2-tuple), trio=(3-tuple), quatro=(4-tuple) of matching numbers
- Rule 4 (target metric): correctness (all sub-patterns extracted)
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): `pytest tests/unit/test_pattern.py -v` -> PASS or UNVERIFIED

## Task Setup
- Granularity: per-combination (analyze overlap between 6er-Kombi and draw)
- Semantics: Extract ALL sub-patterns from match overlap (not exclusive)
- Target metric: correctness - 4-match must yield 1 quatro + 4 trios + 6 duos

## Repro Commands
- `pytest tests/unit/test_pattern.py -v` -> PASS expected after implementation

## Deliverable
Handoff written to: `AI_COLLABORATION/HANDOFFS/ki1_phase2_task05_duo_trio_quatro_fix_ARCHITECT_20251226_195407.md`

## WORKING_SET_REQUEST for EXECUTOR
- kenobase/analysis/frequency.py
- kenobase/analysis/__init__.py
- kenobase/core/data_loader.py
- tests/unit/test_frequency.py
- tests/conftest.py
- all_code/00_0_Keno_6-Kombi_Analyse_V9.py
