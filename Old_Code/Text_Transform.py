
import codecs
import re

# Der ursprüngliche Text
text = "Anna schreibt einen Brief an ihre Freundin Linda. Liebe Linda, nun bin ich schon seit einer Woche am Meer. Es wird höchste Zeit, dass ich dir einen Gruß sende. Hier ist es wunderschön. Jeden Tag verbringen wir viele Stunden am Strand. Ich hoffe, dass du dich nicht zu sehr langweilst. Wie ist das Wetter bei euch? Gehst du mit deinen Eltern wieder ins Bad? Nun muss ich dir noch von einer großen Überraschung berichten. Als ich gestern Vormittag in der Ostsee tauchen war, stieß ich mit einer Frau zusammen. Ich war sehr erschrocken und bat sie um Entschuldigung. Plötzlich erkannte ich sie. Weißt du, wer es war? Es war unsere Schulleiterin. Sie war genauso überrascht wie ich und rief: „Anna, wie kommst du denn hierher?\" Stell dir vor, sie wohnt hier nur zwei Häuser weiter! Schreib mir, was es bei dir Neues gibt! Viele Grüße von deiner Anna"

# Erstelle eine Liste aller Satzzeichen in der deutschen Sprache als Tupel
satzzeichen = {'.': ' Punkt', ',': ' Komma', ';': ' Semikolon', ':': ' Doppelpunkt', '!': ' Ausrufezeichen', '?': ' Fragezeichen', '-': ' Bindestrich', '–': ' Gedankenstrich', '„': ' Anführungszeichen unten', '“': ' Anführungszeichen oben', '‘': ' Apostroph links', '’': ' Apostroph rechts', '(': ' Runde Klammer auf', ')': ' Runde Klammer zu', '[': ' Eckige Klammer auf', ']': ' Eckige Klammer zu', '{': ' Geschweifte Klammer auf', '}': ' Geschweifte Klammer zu', '/': ' Schrägstrich', '\\': ' Umgekehrter Schrägstrich', '@': ' At-Zeichen', '#': ' Hashtag', '$': ' Dollarzeichen', '%': ' Prozentzeichen', '^': ' Hochgestelltes Zeichen', '&': ' Und-Zeichen', '*': ' Stern', '+': ' Pluszeichen', '=': ' Gleichheitszeichen', '<': ' Kleiner als', '>': ' Größer als', '|': ' Senkrechter Strich', '~': ' Tilde', '`': ' Gravis'}

# Suchen und Ersetzen von Satzzeichen durch ihren Namen in Klammern
text1 = text
for zeichen in satzzeichen:
    text1 = re.sub(re.escape(zeichen), satzzeichen[zeichen], text1)
for zeichen in satzzeichen:
    text1 = re.sub(re.escape(satzzeichen[zeichen]), satzzeichen[zeichen] + '<break time="8s"/>', text1)

# Ausgabe des verarbeiteten Textes
print(text1)
