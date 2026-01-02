
import codecs
import re

# Der ursprüngliche Text wird gelesen
with codecs.open('..\\text.txt', "r", encoding="utf-8") as f:
        liness = f.readlines()
text = (' ').join(liness)
#print (text)

# Erstelle eine Liste aller Satzzeichen in der deutschen Sprache als Tupel
satzzeichen = {'.': ' Punkt', ',': ' Komma', ';': ' Semikolon', ':': ' Doppelpunkt', '!': ' Ausrufezeichen', '?': ' Fragezeichen', '-': ' Bindestrich', '–': ' Gedankenstrich', '„': ' Anführungszeichen unten', '“': ' Anführungszeichen oben', '‘': ' Apostroph links', '’': ' Apostroph rechts', '(': ' Runde Klammer auf', ')': ' Runde Klammer zu', '[': ' Eckige Klammer auf', ']': ' Eckige Klammer zu', '{': ' Geschweifte Klammer auf', '}': ' Geschweifte Klammer zu', '/': ' Schrägstrich', '\\': ' Umgekehrter Schrägstrich', '@': ' At-Zeichen', '#': ' Hashtag', '$': ' Dollarzeichen', '%': ' Prozentzeichen', '^': ' Hochgestelltes Zeichen', '&': ' Und-Zeichen', '*': ' Stern', '+': ' Pluszeichen', '=': ' Gleichheitszeichen', '<': ' Kleiner als', '>': ' Größer als', '|': ' Senkrechter Strich', '~': ' Tilde', '`': ' Gravis'}

# Suchen und Ersetzen von Satzzeichen durch ihren Namen in Klammern
c = 6
text1 = text
for zeichen in satzzeichen:
    text1 = re.sub(re.escape(zeichen), satzzeichen[zeichen], text1)
for zeichen in satzzeichen:
    if c < 7 and satzzeichen[zeichen] == ' Punkt':
        text1 = re.sub(re.escape(satzzeichen[zeichen]),'<break time="2s"/>' + satzzeichen[zeichen] + '<break time="'+ str(c) + 's"/>.', text1)
    elif c < 7 :
        text1 = re.sub(re.escape(satzzeichen[zeichen]),'<break time="2s"/>' + satzzeichen[zeichen] + '<break time="'+ str(c) + 's"/>', text1)
        c += 1
    elif c == 7 and satzzeichen[zeichen] != ' Punkt':
        text1 = re.sub(re.escape(satzzeichen[zeichen]), '<break time="2s"/>' + satzzeichen[zeichen] + '<break time="'+ str(c) + 's"/>.', text1)
        c = 6

text1liste = text1.split('.')
# Ausgabe des verarbeiteten Textes
print(text1liste)
with codecs.open('..\\text1.txt', "w",encoding="utf-8") as file:
    for lino in text1liste:
        file.write(lino.strip() + '\n')
        file.write(lino.strip() + '\n')

def cut_text(file, word):
    with codecs.open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with codecs.open("cut_" + file, "w", encoding="utf-8") as f:
        for line in lines:
            if word in line:
                f.write(line.strip() + "\n")

cut_text("text1.txt", ".")
