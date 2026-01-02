---
status: REJECTED
task: phase1_task01_project_structure
role: PROXY
phase: PROXY_IMPL
reviewed_handoff: "ki2_phase1_task01_project_structure_EXECUTOR_20251226_170918.md"
summary:
  - VERIFIED: kenobase/ directory exists with correct structure (core, analysis, physics, pipeline)
  - VERIFIED: All 8 __init__.py files present and syntactically valid
  - VERIFIED: pytest.ini created with correct markers
  - VERIFIED: .gitignore comprehensive (102 lines, data dirs excluded)
  - VERIFIED: config/default.yaml exists and is valid (76 lines)
  - VERIFIED: data/raw|processed|results directories with .gitkeep files
  - BUG FOUND: pyproject.toml has UTF-8 BOM (EF BB BF) - causes TOML parser failure
  - BUG FOUND: src/ directory still exists - should be removed after rename
---

# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): CONFIRMED
- Rule 2 (granularity stated): global (project structure task)
- Rule 3 (semantics defined): N/A (structure task)
- Rule 4 (target metric): N/A (structure task)
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): `xxd pyproject.toml | head -5` -> BOM visible; `ls src/` -> exists

## Task Setup
- Granularity: global
- Semantics: Project structure creation
- Target metric: Acceptance criteria from Ticket #1

## Repro Commands
- `xxd pyproject.toml | head -5` -> Shows BOM bytes: efbb bf
- `python -m pytest tests/ --collect-only` -> ERROR: Invalid statement (at line 1, column 1)
- `ls src/` -> Directory still exists with duplicate structure

# Proxy Review (Implementation)

**REJECTED - Two blocking bugs found:**

1. **BUG-1: UTF-8 BOM in pyproject.toml** (CRITICAL)
   - pytest cannot parse the file, breaking all test infrastructure
   - Fix: Re-create without BOM

2. **BUG-2: src/ directory not removed** (HIGH)
   - Creates ambiguity and potential import conflicts
   - Fix: `rm -rf src/`

**Handoff:** `AI_COLLABORATION/HANDOFFS/ki0_phase1_task01_project_structure_PROXY_IMPL_20251226_171318.md`
