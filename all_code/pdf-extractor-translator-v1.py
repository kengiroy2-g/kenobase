import openai
import time
import PyPDF2
import re
import os



# Setze deinen OpenAI API-Schlüssel (via Umgebungsvariable!)
openai.api_key = os.environ.get("OPENAI_API_KEY", "YOUR_KEY_HERE")


def extract_pages(pdf_path):
    """
    Liest das PDF und gibt eine Liste von Seiten-Texten zurück.
    """
    pages_text = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
    return pages_text

def restructure_text(text, prompt_instruction=None):
    """
    Verwendet einen KI-Agenten, um den Text für TTS optimal aufzubereiten.
    Standardmäßig werden unnötige Kopf-/Fußzeilen entfernt, Tabellen in Listen umgewandelt 
    und Wiederholungen eliminiert.
    """
    if prompt_instruction is None:
        prompt_instruction = (
            "Strukturiere den folgenden Text so um, dass er für eine TTS-Wiedergabe optimal "
            "lesbar ist. Entferne unnötige Kopf- und Fußzeilen, wiederholende Elemente und "
            "wandle Tabellen in Listen um, falls vorhanden."
        )
    prompt = f"{prompt_instruction}\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein Experte für Textaufbereitung und TTS-Optimierung."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=16384
        )
        restructured_text = response.choices[0].message.content.strip()
        return restructured_text
    except Exception as e:
        print(f"Fehler beim Umstrukturieren: {e}")
        return None

def translate_text(text, target_language="Französisch"):
    """
    Übersetzt den Text in die gewünschte Sprache mithilfe eines KI-Agenten.
    """
    prompt = f"Übersetze den folgenden Text ins {target_language}:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein professioneller Übersetzer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=16384
        )
        translated_text = response.choices[0].message.content.strip()
        return translated_text
    except Exception as e:
        print(f"Fehler bei der Übersetzung: {e}")
        return None

def process_page(page_text, restructure_before_translation=True):
    """
    Verarbeitet eine Seite, indem sie entweder vor oder nach der Übersetzung umstrukturiert wird.
    
    Bei restructure_before_translation=True wird zuerst der Originaltext umstrukturiert 
    und anschließend übersetzt. Andernfalls wird erst übersetzt und dann der übersetzte Text 
    umstrukturiert.
    """
    if restructure_before_translation:
        # Zuerst umstrukturieren, dann übersetzen
        restructured = restructure_text(page_text)
        if restructured is None:
            restructured = page_text  # Fallback, falls der Agent fehlschlägt
        final_text = translate_text(restructured)
    else:
        # Zuerst übersetzen, dann umstrukturieren
        translation = translate_text(page_text)
        if translation is None:
            translation = page_text  # Fallback, falls die Übersetzung fehlschlägt
        final_text = restructure_text(translation, prompt_instruction=(
            "Strukturiere den folgenden übersetzten Text so um, dass er für eine TTS-Wiedergabe optimal lesbar ist. "
            "Entferne Wiederholungen, passe die Formatierung an und strukturiere den Inhalt sinnvoll."
        ))
    return final_text

def main():
    pdf_path = "C:\\Users\\Admin1\\OneDrive\\Dokumente\\00_Learning\\00_Ghislain\\00_BOOKS\\Internet_Book.pdf"  # Pfad zur PDF-Datei
    output_file = "C:\\Users\\Admin1\\OneDrive\\Dokumente\\00_Learning\\00_Ghislain\\00_BOOKS\\Internet_Book1.txt"  # Ausgabedatei

    # Bestimme den Seitenbereich (Beispiel: von Seite 96 bis Seite 200)
    start_page = 92
    end_page = 404

    pages = extract_pages(pdf_path)
    total_pages = len(pages)
    print(f"Es wurden insgesamt {total_pages} Seiten gefunden.")

    # Überprüfe, ob der gewählte Bereich gültig ist
    if start_page < 1 or start_page > total_pages:
        print("Der Startwert ist ungültig.")
        return
    if end_page is not None and (end_page < start_page or end_page > total_pages):
        print("Der Endwert ist ungültig.")
        return

    pages_to_process = pages[start_page - 1:end_page] if end_page else pages[start_page - 1:]
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        current_page = start_page
        for page_text in pages_to_process:
            print(f"Verarbeite Seite {current_page} ...")
            # Überspringe Seiten mit zu wenig Inhalt
            if len(page_text.split()) < 10:
                print(f"Seite {current_page} wird übersprungen, da sie zu wenig Inhalt hat.")
                current_page += 1
                continue
            processed_text = process_page(page_text, restructure_before_translation=True)
            if processed_text is not None:
                out_file.write(f"--- Seite {current_page} ---\n")
                out_file.write(processed_text + "\n\n")
            else:
                out_file.write(f"--- Seite {current_page} ---\n")
                out_file.write("Fehler beim Verarbeiten dieser Seite.\n\n")
            current_page += 1
            # Kurze Pause, um Rate-Limits zu vermeiden
            time.sleep(1)
    print(f"Verarbeitung abgeschlossen. Ergebnis wurde in '{output_file}' gespeichert.")

if __name__ == "__main__":
    main()
