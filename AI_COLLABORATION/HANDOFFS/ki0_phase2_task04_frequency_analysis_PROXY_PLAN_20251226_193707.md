---
status: APPROVED
task: phase2_task04_frequency_analysis
role: PROXY
phase: PROXY_PLAN
reviewed_handoff: "ki1_phase2_task04_frequency_analysis_ARCHITECT_20251226_193406.md"
summary:
  - Plan vollstaendig mit 6 Funktionen und 2 Dataklassen
  - Integration mit DrawResult aus data_loader.py verifiziert
  - Config-Thresholds in default.yaml vorhanden (min: 0.05, max: 0.20, windows)
  - kenobase/analysis/__init__.py existiert und ist bereit fuer Exports
  - 10+ Tests spezifiziert mit 80% Coverage-Ziel
  - Keine RED FLAGS erkannt - keine globalen Werte wo team-spezifische noetig
  - Granularitaet per-number ist korrekt fuer Haeufigkeitsanalyse
  - Risiken angemessen dokumentiert (leere Listen, Division by Zero)
---
# Rule Confirmation
- Rule 1 (SYSTEM_STATUS + ADR/Docs + git status): UNVERIFIED (SYSTEM_STATUS.json existiert nicht, kein Git-Repo)
- Rule 2 (granularity stated): per-number (global frequency across all draws)
- Rule 3 (semantics defined): frequency = occurrences/total_draws, hot/cold/normal classification
- Rule 4 (target metric): frequency distribution for number selection
- Rule 5 (helper-only boundaries): CONFIRMED
- Rule 6 (reproducibility): pytest tests/unit/test_frequency.py -v -> console output

## Task Setup
- Granularity: per-number (individuelle Zahlenfrequenz in allen Ziehungen)
- Semantics:
  - absolute_frequency: Anzahl Vorkommen
  - relative_frequency: count / total_draws (0.0 - 1.0)
  - hot_numbers: frequency > 0.20 (max_frequency_threshold)
  - cold_numbers: frequency < 0.05 (min_frequency_threshold)
  - rolling_frequency: Frequenz ueber konfigurierbares Fenster
- Target metric: Akkurate Frequenzzaehlung fuer downstream Pattern-Analyse

## Repro Commands
- pytest tests/unit/test_frequency.py -v -> console output
- pytest tests/unit/test_frequency.py --cov=kenobase.analysis.frequency -> coverage report

# Proxy Review

## Verifizierte Dateien

1. **kenobase/core/data_loader.py** (existiert)
   - DrawResult.numbers: list[int] (Zeile 55) - perfekt fuer Frequenzanalyse
   - GameType enum vorhanden (Zeile 34-40)
   - Saubere Pydantic-Modelle

2. **config/default.yaml** (existiert)
   - min_frequency_threshold: 0.05 (Zeile 51)
   - max_frequency_threshold: 0.20 (Zeile 52)
   - windows: [5, 10, 20, 50] (Zeile 69)
   - Alle im Plan referenzierten Config-Werte vorhanden

3. **kenobase/analysis/__init__.py** (existiert)
   - Aktuell leer, bereit fuer Exports
   - Plan spezifiziert korrekte Export-Liste

## Architektur-Check

- KEIN BUG-001: Frequenz-Thresholds sind hier korrekt global
  - Zahlenverteilung ist spieltyp-uebergreifend (KENO 1-70, Lotto 1-49 etc.)
  - Threshold 0.05/0.20 sind relative Werte, nicht absolute
  
- KEIN BUG-003: Kein Orchestrator involviert
  - Reines Analyse-Modul ohne Pipeline-Abhaengigkeit
  
- Integration Points vollstaendig:
  - data_loader.py: DrawResult (READ-ONLY)
  - default.yaml: Config-Werte (READ-ONLY)
  - __init__.py: Exports hinzufuegen

## Risiko-Bewertung

| Risiko | Bewertung | Mitigation im Plan |
|--------|-----------|-------------------|
| Leere Draws-Liste | LOW | Explizite Pruefung dokumentiert |
| Division by Zero | LOW | Guard dokumentiert |
| Ungueltige number_range | LOW | Validierung dokumentiert |
| Performance | LOW | Counter ist O(n), akzeptabel |

## Entscheidung

**APPROVED** - Plan ist mechanisch vollstaendig, architektonisch konsistent, und integriert sauber mit existierenden Modulen. Keine RED FLAGS erkannt.

## WORKING_SET fuer EXECUTOR

WORKING_SET:
- kenobase/analysis/__init__.py (MODIFY)
- kenobase/analysis/frequency.py (CREATE)
- tests/unit/test_frequency.py (CREATE)
- config/default.yaml (READ-ONLY)
- kenobase/core/data_loader.py (READ-ONLY)
