---
Level: 4
---


# **[[MOCs/🌍🏠Home_|🏠]]**

🔙 MOCs: [[_Root/Projekte & Dokumentation|Projekte & Dokumentation]]

⬆️[[_Root/Projekt_Keno_zahlen_Suche|Projekt_Keno_zahlen_Suche]]
⬆️[[_Root/Logik & Python Programme|Logik & Python Programme]]


---------------------------------------
1. **Vollständige Erscheinung einer Kombination identifizieren:**
    
    - Der Code soll jede Ziehung im Archiv durchlaufen und prüfen, ob eine Kombination von Zahlen vollständig erscheint.
    - Bei jeder vollständigen Erscheinung einer Kombination wird eine separate Zählungsoperation initiiert.
2. **Zählungsoperationen:**
	(. **Überprüfung des Erscheinungsdatums:** Für jede Ziehung wird geprüft, ob das Datum nach dem Erscheinungsdatum der Kombination liegt. Wenn das Erscheinungsdatum dem Standarddatum entspricht oder das Ziehungsdatum davor liegt, wird die Ziehung in die Zählung einbezogen.**Zählung der Ziehungen:** Für jede berücksichtigte Ziehung wird `durchgelaufene_ziehungen` um eins erhöht. **Ermittlung der Übereinstimmung:** Es wird geprüft, welche Zahlen der Kombination in der aktuellen Ziehung enthalten sind. Diese Übereinstimmungen werden zur Zählung hinzugefügt.**Gruppierung von Duos, Trios und Quatros:** Basierend auf der Anzahl der übereinstimmenden Zahlen werden Duos, Trios oder Quatros gebildet und gespeichert, wobei eine Priorisierung von Quatros vor Trios vor Duos erfolgt. **Beendigung der Zählung:** Die Zählung endet, sobald jede Zahl der Kombination mindestens einmal erschienen ist. **Erstellung von Ergebnisstrings:** Die Zählungsergebnisse und Gruppierungen werden in String-Formate umgewandelt und zusammen mit anderen Informationen zur Kombination in einer Ergebnisliste gespeichert.Diese Zählungsoperation wird für jede Kombination durchgeführt und ermöglicht es, die Häufigkeit und gemeinsames Auftreten der Zahlen in der Kombination nach ihrem Erscheinungsdatum zu analysieren.
)
    - Die Zählung beginnt direkt nach dem Datum der vollständigen Erscheinung der Kombination (das Datum selbst ist ausgeschlossen).
    - Die Zählung wird durchgeführt, bis jede Zahl der Kombination mindestens einmal in den nachfolgenden Ziehungen erschienen ist.
    - Diese Zählung wird für jede vollständige Erscheinung der Kombination im Archiv separat durchgeführt.
3. **Standarddatum-Logik:**
    
    - Wenn eine Kombination im gesamten Archiv nicht vollständig erscheint, wird das Standarddatum (`standard_datum`) verwendet.
    - Für Kombinationen, die nicht vollständig erscheinen, wird die Zählung vom Anfang des Archivs durchgeführt.
4. **Speichern der Ergebnisse:**
    
    - Für jede durchgeführte Zählungsoperation werden die Ergebnisse gespeichert, einschließlich:
        - Die Kombination.
        - Das Datum der vollständigen Erscheinung oder das Standarddatum, falls die Kombination nie vollständig erscheint.
        - Die Anzahl der durchgelaufenen Ziehungen während der Zählungsoperation.
        - Die endgültige Zählung für jede Zahl in der Kombination.
        - Die ermittelten Duos, Trios und Quatros basierend auf den gemeinsamen Erscheinungen der Zahlen in den Ziehungen während der Zählungsoperation.
5. **Parallelverarbeitung:**
    
    - Der Code soll die Prüfung und Zählung der Kombinationen parallel durchführen, um die Effizienz zu steigern, besonders bei einer großen Anzahl von Kombinationen.






------------------------------------------

unten findest du eine tabelle mit ziehungen. wir die berechnungen von zählung, counter_string, duos_string, trios_string, quatro_string durchführen  für die kombi {3,9,10,46,48,17 } erschienen am 02.07.2022.
- das erscheinungsdatum wird nicht berücksichtig, es wird immer die älsteten Einträge nach dem erscheinungsdatum für die zählungsberücksichtigt.
- sage mir ob du die anforderung verstanden ahst vor der durchführung
P.s zähle nicht falsch, es wird immer die älsteten Einträge nach dem erscheinungsdatum für die zählung berücksichtigt. also ab 01.07.2022 , 30.06.2022,...bis 25.06.2022.
datum ist absteigend sortiert, 02.07.2022 wird nicht berücksichtig 




02.07.2022	20	56	46	10	9	53	70	36	3	12	52	43	69	14	48	59	19	51	17	45
01.07.2022	68	15	2	59	4	27	49	20	45	29	61	51	43	5	32	56	34	12	17	47
30.06.2022	44	52	21	8	17	5	64	55	34	7	14	56	57	61	16	48	62	1	67	25
29.06.2022	61	47	48	20	28	54	7	2	39	31	23	55	42	45	37	66	29	10	21	65
28.06.2022	64	51	52	23	50	3	39	36	28	16	46	13	62	42	66	53	56	6	58	25
27.06.2022	50	38	6	69	10	20	27	49	60	59	9	44	41	23	7	57	63	55	36	12
26.06.2022	48	63	59	70	2	24	11	5	56	26	68	34	14	29	19	38	22	52	20	4
25.06.2022	3	69	63	6	52	66	50	28	41	32	17	39	60	22	64	56	9	40	18	5
 

1. **Zählung (`zählung`)**: Wir würden durch die Datensätze gehen, die **vor dem Erscheinungsdatum** liegen (also beginnend mit dem 01.07.2022 und weiter rückwärts), und zählen, wie oft jede Zahl in der Kombination vorkommt. die zahlen werden dargestellt nach der reihenfolge wie sie in der zeihung vorkommen, nicht die reihenfolge der kombinationen z.B ,"{6: 3, 10: 4, 46: 3, 17: 5, 29: 1, 30: 3}",
    
2. **Counter String (`counter_string`)**: Dies ist eine Zeichenkette, die die Ergebnisse von "Zählung " getrennt durch Kommas, darstellt. z.b "3,4,3,5,1,3",
    
3. **Duos String (`duos_string`)**: Wir würden jedes Paar (Duo) von Zahlen in der Kombination suchen, das gleichzeitig  in einem Datensatz vorkommt. Jedes Mal, wenn ein Paar gefunden wird, wird es zu einem Set hinzugefügt, um Duplikate zu vermeiden. Am Ende wird ein String erstellt, der alle einzigartigen Paare enthält, getrennt
    
4. **Trios String (`trios_string`)**: Ähnlich wie bei den Duos, nur dass hier Dreiergruppen von Zahlen gesucht werden, die gleichzeitig vorkommen. wenn ein Trio erscheint,werden die duos die bereit elemente von diese trios sind nicht mitgezählt für diese ziehung
    
5. **Quatros String (`quatro_string`)**: Ähnlich wie bei den Trios,  Gruppen von vier Zahlen gesucht, die gleichzeitig  in einem Datensatz vorkommen. wenn ein quatros erscheint,werden die duos und trios  die bereit elemente von diese quatross sind nicht mitgezählt für diese ziehung























Um die Aufgabe zu erfüllen, die Logik für die Zählung und Gruppierung von Zahlenkombinationen zu prüfen, insbesondere für die Kombination {3,9,10,46,48,17}, die am 02.07.2022 erschienen ist, würden wir folgendes tun:

1. **Zählung (`zählung`)**: Wir würden durch die Datensätze gehen, die **vor dem Erscheinungsdatum** liegen (also beginnend mit dem 01.07.2022 und weiter rückwärts), und zählen, wie oft jede Zahl in der Kombination vorkommt. Hierbei wird jeder Datensatz betrachtet und für jede Zahl in der Kombination überprüft, ob sie in dem Datensatz vorkommt. Die Zählung wird in einem Dictionary gespeichert, wobei die Schlüssel die Zahlen der Kombination sind und die Werte die jeweiligen Häufigkeiten.
    
2. **Counter String (`counter_string`)**: Dies ist eine Zeichenkette, die die Zählungen für jede Zahl in der Kombination, getrennt durch Kommas, darstellt. Beispielsweise würde `"1,2,1,0,3,1"` bedeuten, dass die erste Zahl einmal, die zweite Zahl zweimal, die dritte Zahl einmal, die vierte Zahl nullmal, die fünfte Zahl dreimal und die sechste Zahl einmal vorkam.
    
3. **Duos String (`duos_string`)**: Wir würden jedes Paar (Duo) von Zahlen in der Kombination suchen, das zusammen in einem Datensatz vorkommt. Jedes Mal, wenn ein Paar gefunden wird, wird es zu einem Set hinzugefügt, um Duplikate zu vermeiden. Am Ende wird ein String erstellt, der alle einzigartigen Paare enthält, getrennt durch Semikolons.
    
4. **Trios String (`trios_string`)**: Ähnlich wie bei den Duos, nur dass hier Dreiergruppen von Zahlen gesucht werden, die zusammen vorkommen. Auch diese werden in einem Set gespeichert, um Einzigartigkeit zu gewährleisten, und schließlich zu einem String zusammengefügt.
    
5. **Quatros String (`quatro_string`)**: Hier werden Gruppen von vier Zahlen gesucht, die zusammen in einem Datensatz vorkommen. Jede gefundene Gruppe wird zu einem Set hinzugefügt und schließlich zu einem String konvertiert.
    

Für die Berechnung würden wir die genannten Schritte programmatisch durchführen, wobei die Sortierung der Daten und das Ausschließen des Erscheinungsdatums der Kombination berücksichtigt werden muss.
----------------------






das datum wird nun aktualisiert ,aber es gibt ein problem .die erzeugung von 'Anzahl der durchgelaufenen Ziehungen', 'Zählungen', 'Counter',  'Duos', 'Trios', 'Quatros'  lauf nicht mehr richtig. die Zählung von "durchgelaufene_ziehungen", "zählung", "counter_string", "Duos", "Trios" und "Quatros" soll stoppen, sobald alle Zahlen der Kombination mindestens einmal erschienen sind.Die Aktualisierung des Datums sollte nur erfolgen, wenn die gesamte Kombination zum ersten Mal erscheint. gibt es die möglichkeit das berechnen und aktualisierung von datum als erste durchzuführen und danach die operationen für 'Anzahl der durchgelaufenen Ziehungen', 'Zählungen', 'Counter',  'Duos', 'Trios', 'Quatros' die ausgabe von quatro wird nicht richtig dargestellt weil mit semikolonne ";" getrennt (sie unten die letzte zahlen) :

"(3, 6, 10, 14, 46, 48)",3,"{3: 1, 6: 2, 10: 2, 14: 1, 46: 1, 48: 2}","1,2,2,1,1,2",06.02.2017,"(48, 46)","(10, 6, 14)",48;10;3;6



1. **Import von Bibliotheken:**
    
    - `pandas`: Für Datenmanipulation und -analyse.
    - `itertools.combinations`: Zum Generieren aller möglichen Kombinationen von Zahlen.
    - `os`: Für Betriebssystem-interaktion, z.B. zur Überprüfung von Dateipfaden.
    - `tqdm`: Für die Fortschrittsanzeige bei Schleifendurchläufen.
    - `concurrent.futures`: Für die parallele Ausführung von Aufgaben.
    - `signal`, `sys`: Für die Signalbehandlung und Systemoperationen, insbesondere zur sauberen Beendigung des Programms.
2. **Globale Variablen und Funktionen zur Datenverwaltung:**
    
    - Zustände und zwischen Ergebnisse während der Programmausführung zu sollen gespeichert und zu verwaltet werden.
    - Funktionen sollen  Fortschritte und Ergebnisse speichern bzw.  laden, um die Resilienz des Programms gegen Unterbrechungen zu erhöhen.


3. **Generieren  von Zahlenpool und  Kombinationen:**
	- eine Funktion filtert einer CSV-Datei "keno_Archiv.csv" nach Datum, liest Zahlen aus dieser CSV-Datei(Die Kopfzeile wird übersprungen) und führt eine Datenextrahierung und Verarbeitung um einzigartige Zahlen zu extrahieren, um Duplikate zu eliminieren.
		- Für jede Zeile werden die Werte von der zweiten bis zur einundzwanzigsten Spalte (Index 1 bis 20) betrachtet, unter der Annahme, dass diese die relevanten Daten enthalten.
		- Jeder Wert wird überprüft: Wenn er nicht leer ist, wird versucht, ihn in einen Integer umzuwandeln.
		- Jede umgewandelte Zahl wird zum Set hinzugefügt. Das Set aktualisiert automatisch nur mit einzigartigen Werten.
		
		- Das Set  wird in eine sortierte Liste umgewandelt und am terminal  ausgegeben, und die einzigartigen Zahlen werden in Zahlenpool gespeichert.

	- Eine Funktion generiert alle möglichen 6-Zahlen-Kombinationen aus dem vorgegebenen Zahlenpool, die eine bestimmte Summe (`ziel_summen`) haben, und gebe die Ergebnisse zurück 
	  


5. **Prüfung gegen ein keno_Archiv.csv:**

-  Eine Funktion Überprüft jede 6-Zahlen-Kombination in einem Batch gegen eine  Archiv von historischen keno Ziehungen, um zu sehen ob sie dort vorkommen .
- behalten werden nur 6-Zahlen-Kombination die höchsten nur einmal in ganze keno_Archiv.csv vorkommen. 
  nach jeder Batch sollen die Ergebnisse zwischengespeichert in eine "Pruefung_erscheinung" CSV-Datei mit der Strucktur"Datum, Kombination, Anzahl_erscheinung_Archiv "
- Die Aufgabe sollen nach einer  Parallelverarbeitung, durchgeführt werden.

6. **Zähler für jeder Kombination:** 
	Die Fuktion filtert die CSV-Datei "keno_Archiv.csv" nach datum 
	jeder 6-Zahlen-Kombination in "Pruefung_erscheinung" CSV-Datei  wird gegen die Ziehungen der gefilterten CSV-Datei "keno_Archiv.csv" geprüft um zu ermitteln, wie oft jede Zahl in die geprüfte 6-Zahlen-Kombination vorkommt bis Alle Zahlen mindesten ein mal  erschienen sind.
	- Durchläuft jede Ziehung ab das Früherste  Datum in CSV-Datei und aktualisiert den Zähler für jede Zahl, die in der Ziehungen vorkommt.
	- Beendet die Schleife, sobald jede Zahl in der  6-Zahlen-Kombination mindestens einmal erschienen ist.
	- Zählungsergebnisse werden in eine Final_CSV-Datei gespeichert werden mit den Spalten "Datum,  6-Zahlen-Kombination, Anzahl_erscheinung_Archiv Anzahl der durchgelaufene Ziehungen, Zählungen (wobei  die Zahlen und derer counter in einem string  wie folgt gespeichert werden sollen [34: 1],[3: 2],[7: 3],[41: 1],[13: 1],[26: 1],[30: 3]) , Counter (hier wird in einem string  nur die counter gespeichert)"
