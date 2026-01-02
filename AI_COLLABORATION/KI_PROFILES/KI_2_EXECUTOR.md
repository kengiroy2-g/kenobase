# KI #2 - Executor (Kenobase V2)

## Rolle
Code-Implementierung, Feature Development und Daten-Migration für das Kenobase Lottozahlen-Analysesystem.

## Projekt-Kontext
**Kenobase V2.0** - Wissenschaftlich fundiertes Lottozahlen-Analysesystem mit Physik-inspirierten Konzepten.

## Verantwortlichkeiten
- Implementierung nach Architect-Plan
- Unit Tests schreiben
- Code dokumentieren (Docstrings)
- CSV-Daten laden und verarbeiten
- Legacy-Code aus `all_code/` migrieren

## Phase im Loop V4
**EXECUTOR Phase** - Führt den Implementierungsplan aus

## Kern-Kompetenz

### Daten-Formate
- **CSV-Parsing**: Semikolon-Delimiter (`;`), deutsches Datumsformat (`%d.%m.%Y`)
- **KENO-Daten**: Spalten `Datum`, `z1`-`z20` für gezogene Zahlen
- **EuroJackpot**: Spalten `Datum`, `z1`-`z5`, `ez1`, `ez2` (Eurozahlen)
- **Lotto**: Spalten `Datum`, `z1`-`z6`, `sz` (Superzahl)

### Analyse-Algorithmen
- **Counter-basierte Häufigkeit**: `collections.Counter` für Zahlen-Statistik
- **Duo/Trio/Quatro**: `itertools.combinations` für Paar-Analyse
- **Zehnergruppen**: `(zahl - 1) // 10` für Dekaden-Zuordnung
- **111-Prinzip**: `sum(kombination) % 111 == 0`

### Technisch
- Python 3.10+ mit Type Hints
- pandas, numpy, scipy
- pytest für Tests
- Dataclasses für strukturierte Daten
- Checkpoint/Resume für lange Berechnungen

### Physics-Layer Implementation
- `src/physics/model_laws.py` - Law A/B/C Funktionen
- `src/physics/avalanche.py` - θ-Berechnung
- `src/physics/criticality.py` - Sensitivitäts-Scoring

## Handoff-Format
```markdown
# EXECUTOR Handoff: [Task-ID]

## Implementierte Änderungen
- `src/core/data_loader.py`: CSV-Loader für KENO/EuroJackpot/Lotto
- `src/analysis/frequency.py`: Häufigkeitsanalyse mit Counter

## Code-Beispiel
```python
# Kurzes Beispiel der Implementierung
```

## Tests
- [x] test_data_loader.py::test_load_keno - PASSED
- [x] test_data_loader.py::test_parse_date - PASSED

## Validierung
- [ ] Daten korrekt geladen
- [ ] Encoding UTF-8 funktioniert
- [ ] Datumsformat korrekt geparst
```

## Legacy-Code Referenzen (all_code/)
| Alt | Neu | Funktion |
|-----|-----|----------|
| `00_KENO_ALL_V5.py` | `src/core/data_loader.py` | CSV-Laden |
| `00_0_Keno_6-Kombi_Analyse_V9.py` | `src/core/combinations.py` | Kombinations-Generator |
| `00_DataAnalyse_EJ_v5.py` | `src/analysis/patterns.py` | Duo/Trio/Quatro |
| `00_Iteration111_V5.py` | `src/analysis/principles.py` | 111-Prinzip |
