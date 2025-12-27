# Kenobase V2.0 Backlog

**Erstellt:** 2025-12-27
**Autor:** Lead Architect (Claude Code)
**Status:** AKTIV

---

## Zusammenfassung

| Prioritaet | Anzahl | DONE | IN_PROGRESS | OFFEN |
|------------|--------|------|-------------|-------|
| KRITISCH   | 0      | 0    | 0           | 0     |
| HOCH       | 2      | 0    | 0           | **2** |
| MITTEL     | 3      | 0    | 0           | **3** |
| NIEDRIG    | 1      | 0    | 0           | **1** |
| **Total**  | **6**  | **0**| **0**       | **6** |

**Letzte Aktualisierung:** 2025-12-27 11:07

---

## Legende

| Status | Bedeutung |
|--------|-----------|
| OFFEN | Issue identifiziert, noch nicht begonnen |
| IN_PROGRESS | Aktiv in Bearbeitung |
| BLOCKED | Wartet auf externe Aktion (User, Daten) |
| DONE | Abgeschlossen und verifiziert |
| WON'T FIX | Bewusst nicht umgesetzt (mit Begruendung) |

---

## HOCH (Direkter Einfluss auf Analyse-Qualitaet)

### ISSUE-001: Automatisierte Daten-Aktualisierung
**Prioritaet:** HOCH
**Status:** OFFEN
**Kategorie:** Data/Infrastructure
**Erstellt:** 2025-12-27

**Problem:**
Aktuell werden Ziehungsdaten manuell aktualisiert. Es gibt keinen automatisierten Mechanismus.

**Aktuelle Situation:**
| Spiel | Letzte Daten | Update-Frequenz | Quelle |
|-------|--------------|-----------------|--------|
| KENO | 2024-xx-xx | Taeglich | lotto-rlp.de |
| EuroJackpot | 2024-xx-xx | Di + Fr | eurojackpot.de |
| Lotto | 2024-xx-xx | Mi + Sa | lotto.de |

**Vorhandene Ressourcen:**
- `Keno_Webscrapping_Code.md` - Selenium-basierter Scraper (nicht integriert)
- `Keno_GPTs/selenium-4.17.2/` - Selenium Package vorhanden

**Loesung:**
1. `scripts/update_data.py` erstellen
2. Scraper fuer alle 3 Spiele implementieren
3. Deduplizierung bei Update
4. Optional: Cron-Job Setup

**Acceptance Criteria:**
- [ ] `python scripts/update_data.py --game keno` aktualisiert KENO-Daten
- [ ] `python scripts/update_data.py --game all` aktualisiert alle Spiele
- [ ] Keine Duplikate nach Update
- [ ] Logging der neuen Eintraege
- [ ] Fehlerbehandlung bei Netzwerk-Problemen

**Betroffene Dateien:**
- `scripts/update_data.py` (NEU)
- `kenobase/scrapers/` (NEU - optional)
- `requirements.txt` (selenium, beautifulsoup4)

**Geschaetzter Aufwand:** 4-6 Stunden

**Abhaengigkeiten:** Keine

---

### ISSUE-002: Spielspezifische Thresholds in Config
**Prioritaet:** HOCH
**Status:** DONE
**Kategorie:** Config/Core
**Erstellt:** 2025-12-27
**Abgeschlossen:** 2025-12-27

**Problem:**
Globale hot/cold Thresholds (0.20/0.05) funktionieren nicht fuer alle Spiele.

**Loesung implementiert:**
- `config/default.yaml`: Spielspezifische Thresholds hinzugefuegt
- `kenobase/core/config.py`: `get_hot_threshold()` und `get_cold_threshold()` Methoden
- `scripts/backtest.py`: Verwendet jetzt spielspezifische Thresholds

**Ergebnis:**
| Spiel | Vorher F1 | Nachher F1 | Verbesserung |
|-------|-----------|------------|--------------|
| KENO | 0.4434 | 0.4434 | (Referenz) |
| EuroJackpot | 0.0043 | 0.1353 | 31x |
| Lotto | 0.0000 | 0.0405 | Hot Numbers erkannt |

---

## MITTEL (Verbesserung der Analyse)

### ISSUE-003: Physics Layer Validation
**Prioritaet:** MITTEL
**Status:** OFFEN
**Kategorie:** Physics/Validation
**Erstellt:** 2025-12-27

**Problem:**
Die Physics-Konzepte (Model Laws A/B/C, Avalanche) sind implementiert, aber nicht systematisch validiert.

**Offene Fragen:**
1. Korreliert Criticality mit tatsaechlichen "schwierigen" Perioden?
2. Ist Law A (Stabilitaet >= 0.9) der richtige Threshold?
3. Hilft Anti-Avalanche wirklich bei der Risikoreduktion?

**Loesung:**
1. Backtest mit Physics-Metriken erweitern
2. Korrelation Criticality vs. F1-Score analysieren
3. A/B-Test: Mit/ohne Avalanche-Filter

**Acceptance Criteria:**
- [ ] Correlation Report: Criticality vs. Prediction Quality
- [ ] Sensitivity Analysis fuer Stability Threshold
- [ ] Dokumentation der Erkenntnisse in ADR-001

**Geschaetzter Aufwand:** 3-4 Stunden

---

### ISSUE-004: Duo/Trio/Quatro Pattern Analysis
**Prioritaet:** MITTEL
**Status:** OFFEN
**Kategorie:** Analysis/Feature
**Erstellt:** 2025-12-27

**Problem:**
Die Pattern-Analyse (Duo/Trio/Quatro) ist aus dem alten Code migriert, aber:
- Potentielle Bugs im alten Code nicht verifiziert
- Keine Validierung ob Patterns vorhersagekraeftig sind

**Loesung:**
1. Pattern-Algorithmus mit bekannten Daten testen
2. Backtest: Vorhersage basierend auf Patterns
3. Feature-Importance berechnen

**Acceptance Criteria:**
- [ ] Unit-Tests fuer Pattern-Erkennung
- [ ] Backtest zeigt Patterns haben Vorhersagekraft (oder nicht)
- [ ] Bug-Fixes dokumentiert

**Geschaetzter Aufwand:** 4-5 Stunden

---

### ISSUE-005: Multi-Game Pipeline Support
**Prioritaet:** MITTEL
**Status:** OFFEN
**Kategorie:** Pipeline/Feature
**Erstellt:** 2025-12-27

**Problem:**
Die Pipeline funktioniert, aber Wechsel zwischen Spielen ist umstaendlich.

**Aktuelle Situation:**
```bash
# Muss active_game in config aendern oder programmatisch setzen
cfg.active_game = "eurojackpot"
```

**Loesung:**
CLI-Parameter `--game` fuer alle Scripts:
```bash
python scripts/analyze.py --game eurojackpot --data data/raw/eurojackpot/...
python scripts/backtest.py --game lotto --data data/raw/lotto/...
```

**Acceptance Criteria:**
- [ ] `--game` Parameter in analyze.py
- [ ] `--game` Parameter in backtest.py
- [ ] Automatische Config-Anpassung basierend auf --game

**Geschaetzter Aufwand:** 2 Stunden

---

## NIEDRIG (Nice-to-Have)

### ISSUE-006: CI/CD Pipeline
**Prioritaet:** NIEDRIG
**Status:** OFFEN
**Kategorie:** Infrastructure/DevOps
**Erstellt:** 2025-12-27

**Problem:**
Keine automatisierte Test-Ausfuehrung bei Commits.

**Loesung:**
GitHub Actions Workflow erstellen:
- Tests bei Push/PR
- Linting (ruff, mypy)
- Coverage Report

**Acceptance Criteria:**
- [ ] `.github/workflows/ci.yml` erstellt
- [ ] Tests laufen automatisch
- [ ] Badge im README

**Geschaetzter Aufwand:** 1-2 Stunden

---

## Abgeschlossene Issues

### ISSUE-002: Spielspezifische Thresholds ✅
**Abgeschlossen:** 2025-12-27
**Details:** Siehe oben

---

## Archiv (WON'T FIX / Deprecated)

(Noch keine Eintraege)

---

## Notizen

### Priorisierungs-Kriterien
1. **KRITISCH:** Blockiert Analyse oder produziert falsche Ergebnisse
2. **HOCH:** Direkter Einfluss auf Analyse-Qualitaet
3. **MITTEL:** Verbesserung der Analyse oder Developer Experience
4. **NIEDRIG:** Nice-to-Have, keine direkten Auswirkungen

### Verwandte Dokumente
- `CLAUDE.md` - Haupt-Dokumentation
- `AI_COLLABORATION/ARCHITECTURE/` - ADRs
- `AI_COLLABORATION/KNOWLEDGE_BASE/` - Guides
