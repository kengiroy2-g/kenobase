# Kenobase - Module Mapping (Alt -> Neu)

## Erkannte Module im alten Projekt

### 1. KENO Hauptanalyse

**Alt:** `all_code/00_KENO_ALL_V5.py`

| Funktion | Beschreibung | Neu |
|----------|--------------|-----|
| `read_draws()` | CSV laden | `src/core/data_loader.py` |
| `process_draws_for_target()` | Index-Berechnung | `src/analysis/frequency.py` |
| `document_simultaneous_appearances()` | Duo/Trio/Quatro | `src/analysis/pattern.py` |

### 2. 6er-Kombinations-Analyse

**Alt:** `all_code/00_0_Keno_6-Kombi_Analyse_V9.py`

| Funktion | Beschreibung | Neu |
|----------|--------------|-----|
| `generiere_zahlenpool_optimiert()` | Pool-Generierung | `src/core/number_pool.py` |
| `generiere_kombinationen()` | 6er-Kombis | `src/core/combination_engine.py` |
| `max_zwei_pro_zehnergruppe()` | Filter | `src/core/combination_engine.py` |
| `zaehle_kombination_batch()` | Parallel-Zaehlung | `src/analysis/pattern.py` |

### 3. 111-Prinzip

**Alt:** `all_code/00_Iteration111_V5.py`

| Funktion | Beschreibung | Neu |
|----------|--------------|-----|
| `is_multiple()` | 111-Vielfaches | `src/analysis/pattern.py` |
| `find_combinations_v2()` | Summen-Filter | `src/analysis/pattern.py` |

### 4. EuroJackpot Analyse

**Alt:** `all_code/00_DataAnalyse_EJ_v5.py`

| Funktion | Beschreibung | Neu |
|----------|--------------|-----|
| `read_draws()` | CSV laden | `src/core/data_loader.py` |
| `document_simultaneous_appearances()` | Duos/Trios | `src/analysis/pattern.py` |

### 5. Archiv-Pruefung mit Checkpoint

**Alt:** `all_code/00_EJ_check_v12_149.py`

| Funktion | Beschreibung | Neu |
|----------|--------------|-----|
| `speichere_checkpoint()` | Checkpoint | `src/pipeline/checkpoint.py` |
| `lese_checkpoint()` | Resume | `src/pipeline/checkpoint.py` |
| `batch_vorpruefung()` | Parallel-Check | `src/pipeline/validators.py` |
| `vorpruefung_gegen_archiv_parallel()` | Archiv-Vergleich | `src/pipeline/validators.py` |

## Physik-Module (NEU)

### src/physics/model_laws.py

| Funktion | ADR | Beschreibung |
|----------|-----|--------------|
| `is_law()` | ADR-018 | Stabilitaetstest |
| `calculate_pipeline_action()` | ADR-018 | Least-Action |
| `calculate_criticality()` | ADR-018/020 | Risiko-Score |

### src/physics/avalanche.py

| Funktion | ADR | Beschreibung |
|----------|-----|--------------|
| `calculate_theta()` | ADR-021 | Verlustwahrscheinlichkeit |
| `get_avalanche_state()` | ADR-021 | SAFE/MODERATE/WARNING/CRITICAL |
| `is_profitable()` | ADR-021 | p * q > 1 Check |

## Datenfluss (Gesamt)

```
[CSV-Dateien]
    |
    v
[data_loader.py] --> DataFrame
    |
    v
[number_pool.py] --> Zahlenpool (Top-11)
    |
    v
[combination_engine.py] --> 6er-Kombinationen (gefiltert)
    |
    v
[pattern.py] --> Duos, Trios, Quatros, 111-Muster
    |
    v
[model_laws.py] --> Stabilitaet, Criticality
    |
    v
[avalanche.py] --> State-Klassifikation
    |
    v
[Output] --> JSON/CSV/HTML Report
```

## Bekannte Bugs (zu fixen)

### BUG-001: Duo/Trio/Quatro Berechnung

**Quelle:** Kommentar in V7-1.py
**Beschreibung:** "Duos,trios,quatros werden falsch berechnet"
**Fix:** Vergleiche V6 vs V7-1, implementiere korrigierte Version
**Task:** phase2_task05_duo_trio_quatro_fix
