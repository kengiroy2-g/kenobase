# Datei-Liste fuer KI-Review

**Erstellt:** 2026-01-02
**Zweck:** Schnelle Referenz aller relevanten Dateien

---

## PRIORITAET 1: Kern-Dokumente (MUSS LESEN)

```
CLAUDE.md                                                    # Projekt-Ueberblick
AI_COLLABORATION/KNOWLEDGE_BASE/HYPOTHESES_CATALOG.md        # Alle 23 Hypothesen
AI_COLLABORATION/KNOWLEDGE_BASE/STRATEGY_DANCE_KOMPENDIUM.md # Strategien
AI_COLLABORATION/HANDOFFS/HANDOFF_INDEPENDENT_REVIEW.md      # Dieses Handoff
```

---

## PRIORITAET 2: Haupt-Scripts (ZUM TESTEN)

```
scripts/generate_optimized_tickets.py      # V2 Pool-Generator (HAUPT)
scripts/backtest_pool_v1_vs_v2.py          # V1 vs V2 Vergleich
scripts/analyze_pool_misses_deep.py        # Pattern-Analyse
scripts/validate_pool_tickets_rigorous.py  # Pool-GK Validierung
scripts/backtest_post_jackpot.py           # Jackpot-Cooldown
scripts/analyze_cycles_comprehensive.py    # Zyklus-Analyse
scripts/test_dance_hypotheses.py           # Dance-Hypothesen
```

---

## PRIORITAET 3: Ergebnis-Dateien (ZUM PRUEFEN)

```
results/pool_v1_vs_v2_backtest.json           # V2 +3.2% besser
results/pool_miss_deep_analysis.json          # BAD/GOOD Patterns
results/pool_tickets_rigorous_validation.json # Keine GK-Ueberlappung
results/post_jackpot_backtest.json            # -66% nach Jackpot
results/cycles_comprehensive_analysis.json    # FRUEH vs SPAET
```

---

## PRIORITAET 4: Rohdaten (ZUM VALIDIEREN)

```
data/raw/keno/KENO_ab_2022_bereinigt.csv      # Ziehungen 2022-2025
Keno_GPTs/Keno_GQ_2025.csv                    # Gewinnquoten 2025
Keno_GPTs/Keno_GQ_2022_2023-2024.csv          # Gewinnquoten 2022-2024
```

---

## PRIORITAET 5: Konversations-Historie

```
AI_COLLABORATION/ARTIFACTS/conversation_2025_monthly_pool_validation.md
```

---

## SCHNELL-TEST BEFEHLE

```powershell
# 1. V1 vs V2 (2 Min)
python scripts/backtest_pool_v1_vs_v2.py

# 2. Pattern-Analyse (1 Min)
python scripts/analyze_pool_misses_deep.py

# 3. Ticket-Generator (10 Sek)
python scripts/generate_optimized_tickets.py --top 3

# 4. Unit-Tests (30 Sek)
pytest tests/unit/ -v --tb=short
```

---

## KERN-BEHAUPTUNGEN ZUM PRUEFEN

| # | Behauptung | Evidenz-Datei | Skeptisch weil... |
|---|------------|---------------|-------------------|
| 1 | V2 +3.2% besser | pool_v1_vs_v2_backtest.json | Overfitting? |
| 2 | BAD_PATTERNS >75% Miss | pool_miss_deep_analysis.json | Sample Size? |
| 3 | Pool ≤17 = 100% 6/6 in 56d | (mathematisch) | Trivial? |
| 4 | Keine Pool-GK Ueberlappung | pool_tickets_rigorous_validation.json | Artefakt? |
| 5 | -66% nach Jackpot | post_jackpot_backtest.json | N=11 zu klein? |
| 6 | FRUEH +422% vs SPAET | cycles_comprehensive_analysis.json | Data-Snooping? |

---

## KRITISCHE FRAGEN

1. Ist IRGENDETWAS davon nicht durch Zufall erklaerbar?
2. Wurde FDR/Bonferroni konsequent angewendet?
3. Gibt es echte Out-of-Sample Validierung?
4. Fuehrt IRGENDETWAS zu positivem ROI?
5. Ist das "Manipulation"-Axiom gerechtfertigt?

---

**Gesamtzahl relevanter Dateien:** ~25
**Geschaetzte Review-Zeit:** 2-4 Stunden
