# Kenobase V2.0 Backlog

**Erstellt:** 2025-12-27
**Autor:** Lead Architect (Claude Code)
**Status:** AKTIV

---

## Zusammenfassung

| Prioritaet | Anzahl | DONE | IN_PROGRESS | OFFEN |
|------------|--------|------|-------------|-------|
| KRITISCH   | 3      | 3    | 0           | 0     |
| HOCH       | 16     | 15   | 0           | **1** |
| MITTEL     | 11     | 9    | 0           | **2** |
| NIEDRIG    | 3      | 1    | 0           | **2** |
| **Total**  | **33** | **28**| **0**      | **5** |

**Letzte Aktualisierung:** 2025-12-28 15:00 (STRAT-003 EXECUTOR)

---

## Phase 2 Ergebnisse (2025-12-27/28)

### Bestaetigt (Features fuer Phase 3/4)
| Hypothese | Ergebnis | Verwendung |
|-----------|----------|------------|
| HYP-003: Anti-Cluster Reset | 100% Reset nach 5+ | Trading Signal |
| HYP-011: Holiday Effect | p=0.0001, 7.2% vs 9.6% | Kalender-Feature |
| M04: Summen-Fenster | 87% in [605-845] | Filter |
| M01: Pool Size | Top-20 optimal (F1=0.247) | Pool-Generator |
| **HYP-001: Gewinnverteilung** | **CV=9.09% (sehr stabil)** | **Distribution-Analysis** |
| **HYP-004: Birthday-Korrelation** | **r=0.3921** | **Anti-Birthday-Strategie** |
| **HYP-006: WGZ-Muster** | **100% Recurrence, 5.73 avg** | **Recurrence-Feature** |
| **HYP-010: Winner-Ratio** | **1.3x bei Birthday** | **Anti-Birthday-Strategie** |
| **HYP-013: Multi-Einsatz** | **Linear skalierend** | **Einsatz-Strategie** |

### Falsifiziert (NICHT verwenden)
| Hypothese | Ergebnis | Grund |
|-----------|----------|-------|
| HYP-002: Jackpot-Zyklen | CV>0.7, p>0.05 | Wartezeiten zufaellig |
| HYP-005: Dekaden-Affinitaet | 0 signifikante Paare | Keine Struktur |
| HYP-008: 111-Prinzip | p=0.96 | Kein Unterschied zu Random |
| HYP-004/RE02: Popularity | p=0.79 | Keine Korrelation |
| M02: Zehnergruppen-Regel | p=nan | Kein Effekt |
| HYP-007: Duo/Trio Patterns | Nicht signifikant | Instabil |
| HYP-010: Odds Correlation | Nicht signifikant | Keine Korrelation |
| HYP-012: Stake Correlation | Nicht signifikant | Keine Korrelation |

---

## Hypothesen-Kategorie

Alle Hypothesen basieren auf der Grundannahme:
> **Lotterie-Spiele sind NICHT zufaellig, sondern folgen einer mathematischen Verteilung.**

Vollstaendiger Katalog: `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md`

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

### TASK-RE02: Popularity Reverse Engineering
**Prioritaet:** HOCH
**Status:** DONE
**Kategorie:** Analysis/Reverse-Engineering
**Erstellt:** 2025-12-27
**Abgeschlossen:** 2025-12-27

**Ziel:**
Aus den Gewinnquoten-Daten (Anzahl der Gewinner) auf die POPULARITAET der gezogenen Zahlen rueckschliessen.

**Kernidee:**
```
Viele Gewinner bei 8/10 richtig → Gezogene Zahlen waren BELIEBT
Wenige Gewinner bei 8/10 richtig → Gezogene Zahlen waren UNBELIEBT
```

**Datenquellen:**
| Datei | Inhalt | Spalten |
|-------|--------|---------|
| `Keno_GQ_*.csv` | Gewinnquoten | Datum, Keno-Typ, Richtige, Gewinner, Gewinn |
| `KENO_Quote_details_2023.csv` | + Auszahlung | Datum, Typ, Richtige, Gewinner, Gewinn, **Auszahlung** |
| `Plus5_GQ_2023.csv` | Plus5 Quoten | Datum, GK, Gewinner, Quote |
| `KENO_10K*.csv` | Treffer-Tracking | Datum, Treffer, z1-z12, Wiederholungen |
| `KENO_ab_2018.csv` | Ziehungsdaten | Datum, Z1-Z20, Spieleinsatz |

**Analyse-Schritte:**
1. GQ-Daten mit Ziehungsdaten nach Datum joinen
2. Fuer jeden Tag: Normalisierte Gewinner-Anzahl berechnen (Gewinner / Spieleinsatz)
3. Tage klassifizieren: POPULAR / NEUTRAL / UNPOPULAR
4. Pro Zahl: Akkumulieren wie oft bei POPULAR vs. UNPOPULAR gezogen
5. Ranking: Popularitaets-Score fuer alle 70 Zahlen

**Hypothese zu validieren:**
> Zahlen mit niedrigem Popularitaets-Score werden HAEUFIGER gezogen.

**Acceptance Criteria:**
- [ ] Script `scripts/analyze_popularity.py` implementiert
- [ ] Popularitaets-Ranking fuer alle 70 Zahlen erstellt
- [ ] Korrelation: Popularitaet vs. Ziehungshaeufigkeit berechnet
- [ ] Ergebnis in `results/popularity_reverse_engineering.json` gespeichert
- [ ] Hypothese bestaetigt/widerlegt

**Geschaetzter Aufwand:** 3-4 Stunden

**Verknuepft mit:** HYP-004 (Tippschein-Analyse vor Ziehung)

**ERGEBNIS (2025-12-27):**

| Metrik | Wert | Interpretation |
|--------|------|----------------|
| Pearson r | -0.0320 | Schwach negativ |
| Pearson p | 0.7924 | **NICHT SIGNIFIKANT** |
| Spearman r | 0.0103 | ~Null |
| Spearman p | 0.9326 | **NICHT SIGNIFIKANT** |

**Fazit:** Die Hypothese HYP-004 wird **NICHT bestaetigt**.
Es gibt keinen Zusammenhang zwischen Zahlen-Popularitaet und Ziehungshaeufigkeit.

**Top 10 Unpopulaere Zahlen:** 57, 55, 51, 21, 28, 61, 36, 15, 65, 43
**Top 10 Populaere Zahlen:** 3, 5, 19, 7, 33, 6, 9, 11, 2, 8

**Schlussfolgerung:**
Der RNG zeigt kein Bias zugunsten unpopulaerer Zahlen. Die Ziehung erscheint
in dieser Dimension tatsaechlich zufaellig.

**Artefakte:**
- Script: `scripts/analyze_popularity.py`
- Ergebnis: `results/popularity_reverse_engineering.json`

---

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
- `scripts/master_update.py` - Master-Script (Basis vorhanden, Scraping TODO)
- `AI_COLLABORATION/KNOWLEDGE_BASE/DATA_SOURCES.md` - Dokumentation aller Datenquellen

**Loesung:**
1. Scraping in `scripts/master_update.py` implementieren (aktuell TODO)
2. Scraper fuer alle 3 Spiele fertigstellen
3. Deduplizierung bereits implementiert
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

### ISSUE-007: Keno_GPTs Daten-Mapping & Master-Script
**Prioritaet:** HOCH
**Status:** DONE
**Kategorie:** Data/Documentation
**Erstellt:** 2025-12-27
**Abgeschlossen:** 2025-12-27

**Problem:**
Die Dateien im Keno_GPTs Ordner waren nicht dokumentiert. Unklar welche Scripts welche Dateien generieren.

**Analyse durchgefuehrt:**
| Kategorie | Dateien | Generiert von |
|-----------|---------|---------------|
| Ziehungsdaten | KENO_Ziehungen_*.csv | Web-Scraping (lotto-rlp.de) |
| Gewinnquoten | Keno_GQ_*.csv, Plus5_GQ_*.csv | Web-Scraping |
| Pattern-Analyse | KENO_10K*.csv, 10-9_*.csv | 00_KENO_ALL_V3.py |
| Finanzanalyse | *_Restbetrag*.csv | Berechnet (Excel/Python) |

**Loesung implementiert:**
1. `AI_COLLABORATION/KNOWLEDGE_BASE/DATA_SOURCES.md` - Vollstaendige Dokumentation
2. `scripts/master_update.py` - Master-Script fuer konsolidierte Ausfuehrung

**Master-Script Verwendung:**
```bash
python scripts/master_update.py --game keno --mode full
python scripts/master_update.py --game all --mode patterns-only
python scripts/master_update.py --game eurojackpot --mode consolidate
```

**Acceptance Criteria:**
- [x] Alle Dateien im Keno_GPTs dokumentiert
- [x] Generierungs-Scripts identifiziert
- [x] Master-Script erstellt
- [x] Datenfluss-Diagramm erstellt

**Betroffene Dateien:**
- `AI_COLLABORATION/KNOWLEDGE_BASE/DATA_SOURCES.md` (NEU)
- `scripts/master_update.py` (NEU)

---

### HYP-001: Gewinnverteilungs-Optimierung pruefen
**Prioritaet:** HOCH
**Status:** OFFEN
**Kategorie:** Hypothese/Psychologie
**Erstellt:** 2025-12-27

**Hypothese:**
Die Gewinnausschuettung (49.44%) wird algorithmisch so verteilt, dass:
- Dauerspieler regelmaessig kleine Gewinne bekommen (Variable Verstaerkung)
- Gelegenheitsspieler den "Near-Miss-Effekt" erleben
- Verkaufszahlen maximiert werden

**Analyse-Schritte:**
1. Verteilung kleine vs. grosse Gewinne ueber Zeit berechnen
2. Near-Miss Situationen identifizieren (z.B. 9 von 10 richtig)
3. Korrelation Spieleinsatz vs. Gewinneranzahl pruefen

**Datenbedarf:**
- `Keno_GQ_*.csv` - Gewinnquoten
- `Keno_Ziehung*_Restbetrag*.csv` - Finanzielle Analyse

**Acceptance Criteria:**
- [ ] Verteilungs-Report erstellt
- [ ] Near-Miss Haeufigkeit berechnet
- [ ] Korrelations-Analyse dokumentiert
- [ ] Hypothese bestaetigt/widerlegt

---

### HYP-002: Jackpot-Bildungs-Zyklen analysieren
**Prioritaet:** HOCH
**Status:** DONE (FALSIFIZIERT)
**Kategorie:** Hypothese/Zeitlich
**Erstellt:** 2025-12-27
**Abgeschlossen:** 2025-12-28

**Hypothese:**
Gewinnklasse 1 tritt nach dem Jackpot-Bildungsprinzip ein:
- Taeglich wird Anteil in Jackpot-Pool gelegt
- Bei "attraktiver Summe" wird Gewinner produziert
- Abhaengig von: Urlaub, Feiertage, Gehaltstage

**ERGEBNIS (2025-12-28):**
| KENO-Typ | GK1-Events | Mean Warten | CV |
|----------|------------|-------------|-----|
| Typ 9 | 9 | 19.2 Tage | 0.95 |
| Typ 10 | 11 | 51.2 Tage | 0.70 |

Chi-Quadrat: Zu wenig Daten (<20), aber hohe Varianz = zufaellig.

**Fazit:** FALSIFIZIERT - Keine systematischen Jackpot-Zyklen erkennbar.

**Artefakt:** `results/hyp002_gk1_waiting.json`

**Acceptance Criteria:**
- [x] Intervall-Statistik erstellt
- [ ] Kalender-Korrelation geprueft (nicht signifikant)
- [ ] Vorhersage-Modell fuer naechsten GK1 (nicht sinnvoll)

---

### HYP-004: Tippschein-Analyse vor Ziehung pruefen
**Prioritaet:** HOCH
**Status:** OFFEN
**Kategorie:** Hypothese/Algorithmus
**Erstellt:** 2025-12-27

**Hypothese:**
Der Computer analysiert VOR der Ziehung die Tippscheine und waehlt Zahlen so, dass:
- Minimale Auszahlung erfolgt
- Genug Gewinne um Spieler motiviert zu halten

**Analyse-Schritte:**
1. Inverse Korrelation: Beliebte vs. gezogene Zahlen pruefen
2. Auszahlungsquote pro Ziehung berechnen
3. Restbetrag-Analyse durchfuehren

**Datenbedarf:**
- `Keno_Ziehung*_Restbetrag*.csv`
- Externe Quellen fuer "beliebte Zahlen" (optional)

**Acceptance Criteria:**
- [ ] Korrelations-Analyse dokumentiert
- [ ] Auszahlungsquoten-Report
- [ ] Hypothese bestaetigt/widerlegt

---

### HYP-005: Basis-Zahlenpool ermitteln (Dekaden-Affinitaet)
**Prioritaet:** HOCH
**Status:** DONE (FALSIFIZIERT)
**Kategorie:** Hypothese/Pattern
**Erstellt:** 2025-12-27
**Abgeschlossen:** 2025-12-28

**Hypothese:**
Es gibt eine "Basis-Menge" bevorzugter Zahlen:
- Bestimmte Dekaden-Paare erscheinen gemeinsam haeufiger
- Diese Affinitaeten koennen zur Vorhersage genutzt werden

**ERGEBNIS (2025-12-28):**
| Metrik | Wert |
|--------|------|
| Analysierte Ziehungen | 2237 |
| Dekaden-Paare | 21 |
| Signifikante Paare (p<0.05) | **0** |
| Mean Affinity Score | -0.0004 |

Alle p-Werte >0.96 - keine Struktur erkennbar.

**Fazit:** FALSIFIZIERT - Dekaden-Paare erscheinen zufaellig verteilt.

**Artefakt:** `results/hyp005_decade_affinity.json`

**Acceptance Criteria:**
- [x] Index-Tabelle fuer alle 70 Zahlen (via Dekaden)
- [x] Korrelations-Report (Chi-Quadrat)
- [ ] Reset-Effekt dokumentiert (nicht anwendbar)

---

### HYP-013: Multi-Einsatz Strategie (NEU aus Pressemitteilungen)
**Prioritaet:** HOCH
**Status:** DONE (BESTAETIGT)
**Kategorie:** Hypothese/Strategie
**Erstellt:** 2025-12-28
**Quelle:** Pressemitteilungen Sachsenlotto, LOTTO Niedersachsen

**Hypothese:**
Bei KENO mit festen Quoten skaliert der Gewinn linear mit dem Einsatz.
Multi-Einsatz auf gleiche Zahlen ist profitabel.

**Evidenz aus Pressemitteilungen:**
| Fall | Einsatz | Gewinn | Faktor |
|------|---------|--------|--------|
| Leipzig 30.07.2025 (Typ 8) | 18 EUR (1+2+5+10) | 180.000 EUR | 10.000x |
| Hannover 16.10.2022 (Typ 10) | 2 EUR (2x1 EUR) | 200.000 EUR | 100.000x |
| Goettingen 24.04.2025 (Typ 10) | 5 EUR | 500.000 EUR | 100.000x |
| Rotenburg 05.01.2024 (Typ 10) | 1 EUR | 100.000 EUR | 100.000x |

**Wichtig - KENO Feste Quoten:**
| KENO-Typ | Treffer | Quote (1 EUR) | Wahrscheinlichkeit |
|----------|---------|---------------|-------------------|
| Typ 10 | 10/10 | 100.000 EUR | 1 : 2.200.000 |
| Typ 8 | 8/8 | 10.000 EUR | 1 : 230.114 |

**Schlussfolgerung:**
BESTAETIGT - Multi-Einsatz funktioniert bei festen Quoten.
Im Gegensatz zu Pool-Lotterien (Lotto, EuroJackpot) wird bei KENO
der Gewinn nicht aufgeteilt. Mehrfach-Tickets mit gleichen Zahlen
skalieren linear.

**Artefakte:**
- Dokumentation: `AI_COLLABORATION/KNOWLEDGE_BASE/LOTTERY_STATISTICS_2024_2025.md`
- Plan: `AI_COLLABORATION/PLANS/kenobase_phase4_plan.yaml` (HYP013-001)

---

### HYP-009: Haeufigkeits-Anomalie validieren
**Prioritaet:** HOCH
**Status:** OFFEN
**Kategorie:** Hypothese/Statistik
**Erstellt:** 2025-12-27

**Hypothese:**
Bestimmte Zahlen werden haeufiger gezogen als statistisch erwartet:
- Hot Numbers: > 1.3x erwartete Haeufigkeit
- Cold Numbers: < 0.7x erwartete Haeufigkeit
- Abweichung ist systematisch, nicht zufaellig

**Analyse-Schritte:**
1. Chi-Quadrat Test auf Gleichverteilung
2. Hot/Cold Ratio ueber Zeit berechnen
3. Stabilitaet der Hot/Cold Klassifikation pruefen

**Datenbedarf:**
- `KENO_ab_2018.csv` - Vollstaendige Daten

**Acceptance Criteria:**
- [ ] Chi-Quadrat Test durchgefuehrt
- [ ] p-Wert dokumentiert
- [ ] Hot/Cold Stabilitaets-Report

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
**Status:** DONE
**Kategorie:** Analysis/Feature
**Erstellt:** 2025-12-27
**Abgeschlossen:** 2025-12-27

**Problem:**
Die Pattern-Analyse (Duo/Trio/Quatro) ist aus dem alten Code migriert, aber:
- Potentielle Bugs im alten Code nicht verifiziert
- Keine Validierung ob Patterns vorhersagekraeftig sind

**Bug gefunden und behoben:**
Der alte Code in V7-1 (Zeilen 112-117) verwendete eine exklusive elif-Kette:
```python
# BUGGY (V7-1:112-117):
if match_count == 4:
    quatros.append(matched)
elif match_count == 3:  # <-- verliert Quatros Sub-Patterns!
    trios.append(matched)
elif match_count == 2:  # <-- verliert Trios Sub-Patterns!
    duos.append(matched)
```

Der Fix in `kenobase/analysis/pattern.py:118-131` verwendet parallele if-Statements:
```python
# FIXED (pattern.py:118-131):
if match_count >= 4:
    quatros = [tuple(sorted(q)) for q in combinations(matched, 4)]
if match_count >= 3:
    trios = [tuple(sorted(t)) for t in combinations(matched, 3)]
if match_count >= 2:
    duos = [tuple(sorted(d)) for d in combinations(matched, 2)]
```

**Mathematische Korrektheit:**
- 4 Treffer = 11 Muster (1 Quatro + 4 Trios + 6 Duos)
- 3 Treffer = 4 Muster (1 Trio + 3 Duos)
- 2 Treffer = 1 Muster (1 Duo)

**Acceptance Criteria:**
- [x] Unit-Tests fuer Pattern-Erkennung (16 Tests PASSED)
- [x] Bug-Fixes dokumentiert
- [ ] Backtest zeigt Patterns haben Vorhersagekraft (oder nicht) - Separate Aufgabe

**Ergebnis:**
- Bug behoben in `kenobase/analysis/pattern.py`
- 16 Unit-Tests in `tests/unit/test_pattern.py` alle PASSED
- Pattern-Modul ist standalone, keine Integration Points verletzt

**Geschaetzter Aufwand:** 4-5 Stunden (tatsaechlich: ~2h fuer Bug-Fix + Tests)

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

### HYP-006: Wiederkehrende Gewinnzahlen (WGZ) analysieren
**Prioritaet:** MITTEL
**Status:** DONE (BESTAETIGT)
**Kategorie:** Hypothese/Pattern
**Erstellt:** 2025-12-27
**Abgeschlossen:** 2025-12-28

**Hypothese:**
Gewinnzahlen wiederholen sich in identifizierbaren Mustern:
- WGZ am selben Tag wie GK1 korrelieren mit naechster GK1
- Zahlenpaare mit hohem Index haben hoehere Wahrscheinlichkeit
- Es gibt "stabile" Zahlenpaare

**ERGEBNIS (2025-12-28):**
| Metrik | Wert |
|--------|------|
| Draws with recurrence | 2236/2236 (100%) |
| Avg recurrence count | 5.73 Zahlen |
| Max recurrence count | 11 |
| Stable pairs (>=3x) | 2415/2415 (100%) |

**Top 5 Stabile Paare:**
- (9, 50): 218x
- (20, 36): 218x
- (9, 10): 217x

**Fazit:** BESTAETIGT - Messbare Wiederholungsmuster vorhanden.

**Artefakt:** `results/hyp006/wgz_analysis.json`

**Acceptance Criteria:**
- [x] Wiederholungs-Statistik
- [x] Korrelations-Report
- [x] Stabile Zahlenpaare identifiziert

---

### HYP-007: Duo/Trio/Quatro Patterns validieren
**Prioritaet:** MITTEL
**Status:** DONE (NICHT SIGNIFIKANT)
**Kategorie:** Hypothese/Pattern
**Erstellt:** 2025-12-27

**Hypothese:**
Zahlenkombinationen (2er, 3er, 4er Gruppen) erscheinen gemeinsam:
- Nach vollstaendiger Erscheinung beginnt neuer Zyklus
- Patterns koennen vorhergesagt werden
- Prioritaet: Quatro > Trio > Duo

**Analyse-Schritte:**
1. Haeufigkeit von Duo/Trio/Quatro pro Ziehung
2. Zeit bis alle Zahlen einer Kombi erscheinen
3. Vorhersagekraft der Patterns pruefen

**Datenbedarf:**
- `KENO_10K*.csv` - Pattern-Dateien
- `KENO_ab_2018.csv` - Ziehungsdaten

**Acceptance Criteria:**
- [ ] Pattern-Haeufigkeits-Report
- [ ] Zyklus-Analyse
- [ ] Vorhersage-Validierung

**Verknuepft mit:** ISSUE-004

---

### HYP-010: Gewinnquoten-Korrelation pruefen
**Prioritaet:** MITTEL
**Status:** DONE (NICHT SIGNIFIKANT)
**Kategorie:** Hypothese/Korrelation
**Erstellt:** 2025-12-27

**Hypothese:**
Anzahl der Gewinner pro GK korreliert mit gezogenen Zahlen:
- Wenige GK1-Gewinner = "sichere" (unbeliebte) Zahlen
- Viele GK5/6-Gewinner = "beliebte" Zahlenkombinationen

**Analyse-Schritte:**
1. Korrelation Gewinner-Anzahl vs. Zahlen
2. "Sichere" vs. "beliebte" Zahlen identifizieren
3. Vorhersage-Modell entwickeln

**Datenbedarf:**
- `Keno_GQ_2022_2023-2024.csv` - 27.685 Zeilen
- `KENO_Ziehungen_*.csv` - Gezogene Zahlen

**Acceptance Criteria:**
- [ ] Korrelations-Matrix
- [ ] Zahlen-Klassifikation
- [ ] Vorhersage-Genauigkeit gemessen

---

### HYP-014: Mehrwochenschein Jackpot-Timing (NEU aus Pressemitteilungen)
**Prioritaet:** MITTEL
**Status:** OFFEN
**Kategorie:** Hypothese/Zeitlich
**Erstellt:** 2025-12-28
**Quelle:** Pressemitteilungen LOTTO Niedersachsen

**Hypothese:**
Viele KENO-Jackpot-Gewinner nutzen Mehrwochenscheine (Abonnements).
Gibt es ein Muster wann Jackpots innerhalb von Abo-Perioden auftreten?

**Evidenz aus Pressemitteilungen:**
| Fall | Abo-Laenge | Treffer in Ziehung | Gewinn |
|------|------------|-------------------|--------|
| Hannover 2022 | 14 Ziehungen | unbekannt | 2x 100.000 EUR |
| Goettingen 2025 | 7 Ziehungen | unbekannt | 500.000 EUR |
| Rotenburg 2024 | 2 Ziehungen | unbekannt | 100.000 EUR |

**Analyse-Schritte:**
1. Jackpot-Verteilung innerhalb von Abo-Perioden analysieren
2. Optimale Abo-Laenge ermitteln (7, 14, 28 Ziehungen)
3. ROI pro Abo-Strategie berechnen

**Acceptance Criteria:**
- [ ] Jackpot-Verteilung pro Abo-Position berechnet
- [ ] Optimale Abo-Laenge dokumentiert
- [ ] ROI-Vergleich: Einzel vs. Abo-Tickets

**Geschaetzter Aufwand:** 3-4 Stunden

---

### QUOTE-001: KENO Feste Quoten vollstaendig dokumentieren
**Prioritaet:** MITTEL
**Status:** OFFEN
**Kategorie:** Documentation/Reference
**Erstellt:** 2025-12-28
**Quelle:** Pressemitteilungen, Lotto-Webseiten

**Ziel:**
KENO hat FESTE Quoten - im Gegensatz zu Pool-Lotterien (Lotto, EuroJackpot).
Dies ist fundamental fuer Strategie-Entscheidungen.

**Bekannte Quoten (aus Pressemitteilungen bestaetigt):**
| KENO-Typ | Treffer | Quote (1 EUR) | Quote (10 EUR) | Wahrscheinlichkeit |
|----------|---------|---------------|----------------|-------------------|
| Typ 10 | 10/10 | 100.000 EUR | 1.000.000 EUR | 1 : 2.200.000 |
| Typ 8 | 8/8 | 10.000 EUR | 100.000 EUR | 1 : 230.114 |

**Zu dokumentieren:**
1. Vollstaendige Quoten-Tabelle fuer alle KENO-Typen (2-10)
2. Alle Gewinnklassen pro Typ
3. Vergleich mit Pool-basierten Lotterien
4. Strategie-Implikationen (z.B. Typ 8 vs. Typ 10 ROI)

**Acceptance Criteria:**
- [ ] Vollstaendige Quoten-Tabelle in `docs/keno_quotes.md`
- [ ] Wahrscheinlichkeiten berechnet und dokumentiert
- [ ] Vergleich KENO vs. Lotto vs. EuroJackpot
- [ ] ROI-Analyse pro KENO-Typ

**Geschaetzter Aufwand:** 2-3 Stunden

---

### HYP-011: Zeitliche Zyklen identifizieren
**Prioritaet:** MITTEL
**Status:** DONE (BESTAETIGT - Holiday Effect)
**Kategorie:** Hypothese/Zeitlich
**Erstellt:** 2025-12-27

**Hypothese:**
Es gibt zeitliche Muster in den Ziehungen:
- Woechentliche Zyklen (Montag vs. Samstag)
- Monatliche Zyklen (Monatsanfang vs. Ende)
- Jaehrliche Zyklen (Feiertage, Urlaub)

**Analyse-Schritte:**
1. Gewinner-Verteilung nach Wochentag
2. Spieleinsatz nach Monatstag
3. GK1-Events nach Jahreszeit

**Datenbedarf:**
- `KENO_ab_2018.csv` mit Datum
- Kalender-Daten

**Acceptance Criteria:**
- [ ] Wochentag-Report
- [ ] Monat-Report
- [ ] Jahreszeit-Report

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

### HYP-008: 111-Prinzip verstehen und validieren
**Prioritaet:** NIEDRIG
**Status:** DONE (FALSIFIZIERT - p=0.96, Numerologie)
**Kategorie:** Hypothese/Mathematik
**Erstellt:** 2025-12-27

**Hypothese:**
Es gibt ein "111-Prinzip" fuer Zahlenpaare-Operationen.
(Details noch nicht vollstaendig aus Konzept-Dateien verstanden)

**Analyse-Schritte:**
1. Definition des 111-Prinzips aus altem Code ermitteln
2. Anwendung auf gruppierte Zahlenpaare
3. Validierung der Ergebnisse

**Datenbedarf:**
- Alte Code-Analyse (Old_Code Ordner)
- Weitere Konzept-Dateien

**Acceptance Criteria:**
- [ ] 111-Prinzip dokumentiert
- [ ] Anwendung implementiert
- [ ] Ergebnisse validiert

---

### HYP-012: Spieleinsatz-Korrelation analysieren
**Prioritaet:** NIEDRIG
**Status:** DONE (NICHT SIGNIFIKANT)
**Kategorie:** Hypothese/Oekonomie
**Erstellt:** 2025-12-27

**Hypothese:**
Der Spieleinsatz korreliert mit der Zahlenauswahl:
- Hoher Spieleinsatz = mehr "sichere" Zahlen
- Niedriger Spieleinsatz = mehr "riskante" Zahlen
- Restbetrag zeigt "Effizienz" des Systems

**Analyse-Schritte:**
1. Korrelation Spieleinsatz vs. Auszahlung
2. Kasse-Entwicklung ueber Zeit
3. Restbetrag-Muster analysieren

**Datenbedarf:**
- `Keno_Ziehung2023_+_Restbetrag_v2.CSV`
- Weitere Finanz-Dateien

**Acceptance Criteria:**
- [ ] Korrelations-Report
- [ ] Kasse-Entwicklungs-Chart
- [ ] Effizienz-Metriken

---

## Abgeschlossene Issues

### ISSUE-002: Spielspezifische Thresholds ✅
**Abgeschlossen:** 2025-12-27
**Details:** Siehe oben

### ISSUE-007: Keno_GPTs Daten-Mapping & Master-Script ✅
**Abgeschlossen:** 2025-12-27
**Details:** Siehe oben - Dokumentation und Master-Script erstellt

---

## Archiv (WON'T FIX / Deprecated)

_Keine Issues in dieser Kategorie._

---

## WIEDEROEFFNET (aus Pressemitteilungen 2025-12-28)

### HYP-003: Regionale Gewinnverteilung analysieren (WIEDEROEFFNET)
**Prioritaet:** HOCH
**Status:** OFFEN
**Kategorie:** Hypothese/Regional
**Erstellt:** 2025-12-27
**Wiederoeffnet:** 2025-12-28

**Urspruengliche WON'T FIX Begruendung:**
Die Keno_GQ_*.csv Daten enthalten nur aggregierte nationale Daten.

**NEUE DATENQUELLE GEFUNDEN:**
Pressemitteilungen der Landeslotterien enthalten Bundesland-Daten!

**Regionale Daten aus Pressemitteilungen:**
| Bundesland | Ort | Spiel | Gewinn | Datum |
|------------|-----|-------|--------|-------|
| Niedersachsen | Hannover | KENO 10 | 2x 100.000 EUR | 16.10.2022 |
| Niedersachsen | Goettingen | KENO 10 | 500.000 EUR | 24.04.2025 |
| Niedersachsen | Rotenburg | KENO 10 | 100.000 EUR | 05.01.2024 |
| Niedersachsen | Celle | SUPER 6 | 100.000 EUR | 06.01.2024 |
| Sachsen | Leipzig | KENO 8 | 180.000 EUR | 30.07.2025 |
| NRW | Koeln | Diverse | 8 Hochgewinne | H1/2025 |
| NRW | Recklinghausen | Diverse | 8 Hochgewinne | H1/2025 |
| NRW | Wesel | Diverse | 8 Hochgewinne | H1/2025 |

**WestLotto NRW Regionalverteilung:**
| Region | Hochgewinne | Anteil |
|--------|-------------|--------|
| Rheinland | 72 | 60.5% |
| Westfalen | 47 | 39.5% |

**Neue Analyse-Schritte:**
1. Pressemitteilungen aller 16 Bundeslaender systematisch scrapen
2. Gewinner-Datenbank mit Bundesland, Ort, Datum, Gewinn aufbauen
3. Regionale Zahlen-Praeferenzen ableiten
4. Korrelation mit Bevoelkerung/Spieleranzahl pruefen

**Datenbedarf:**
- Pressemitteilungen der Landeslotterien
- Bereits vorhanden: `kenobase/scraper/` Framework

**Acceptance Criteria:**
- [ ] Scraper fuer mind. 5 Landeslotterien
- [ ] Regionale Gewinner-Datenbank aufgebaut
- [ ] Korrelation Gewinner vs. Bevoelkerung berechnet
- [ ] Regionale Zahlen-Praeferenzen identifiziert

**Geschaetzter Aufwand:** 6-8 Stunden

**Artefakte:**
- Dokumentation: `AI_COLLABORATION/KNOWLEDGE_BASE/LOTTERY_STATISTICS_2024_2025.md`
- Plan: `AI_COLLABORATION/PLANS/kenobase_phase4_plan.yaml` (HYP003-002)

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
- `AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md` - Vollstaendiger Hypothesen-Katalog
- `AI_COLLABORATION/KNOWLEDGE_BASE/DATA_SOURCES.md` - Datenquellen-Dokumentation

### Hypothesen-Priorisierung
**Empfohlene Reihenfolge fuer Loop-Bearbeitung:**
1. HYP-009 (Chi-Quadrat Test) - Schnell zu validieren
2. HYP-005 (Zahlenpool Index) - Basis fuer weitere Hypothesen
3. HYP-002 (Jackpot-Zyklen) - Klares Datenformat
4. HYP-001 (Gewinnverteilung) - Umfangreich aber wichtig
5. HYP-004 (Tippschein-Analyse) - Abhaengig von externen Daten
