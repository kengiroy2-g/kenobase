---
status: APPROVED
task: data_migration_eurojackpot
role: PROXY
phase: PROXY_PLAN
reviewed_handoff: "ki1_data_migration_eurojackpot_ARCHITECT_20251227_012231.md"
summary:
  - ARCHITECT correctly identified column order mismatch in bereinigt format
  - Source: Keno_GPTs/eurojackpot_archiv_bereinigt.csv (N=527 rows)
  - Bereinigt format: S1,S2=EuroZahlen (cols 1-2), z1-z5=Hauptzahlen (cols 3-7)
  - DataLoader expects inverted order (main first, euro last)
  - Fix requires: copy file + fix parser column mapping
  - No red flags (BUG-001/003 not applicable)
  - Test fixture uses different format - both must work after fix
  - Risk: LOW (additive change, reversible)
---

# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): UNVERIFIED (no git repo)
- Rule 2 (granularity stated): per-game
- Rule 3 (semantics defined): Datum;S1;S2;z1-z5
- Rule 4 (target metric): data-integrity (527 rows)
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): `wc -l` -> 528 lines

## Repro Commands
- `wc -l Keno_GPTs/eurojackpot_archiv_bereinigt.csv` -> 528 (verified)
- Post-fix: `python -c "from kenobase.core.data_loader import DataLoader; dl=DataLoader(); r=dl.load('data/raw/eurojackpot/eurojackpot_archiv_bereinigt.csv'); print(len(r))"`

# Proxy Review

**Handoff file created:** `AI_COLLABORATION/HANDOFFS/ki0_data_migration_eurojackpot_PROXY_PLAN_20251227_012431.md`

**Executor can proceed.** Key instructions:
1. Create `data/raw/eurojackpot/` directory
2. Copy source file to target location
3. Fix `_parse_eurojackpot()` to detect bereinigt format via header check for `S1;S2`
4. When bereinigt: cols 1-2 = bonus, cols 3-7 = numbers
5. Verify 527 draws load without errors
