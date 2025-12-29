## Hypothesen aus Pressemitteilungen

**Generiert:** 2025-12-28 17:14
**Records analysiert:** 8
**Quellen:** 5

### HYP-PRESS-001: Regionale KENO-Gewinner-Verteilung
**Kategorie:** Regional
**Prioritaet:** MITTEL
**Konfidenz:** 48%
**Testbar:** Ja

**Beschreibung:**
KENO-Hochgewinne sind regional ungleich verteilt. Niedersachsen zeigt ueberdurchschnittlich viele Gewinne (37.5%). Dies koennte auf Spielerverhalten, Bevoelkerungsdichte oder Zufall zurueckzufuehren sein.

**Evidenz:**
- Top Bundesland: Niedersachsen (3/8, 37.5%)
-   - Niedersachsen: 3 (37.5%)
-   - NRW: 2 (25.0%)
-   - Sachsen: 1 (12.5%)
-   - Bayern: 1 (12.5%)
-   - Hamburg: 1 (12.5%)
- Top Orte: Hannover, Region Hannover, Landkreis Goettingen

**Acceptance Criteria:**
- [ ] Chi-Quadrat-Test auf Bevoelkerungs-Proportionalitaet
- [ ] Vergleich mit DLTB-Statistiken (20% NRW Anteil)
- [ ] Korrektur fuer unterschiedliche Spielerzahlen pro Bundesland

**Datenbedarf:**
- Bevoelkerungszahlen pro Bundesland
- KENO-Spielerzahlen pro Bundesland (falls verfuegbar)
- Mehr Pressemitteilungen fuer statistische Signifikanz

---

### HYP-PRESS-002: KENO-Typ Praeferenz bei Hochgewinnen
**Kategorie:** Strategie
**Prioritaet:** MITTEL
**Konfidenz:** 70%
**Testbar:** Ja

**Beschreibung:**
KENO Typ 10 dominiert die Pressemitteilungen (62.5%). Dies ist bedingt durch hohe Quoten (100.000x) und Nachrichtenwert. Typ 8/9 erscheinen seltener trotz hoeherer Gewinnwahrscheinlichkeit.

**Evidenz:**
- KENO-Typ Verteilung der Hochgewinne:
-   - Typ 8: 2 (25.0%), Avg: 115,000 EUR
-   - Typ 9: 1 (12.5%), Avg: 250,000 EUR
-   - Typ 10: 5 (62.5%), Avg: 200,000 EUR

**Acceptance Criteria:**
- [ ] Vergleich mit tatsaechlicher GK1-Verteilung nach Typ
- [ ] ROI-Berechnung: Typ 10 vs Typ 8 vs Typ 6
- [ ] Erwartungswert-Analyse pro KENO-Typ

**Datenbedarf:**
- Offizielle KENO-Quoten und Wahrscheinlichkeiten
- Historische GK1-Events nach Typ aus Keno_GPTs Daten

---

### HYP-PRESS-003: Gewinnhoehen-Clustering bei KENO
**Kategorie:** Oekonomie
**Prioritaet:** NIEDRIG
**Konfidenz:** 60%
**Testbar:** Ja

**Beschreibung:**
KENO-Hochgewinne clustern um bestimmte Betraege (100k, 500k). Dies entspricht den festen Quoten und typischen Einsatzhoehen. Multi-Einsatz-Strategien fuehren zu aggregierten Gewinnen.

**Evidenz:**
- Gewinnspanne: 50,000 - 500,000 EUR
- Durchschnitt: 185,000 EUR
- Median: 180,000 EUR
- Verteilung nach Groesse:
-   - 50k-100k: 1
-   - 100k-500k: 6
-   - 500k+: 1

**Acceptance Criteria:**
- [ ] Vergleich mit festen KENO-Quoten (10k, 100k, 1M)
- [ ] Analyse typischer Einsatzhoehen (1, 2, 5, 10 EUR)
- [ ] Identifikation von Multi-Einsatz-Faellen

**Datenbedarf:**
- KENO Quoten-Tabelle pro Typ und Einsatz
- Detaillierte Gewinnaufschluesselung aus Pressemitteilungen

---

### HYP-PRESS-004: Zeitliche Muster bei KENO-Hochgewinnen
**Kategorie:** Zeitlich
**Prioritaet:** NIEDRIG
**Konfidenz:** 40%
**Testbar:** Ja

**Beschreibung:**
KENO-Hochgewinne zeigen moegliche zeitliche Muster. Bestimmte Monate oder Wochentage koennten haeufiger vorkommen. Korrelation mit Spielerverhalten und Jackpot-Zyklen moeglich.

**Evidenz:**
- Zeitliche Verteilung der Hochgewinne:
-   - Top Monat: Oktober (1x)
-   - Top Wochentag: Mittwoch (2x)

**Acceptance Criteria:**
- [ ] Chi-Quadrat-Test auf Gleichverteilung
- [ ] Vergleich mit HYP-011 (Feiertags-Effekt)
- [ ] Kontrolle fuer Pressemitteilungs-Timing vs. Ziehungs-Timing

**Datenbedarf:**
- Vollstaendige KENO-Ziehungsdaten mit Datum
- Feiertags-Kalender (bereits in HYP-011 genutzt)

---

### HYP-PRESS-005: Gewinnzahlen-Muster in Pressemitteilungen
**Kategorie:** Pattern
**Prioritaet:** MITTEL
**Konfidenz:** 50%
**Testbar:** Ja

**Beschreibung:**
Birthday-Zahlen (1-31) machen 33.3% der Gewinnzahlen aus (erwartet: 44.3%). Abweichungen koennten auf Spielerverhalten oder Selection Bias hindeuten.

**Evidenz:**
- Analysierte Zahlen: 63
- Birthday-Zahlen (1-31): 21 (33.3%)
- Erwarteter Anteil: 44.3%
- Haeufigste Zahlen:
-   - 70: 4x
-   - 68: 3x
-   - 41: 2x
-   - 38: 2x
-   - 63: 2x

**Acceptance Criteria:**
- [ ] Vergleich mit HYP-004 (Birthday-Korrelation r=0.39)
- [ ] Binomial-Test auf Birthday-Abweichung
- [ ] Kontrolle fuer Selection Bias (nur Hochgewinne publiziert)

**Datenbedarf:**
- Mehr extrahierte Gewinnzahlen aus Pressemitteilungen
- Vollstaendige KENO-Ziehungsdaten zum Vergleich

---
