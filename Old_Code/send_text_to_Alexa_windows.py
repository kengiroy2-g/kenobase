import urllib.parse
import requests

Imput_file= 'C:\\Users\Admin1\\Documents\\CodeProjekt\\Text_to_Alexa\\text2.txt'
Output_file= 'C:\\Users\\Admin1\\Documents\\CodeProjekt\\Text_to_Alexa\\text3.txt'

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

    # Öffne die Eingabedatei und erstelle eine Ausgabedatei
    with open(Imput_file, "r", encoding="utf-8") as f, open(Output_file, "w", encoding="utf-8") as file:
        # Füge die erste Zeile zur Ausgabedatei hinzu
        file.write('<emphasis level="moderate">\n')
        
        # Schreibe jede Zeile der Eingabedatei in die Ausgabedatei und entferne überflüssige Leerzeichen
        for line in f:
            file.write(line.strip() + '\n')
        
        # Füge die letzte Zeile zur Ausgabedatei hinzu
        file.write("</emphasis>\n")

    # Öffne die Ausgabedatei und lese alle Zeilen
    with open('..\\text3.txt', "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Verbinde die Zeilen zu einem einzigen Text
    text = (' ').join(lines)

    # Rufe die Funktion send_text_to_tts mit den definierten Parametern auf
    send_text_to_tts(text, id, hash)
