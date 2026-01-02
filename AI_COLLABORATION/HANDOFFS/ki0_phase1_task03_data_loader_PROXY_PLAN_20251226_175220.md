---
status: REJECTED
task: phase1_task03_data_loader
role: PROXY
phase: PROXY_PLAN
reviewed_handoff: "ki1_phase1_task03_data_loader_ARCHITECT_20251226_174920.md"
summary:
  - KENO CSV-Format korrekt analysiert (22 cols, ';', dd.mm.yyyy)
  - EuroJackpot hat 8 Spalten nicht 7: Datum;S1;S2;z1;z2;z3;z4;z5 (Bonus zuerst!)
  - KRITISCH: Lotto-Format komplett falsch! Ist: "ISO-Datum,zahlen-mit-bindestrich"
  - Lotto_archiv_bereinigt.csv nutzt NICHT Semikolon sondern Komma und Bindestriche
  - Plan muss Lotto-Parser komplett ueberarbeiten (Format-Erkennung noetig)
  - Integration mit LegacyConfig prinzipiell korrekt konzipiert
  - Pydantic-basierte Validierung passend zu config.py
  - Working-Set-Request: Lotto-Alternativ-Datei pruefen (s. Daten/Lotto_Archiv_ab-1955.csv)
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): UNVERIFIED (SYSTEM_STATUS.json nicht vorhanden, kein Git-Repo)
- Rule 2 (granularity stated): per-game (KENO/EuroJackpot/Lotto haben unterschiedliche Formate)
- Rule 3 (semantics defined): date, numbers[], bonus[] (standardisierter Output)
- Rule 4 (target metric): data-quality (Schema-Validierung, keine FP/FN auf Datenebene)
- Rule 5 (helper-only boundaries): CONFIRMED (DataLoader ist standalone Modul in kenobase/core/)
- Rule 6 (reproducibility): UNVERIFIED (keine Repro-Commands im Plan)

## Task Setup
- Granularity: per-game (drei unterschiedliche Parser fuer drei Formate)
- Semantics: DataFrame mit Spalten {date: datetime, numbers: list[int], bonus: list[int]}
- Target metric: >80% Coverage, Schema-Validierung ohne Datenverlust

## Repro Commands
- Verifikation der CSV-Formate: Read() auf die drei Basis-Dateien
- Keine Unit-Test-Commands spezifiziert -> UNVERIFIED

# Proxy Review

**Status: REJECTED** - Plan basiert auf falschen Annahmen ueber das Lotto-CSV-Format.

**Kritische Probleme:**
1. Lotto-Format ist `"ISO-Datum,zahlen-mit-bindestrich"` - nicht Semikolon-getrennt mit separaten Spalten
2. EuroJackpot hat 8 Spalten (nicht 7), Bonus-Spalten stehen VOR Zahlen-Spalten

**Handoff erstellt:** `AI_COLLABORATION/HANDOFFS/ki0_phase1_task03_data_loader_PROXY_PLAN_20251226_175220.md`

**Naechste Aktion:** ARCHITECT muss Plan korrigieren mit verifizierter Format-Analyse.
