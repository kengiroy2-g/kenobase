# **[[MOCs/🌍🏠Home_|🏠]]**

🔙 MOCs: [[_Root/Projekte & Dokumentation|Projekte & Dokumentation]]

⬆️[[_Root/Projekt_Keno_zahlen_Suche|Projekt_Keno_zahlen_Suche]]
⬆️[[_Root/Logik & Python Programme|Logik & Python Programme]]

⬆️[[_Root/00_KENO_ALL_V5.py]]



In Ihrem Code werden Daten aus verschiedenen CSV-Dateien verarbeitet, um Informationen zu KENO-Ziehungen zu filtern, zu analysieren und Zusammenhänge zwischen den Ziehungen zu identifizieren. Im Folgenden wird die Logik Schritt für Schritt erklärt:

### Schritt 1: Filterung und Sortierung der KENO-Gewinnquoten
- **Vorgang**: Die CSV-Datei "Keno_GQ_2023.csv" wird eingelesen. Diese Datei enthält die Gewinnquoten für verschiedene KENO-Typen.
- **Ziel**: Es werden nur die Zeilen behalten, bei denen der KENO-Typ 10 oder 9 ist, die Anzahl der richtigen Zahlen dem KENO-Typ entspricht und es mindestens 5 Gewinner gibt.
- **Ergebnis**: Die gefilterten Daten werden nach Datum sortiert und zusätzliche Informationen über die vergangenen Tage seit dem letzten Gewinn werden berechnet. Die gefilterten Daten werden dann in die Datei "10-9_KGDaten_gefiltert.csv" gespeichert.

### Schritt 2: Einlesen der Keno-Ziehungsdaten und Filterung
- **Vorgang**: Die CSV-Datei "KENO_Ziehungen_2023_GPT.csv" wird eingelesen, die die Daten aller KENO-Ziehungen des Jahres 2023 enthält.
- **Ziel**: Filterung dieser Daten, um nur die Ziehungen zu behalten, die in der gefilterten Liste aus Schritt 1 vorkommen.
- **Ergebnis**: Die gefilterten Ziehungsdaten werden in die Datei "10-9_NumbertoCheck.csv" gespeichert.

### Schritt 3 bis 5: Überprüfung der Ziehungen auf Treffer
- **Vorgang**: Die in "10-9_NumbertoCheck.csv" gefilterten Ziehungsdaten werden analysiert, um Übereinstimmungen mit anderen Ziehungen zu finden.
- **Ziel**: Herausfinden, welche Zahlen bei den jeweiligen Ziehungen getroffen wurden. Dabei werden Ziehungen am selben Tag nicht verglichen.
- **Ergebnis**: Die Ergebnisse, einschließlich der Anzahl der Treffer und der spezifischen Treffernummern, werden in zwei Dateien gespeichert: "10-9_CheckNumbers.csv" für eine kompakte Ansicht und "10-9_CheckNumbers_z120.csv" für eine detaillierte Ansicht, in der jede Trefferzahl in einer eigenen Spalte von z1 bis z20 aufgeführt wird.

### Schritt 6: Zusammenführen der Daten und Speichern
- **Vorgang**: Die gefilterten Daten aus "10-9_KGDaten_gefiltert.csv" und die detaillierten Ergebnisse aus "10-9_CheckNumbers_z120.csv" werden zusammengeführt.
- **Ziel**: Eine kombinierte Ansicht erstellen, die zeigt, welche Gewinne an welchem Datum erzielt wurden und welche Zahlen dabei getroffen wurden.
- **Ergebnis**: Die zusammengeführten Daten werden in der Datei "10-9_Liste_GK1_Treffer.csv" gespeichert.

### Abschluss des Prozesses
- **Vorgang**: Die finale CSV-Datei "10-9_Liste_GK1_Treffer.csv" wird eingelesen und das Datumsformat wird aktualisiert.
- **Ergebnis**: Die aktualisierte Datei wird gespeichert und der Prozess wird als erfolgreich abgeschlossen gemeldet.

Dieser dokumentierte Prozess stellt sicher, dass die Datenflüsse klar und die Ergebnisse jeder Phase des Prozesses nachvollziehbar sind. Es hilft dabei, die Datenaufbereitung und Analyse transparent zu gestalten, was für eine effektive Dokumentation und zukünftige Überprüfungen unerlässlich ist.