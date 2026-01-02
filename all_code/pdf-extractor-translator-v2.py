import PyPDF2
import openai
import time
import re

# Setze deinen OpenAI API-Schlüssel
openai.api_key = "REDACTED_API_KEY"

def extract_pages(pdf_path):
    """
    Liest das PDF und gibt eine Liste von Strings zurück,
    wobei jeder String den Text einer Seite repräsentiert.
    """
    pages_text = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
    return pages_text

###############################################################################
# 2) KI-Aufruf zur ersten 'Reinigungs'-Schritt (Seitenzahlen, Fußzeilen etc. entfernen)
###############################################################################
def clean_text_for_tts(text, model_name="gpt-4o-mini"):
    """
    Ruft das KI-Modell auf, um störende Elemente (Seitenzahlen, überflüssige
    Markdown-Überschriften, Kopf-/Fußzeilen usw.) zu entfernen.
    """
    system_message = (
        "Du bist ein Experte für Textaufbereitung und TTS-Optimierung. "
        "Bitte entferne im folgenden Text alle Seitenzahlen, unnötigen Überschriften, "
        "Datumszeilen, URLs, Markdown-Formatierung,wiederholte inhalte und alles, was beim Vorlesen stören könnte. "
        "Behalte jedoch die inhaltliche Struktur (Absätze), soweit sie sinnvoll ist."
        "wandle Tabellen in Listen um, falls vorhanden."
    )

    user_prompt = f"Hier ist der zu reinigende Text:\n\n{text}"
    
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=16384
        )
        cleaned_text = response.choices[0].message.content.strip()
        return cleaned_text
    except Exception as e:
        print(f"Fehler beim Reinigen des Textes: {e}")
        return text  # Fallback

###############################################################################
# 3) (Optional) Übersetzung des Textes
###############################################################################
def translate_text(text, target_language="Französisch", model_name="gpt-4o-mini"):
    """
    Übersetzt den Text in die gewünschte Sprache mithilfe des KI-Modells.
    Hinweis: Falls du keine Übersetzung brauchst, kannst du diese Funktion einfach weglassen
    oder in 'process_page()' entsprechend anpassen.
    """
    system_message = (
        "Du bist ein professioneller Übersetzer. "
        "Bitte übersetze den folgenden Text möglichst sinngenau und flüssig."
    )
    user_prompt = f"Übersetze den folgenden Text ins {target_language}:\n\n{text}"
    
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=16384
        )
        translated_text = response.choices[0].message.content.strip()
        return translated_text
    except Exception as e:
        print(f"Fehler bei der Übersetzung: {e}")
        return text  # Fallback

###############################################################################
# 4) (Optional) SSML-Generator
###############################################################################
def generate_ssml(text, model_name="gpt-4o-mini"):
    """
    Erzeugt aus dem bereinigten/flüssigen Fließtext eine SSML-Version mit Pausen,
    Hervorhebungen etc., die Amazon Polly besser vorlesen kann.

    Wichtig: Wenn du SSML nicht benötigst, kannst du diese Funktion weglassen.
    """
    system_message = (
        "Du bist ein Assistent, der aus Texten ein Hörbuch-Manuskript im SSML-Format erstellt. "
        "Füge sinnvolle <break time=\"500ms\"/>-Pausen ein, entferne überflüssige Formatierungen und "
        "markiere Überschriften oder wichtige Begriffe. Achte darauf, dass der Text anschließend "
        "korrektes SSML ist und in <speak>...</speak> eingebettet wird."
    )
    user_prompt = f"Hier ist der Text, der als SSML aufbereitet werden soll:\n\n{text}"
    
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=16384
        )
        ssml_text = response.choices[0].message.content.strip()
        return ssml_text
    except Exception as e:
        print(f"Fehler beim Erzeugen von SSML: {e}")
        return text  # Fallback

###############################################################################
# 5) Prozessfunktion für eine Seite (oder einen Textblock)
###############################################################################
def process_text_block(
    text_block,
    do_clean=True,
    do_translate=True,
    target_language="Französisch",
    do_ssml=True,
    model_name="gpt-4o-mini"
):
    """
    Verarbeitet einen einzelnen Textblock (z. B. eine PDF-Seite oder
    mehrere zusammengefügte Seiten).

    Parameter:
    - do_clean:   True, wenn wir den Text zuerst "reinigen" (Seitenzahlen entfernen etc.).
    - do_translate: True, wenn der Text noch übersetzt werden soll.
    - target_language: Sprache, in die übersetzt werden soll (z. B. "Französisch").
    - do_ssml:    True, wenn wir danach noch eine SSML-Version generieren wollen.
    - model_name: Welches KI-Modell verwendet werden soll.
    """
    # 1) Aufbereiten / Reinigen
    if do_clean:
        text_block = clean_text_for_tts(text_block, model_name=model_name)
    
    # 2) Optional: Übersetzen
    if do_translate:
        text_block = translate_text(text_block, target_language=target_language, model_name=model_name)
    
    # 3) Optional: SSML generieren
    if do_ssml:
        text_block = generate_ssml(text_block, model_name=model_name)
    
    return text_block

###############################################################################
# 6) Hauptfunktion
###############################################################################
def main():
    pdf_path = r"C:\\Users\\Admin1\\OneDrive\\Dokumente\\00_Learning\\00_Ghislain\\00_BOOKS\\Internet_Book.pdf"
    output_file = r"C:\\Users\\Admin1\\OneDrive\\Dokumente\\00_Learning\\00_Ghislain\\00_BOOKS\\Internet_Book_processed.txt"
    
    # Seitenbereiche definieren
    start_page = 
    end_page = 404

    # PDF auslesen
    pages = extract_pages(pdf_path)
    total_pages = len(pages)
    print(f"Es wurden insgesamt {total_pages} Seiten gefunden.")

    # Gültigkeitscheck
    if start_page < 1 or start_page > total_pages:
        print("Der Startwert ist ungültig.")
        return
    if end_page is not None and (end_page < start_page or end_page > total_pages):
        print("Der Endwert ist ungültig.")
        return

    # Entsprechenden Seitenbereich herausnehmen
    pages_to_process = pages[start_page - 1:end_page] if end_page else pages[start_page - 1:]

    # Erstelle die Ausgabedatei
    with open(output_file, 'w', encoding='utf-8') as out_file:
        current_page = start_page
        for page_text in pages_to_process:
            print(f"Verarbeite Seite {current_page} ...")

            # Seiten mit zu wenig Inhalt überspringen (optional)
            if len(page_text.strip()) < 30:  # < 30 Zeichen => meist leere/sehr kurze Seite
                print(f"Seite {current_page} wird übersprungen, da sie zu wenig Inhalt hat.")
                current_page += 1
                continue

            # Hier kannst du steuern, ob übersetzt oder SSML generiert werden soll
            # (z. B. do_translate=False, do_ssml=False, je nach Bedarf)
            processed_text = process_text_block(
                text_block=page_text,
                do_clean=True,           # True => Seitenzahlen, Kopf-/Fußzeilen etc. entfernen
                do_translate=True,      # Falls du es übersetzen willst, hier True setzen
                target_language="Französisch", 
                do_ssml=True,           # Falls du SSML haben willst, hier True setzen
                model_name="gpt-4o-mini" # Dein gewünschtes Modell
            )

            if processed_text is not None:
                # Du kannst hier natürlich auch frei entscheiden, ob du erneut die Seitenzahl
                # ausgeben willst (z. B. "Seite X"), oder gar nicht.
                out_file.write(f"--- Verarbeitete Seite {current_page} ---\n")
                out_file.write(processed_text + "\n\n")
            else:
                out_file.write(f"--- Seite {current_page} ---\n")
                out_file.write("Fehler beim Verarbeiten dieser Seite.\n\n")

            current_page += 1
            # Kurze Pause, um Rate Limits zu vermeiden (je nach Bedarf)
            time.sleep(1)

    print(f"Verarbeitung abgeschlossen. Ergebnis wurde in '{output_file}' gespeichert.")

###############################################################################
# Code ausführen
###############################################################################
if __name__ == "__main__":
    main()
