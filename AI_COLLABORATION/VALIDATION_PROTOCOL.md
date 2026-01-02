# Validierungs-Protokoll fuer KI-Analysen

**Erstellt:** 01.01.2026
**Grund:** Vermeidung von Fehlern durch ungepruefte KI-Inferenz

---

## REGEL 1: Bestehende Ergebnisse ZUERST lesen

Vor JEDER neuen Analyse:

```
1. Pruefe results/*.md und results/*.json
2. Pruefe AI_COLLABORATION/KNOWLEDGE_BASE/
3. Lese relevante frueheren Analysen
4. Notiere die BEKANNTEN FAKTEN
```

**Befehl:** "Zeige mir zuerst die bestehenden Ergebnisse zu [Thema]"

---

## REGEL 2: Keine Neuberechnung validierter Daten

VERBOTEN:
- Neue Berechnung wenn validierte Ergebnisse existieren
- Ueberschreiben von dokumentierten Fakten
- Annahmen ohne Quellenangabe

ERLAUBT:
- Neue Analyse NUR fuer neue Fragestellungen
- Erweiterung bestehender Analysen
- Validierung durch Kreuzreferenz

---

## REGEL 3: Widerspruchs-Check

Bei JEDEM neuen Ergebnis:

```
NEUES ERGEBNIS: [X]
BEKANNTES ERGEBNIS: [Y]

Widerspruch? JA/NEIN

Wenn JA:
  → STOPP
  → Fehlersuche in neuer Berechnung
  → NIEMALS altes Ergebnis verwerfen ohne Begruendung
```

---

## REGEL 4: Quellen-Pflicht

Jede Aussage braucht eine Quelle:

```
RICHTIG:
  "HZ7 W20 hatte 69 Jackpots (Quelle: results/hot_zone_fenster_vergleich_2022_2024.md)"

FALSCH:
  "HZ6 ist besser" (ohne Quelle)
```

---

## REGEL 5: Bekannte Fakten (Stand 01.01.2026)

### Hot-Zone Strategie (VALIDIERT)

| Fakt | Wert | Quelle |
|------|------|--------|
| Bestes Fenster | W20 | hot_zone_fenster_vergleich_2022_2024.md |
| HZ7 W20 Jackpots | 69 (2022-2024) | hot_zone_fenster_vergleich_2022_2024.md |
| HZ7 W20 Erfolgsquote | 75% | hot_zone_fenster_vergleich_2022_2024.md |
| Bester Einzeltag | 7 JP (23.06.2025) | hot_zone_timelines_2024_h2_w20.md |

### Timing-Regeln (VALIDIERT)

| Fakt | Wert | Quelle |
|------|------|--------|
| FRUEH-Phase ROI | +364% vs SPAET | frueh_phase_isolated_test.json |
| Cooldown Dauer | 30 Tage | cooldown_rule_isolated_test.json |
| Cooldown ROI-Effekt | -66% | FINALE_STRATEGIE_SYNTHESE.md |

### WARNUNG: Falsche Aussagen (korrigiert)

| Falsche Aussage | Korrekte Aussage |
|-----------------|------------------|
| "W100 ist optimal" | W20 ist optimal (69 vs 37 JP) |
| "HZ6 ist effizienter" | HZ7 W20 hat 69 JP, HZ6 nur wenige |
| "Loop-Erweitert beste ROI" | HZ7 W20 hat +413% ROI |

---

## Checkliste vor jeder Analyse

- [ ] Bestehende Ergebnisse gelesen?
- [ ] Bekannte Fakten notiert?
- [ ] Neue Analyse widerspricht nicht?
- [ ] Quellen fuer alle Aussagen?
- [ ] Widerspruchs-Check durchgefuehrt?

---

## Befehl fuer Benutzer

Wenn du unsicher bist, sage:

> "Pruefe zuerst die bestehenden Ergebnisse bevor du antwortest"

oder

> "Zeige mir die Quellen fuer diese Aussage"

---

*Dieses Protokoll ist verbindlich fuer alle KI-Analysen im Kenobase-Projekt.*
