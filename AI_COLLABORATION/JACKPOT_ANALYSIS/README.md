# Jackpot Selection Analysis

**Status:** IN PROGRESS
**Letzte Aktualisierung:** 2026-01-01

---

## Ziel

Reverse-Engineering des KENO Jackpot-Auswahlalgorithmus:
- Wie wählt das System aus den 20 gezogenen Zahlen die 10 "Gewinner-Zahlen"?
- Welche Kriterien werden verwendet?
- Können wir diese Regeln nutzen?

---

## Architektur-Dokument

Siehe: `AI_COLLABORATION/ARCHITECTURE/JACKPOT_SELECTION_ANALYSIS.md`

---

## Aktueller Stand

### Analysierte Jackpots

| Datum | Region | Status | Erkenntnisse |
|-------|--------|--------|--------------|
| 2025-10-25 | Kyritz, Brandenburg | ANALYSIERT | 8 gerade, keine konsekutiven |

### Gefundene Muster

1. **Gerade Zahlen:** Gewinner hat 8/10 gerade (Top 1%)
2. **Historische Reife:** Gewinner war bereits am Vortag 10/10
3. **Keine Konsekutiven:** Min. Abstand = 2

---

## Offene Tasks

| ID | Task | Priorität | Status |
|----|------|-----------|--------|
| T1.1 | Weitere Jackpot-Events dokumentieren | P0 | OFFEN |
| T2.4 | Temporale Features hinzufügen | P1 | OFFEN |
| T3.1 | Kyritz vollständig analysieren (alle 184k) | P1 | TEIL |
| T4.1 | Konsistente Features identifizieren | P2 | OFFEN |

---

## Für KIs: Wie beitragen?

1. Lies die Architektur: `ARCHITECTURE/JACKPOT_SELECTION_ANALYSIS.md`
2. Wähle eine Perspektive (Statistisch, Strukturell, Temporal, etc.)
3. Führe Analyse durch
4. Speichere Ergebnisse in `results/layerX_...`
5. Aktualisiere dieses README

---

## Wichtige Dateien

```
JACKPOT_ANALYSIS/
├── README.md                    # DIESES DOKUMENT
├── config.yaml                  # Konfiguration
├── data/
│   └── jackpot_events.json      # Alle Jackpot-Events
├── results/
│   ├── layer1_features/         # Feature-Berechnungen
│   ├── layer2_combinations/     # Kombinations-Analysen
│   ├── layer3_patterns/         # Muster
│   ├── layer4_rules/            # Regeln
│   └── layer5_strategy/         # Strategien
└── reports/
    └── ERKENNTNISSE.md          # Laufende Erkenntnisse
```
