
import codecs
import re
import requests
import urllib.parse
import subprocess

def insert_break_after_n_words(text, n=4):
    words = text.split()
    word_count = 0
    new_words = []

    for word in words:
        new_words.append(word)
        if not any(satzzeichen[c] in word for c in satzzeichen):
            word_count += 1
        else:
            word_count = 0
        if word_count == n:
            new_words.append('<break time="6s"/>')
            word_count = 0

    return ' '.join(new_words)

def remove_quotes(path):
    return path.replace('"', '')

""" input_file= 'C:\\Users\\admin1\\Desktop\\Alexa_Diktat\\input.txt'
output_file= 'C:\\Users\\admin1\\Desktop\\Alexa_Diktat\\output.txt' """
# Benutzer nach den Dateipfaden für Input- und Output-Datei fragen
input_file = input("Bitte geben Sie den Pfad für die Input-Datei ein: ")
output_file = input("Bitte geben Sie den Pfad für die Output-Datei ein: ")

# Anführungszeichen aus den Dateipfaden entfernen
input_file = remove_quotes(input_file)
output_file = remove_quotes(output_file)

# Der ursprüngliche Text wird gelesen
with codecs.open(input_file, "r", encoding="utf-8") as f:
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
text1 = insert_break_after_n_words(text1)
text1liste = text1.split('.')
# Ausgabe des verarbeiteten Textes
#print(text1liste)
with codecs.open(output_file, "w",encoding="utf-8") as file, open(input_file, "r", encoding="utf-8") as f:
    for linos in f:
        file.write(linos.strip() + '\n')
    file.write('<emphasis level="moderate">\n')
    file.write('ENDE<break time="6s"/>\n')
    for lino in text1liste:
        file.write(lino.strip() + '\n')
        file.write(lino.strip() + '\n')
    file.write("</emphasis>\n")

# Anzahl der Zeichen in der Input-Datei
with codecs.open(input_file, "r", encoding="utf-8") as f:
    input_text = f.read()
    input_char_count = len(input_text)
    print(f"Anzahl der Zeichen in der Input-Datei: {input_char_count}")

# Anzahl der Zeichen in der Output-Datei
with codecs.open(output_file, "r", encoding="utf-8") as f:
    output_text = f.read()
    output_char_count = len(output_text)
    print(f"Anzahl der Zeichen in der Output-Datei: {output_char_count}")
    
    
'''def cut_text(file, word):
    with codecs.open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with codecs.open("cut_" + file, "w", encoding="utf-8") as f:
        for line in lines:
            if word in line:
                f.write(line.strip() + "\n")

cut_text("text1.txt", ".")
 '''



# Definiere die Funktion send_text_to_tts, die einen Text, eine ID und einen Hash als Parameter akzeptiert
def send_text_to_tts(text, id, hash):
    # Basis-URL für die API
    base_url = "https://esp8266-server.de/alexa/TextVorlesen/get/"
    
    # URL-kodiere den Text
    encoded_text = urllib.parse.quote(text, safe='')

    # Füge die Parameter zur Basis-URL hinzu
    url = f"{base_url}?id={id}&hash={hash}&SendeText={encoded_text}"
    
    # Sende den GET-Request und speichere die Antwort
    response = requests.get(url)

    # Überprüfe den Statuscode der Antwort und gib eine entsprechende Nachricht aus
    if response.status_code == 200:
        print("Text erfolgreich gesendet!")
    else:
        print(f"Fehler beim Senden des Textes. HTTP-Statuscode: {response.status_code}")

# Hauptteil des Skripts
if __name__ == "__main__":
    # Definiere die id, den hash und den zu sendenden Text
    id = 2049
    hash = "0c280b86daa67c26e2b347d21042d3a9"
    with codecs.open(output_file, "r", encoding="utf-8") as f:
        liness = f.readlines()
    text = (' ').join(liness)

    # Rufe die Funktion send_text_to_tts mit den definierten Parametern auf
    send_text_to_tts(text, id, hash)
# Öffne die Output-Datei mit dem Standardprogramm von Windows
subprocess.run(["start", output_file], shell=True, check=True)
input("Drücken Sie eine Taste, um fortzufahren...")
