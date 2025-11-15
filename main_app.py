import time
import os
import sys
import re
import config
# --- MODIFICARE CHEIE ---
# Setam variabila de mediu INAINTE de a importa cv2
# Acest lucru forteaza OpenCV sa foloseasca backend-ul X11 (xcb) in loc de Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"
# --- SFARSIT MODIFICARE ---

import sensor
import cv2 
import google.generativeai as genai
import PIL.Image
from gtts import gTTS
from datetime import datetime

# --- 1. Configuratie Principala ---
# (Restul configuratiei ramane neschimbat)
# ...

# === Setari Fisiere & Foldere ===
API_KEY_FILE = "apiKey.txt"
IMAGE_FOLDER = "images"
LOG_CONTENT_FOLDER = "content_logs" 
LOG_TYPE_FILE = "typesLogs.txt"     

# === Setari Model Gemini ===
MODEL_NAME = 'gemini-2.5-flash' 

# === Setari TTS (Text-to-Speech) ===
LANGUAGE = 'ro'
TEMP_AUDIO_FILE = "temp_speech.mp3"

# === Setari Camera & UI ===
COUNTDOWN_SECONDS = 5
POS_STATE = (10, 30)
POS_COUNTDOWN = (10, 70) 
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (0, 0, 255)
THICKNESS = 2

# --- 2. Functii Utilitare (din scripturile tale) ---

def read_api_key():
    """Citeste cheia API din fisier."""
    try:
        with open(API_KEY_FILE, 'r') as f:
            api_key = f.read().strip()
        if not api_key:
            print(f"Eroare: Fisierul {API_KEY_FILE} este gol.")
            return None
        return api_key
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{API_KEY_FILE}' nu a fost gasit.")
        return None
    except Exception as e:
        print(f"Eroare la citirea fisierului API: {e}")
        return None

def redacteaza_date_personale(text):
    """
    Inlocuieste datele personale comune (Plasa de Siguranta).
    """
    print("Se verifica datele personale (plasa de siguranta)...")
    text = re.sub(r'\S+@\S+\.\S+', '(email redactat)', text)
    text = re.sub(r'(\+4|0)[ -]?(\d{3}[ -]?\d{3}[ -]?\d{3}|\d{2}[ -]?\d{3}[ -]?\d{4})', '(nr. telefon redactat)', text)
    text = re.sub(r'\b[125678]\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{6}\b', '(CNP redactat)', text)
    text = re.sub(r'\b(Str|B-dul|Aleea|Piata|Nr|Bl|Sc|Ap)\b[\. ]*[\w\d]+', '(adresa redactata)', text, flags=re.IGNORECASE)
    return text

def speak_text(text, language):
    """
    Genereaza si reda audio folosind gTTS si mpg123.
    """
    if not text or text.isspace():
        print("Nu exista continut de redat.")
        return

    try:
        print("Generez audio... (necesita internet)")
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(TEMP_AUDIO_FILE)
        
        print("Redau audio...")
        os.system(f"mpg123 -q {TEMP_AUDIO_FILE}")

    except Exception as e:
        print(f"Eroare la generarea sau redarea TTS: {e}")
        print("Verifica conexiunea la internet si daca 'mpg123' e instalat.")
    finally:
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)

# --- 3. Functii Noi (Logica principala) ---
# (Toate functiile raman neschimbate)

def ensure_dirs():
    """Creeaza folderele necesare daca nu exista."""
    for folder in [IMAGE_FOLDER, LOG_CONTENT_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Director creat: {folder}")

def get_next_capture_number():
    """Gaseste urmatorul numar X disponibil pentru imgX.jlpg si textLogX.txt"""
    img_counter = 1
    while True:
        img_path = os.path.join(IMAGE_FOLDER, f"img{img_counter}.jpg")
        log_path = os.path.join(LOG_CONTENT_FOLDER, f"textLog{img_counter}.txt")
        
        if not os.path.exists(img_path) and not os.path.exists(log_path):
            return img_counter
        img_counter += 1

def log_document_type(doc_type):
    """Adauga tipul documentului in fisierul typesLogs.txt."""
    try:
        with open(LOG_TYPE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{doc_type}\n")
        print(f"Tip document '{doc_type}' salvat in {LOG_TYPE_FILE}")
    except Exception as e:
        print(f"Eroare la scrierea in {LOG_TYPE_FILE}: {e}")



def log_document_content(content, file_path):
    """Salveaza continutul (rezumatul) in fisierul textLogX.txt specific."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Continut salvat in {file_path}")
    except Exception as e:
        print(f"Eroare la scrierea in {file_path}: {e}")

def process_image_with_gemini(model, image_path, content_log_path):
    """
    Trimite imaginea la Gemini, proceseaza raspunsul, salveaza
    si returneaza continutul pentru TTS.
    """
    print(f"Procesez imaginea: {image_path}")
    
    try:
        img = PIL.Image.open(image_path)
    except Exception as e:
        print(f"Eroare la incarcarea imaginii PIL: {e}")
        return "Eroare la incarcarea imaginii."

    prompt_text = f"""
Analizeaza aceasta imagine. Raspunsul tau trebuie sa urmeze STRICT acest format:
LINIA 1: Doar tipul documentului (ex: Factura, Aviz, Scrisoare, Email, Notite).
RESTUL LINIILOR: Un rezumat detaliat al continutului textului din imagine.

INSTRUCTIUNE IMPORTANTA PENTRU REZUMAT:
Evită cu strictețe dezvaluirea oricaror date personale, cum ar fi nume complete, adrese poștale complete, CNP-uri, numere de telefon sau adrese de email.
Menționează doar existența lor generic (de ex. "se observă o adresă de livrare", "conține un CNP", "sunt listate datele de contact ale clientului").
Concentreaza-te pe elementele principale: ce se vinde, care e mesajul principal, care sunt sumele (daca e o factura), etc.
"""

    try:
        response = model.generate_content([prompt_text, img])
        
        raspuns_text = response.text.strip()
        parti = raspuns_text.split('\n', 1) 
        
        doc_type = "Eroare Format"
        doc_content = raspuns_text 

        if len(parti) == 2:
            doc_type = parti[0].strip()
            doc_content = parti[1].strip()
            print(f"Gemini a identificat tipul: {doc_type}")
        else:
            print("EROARE: Modelul nu a returnat formatul cerut (Tip pe L1, Continut restul).")

        redacted_content = redacteaza_date_personale(doc_content)
        
        log_document_type(doc_type)
        log_document_content(redacted_content, content_log_path)

        return redacted_content 

    except Exception as e:
        print(f"Eroare la generarea raspunsului de la Gemini: {e}")
        log_document_type("Eroare API")
        log_document_content(str(e), content_log_path)
        return "A aparut o eroare la procesarea imaginii."

# --- 4. Functia Principala (Main Loop) ---
# (Functia main ramane neschimbata)

def main():
    ensure_dirs()
    
    api_key = read_api_key()
    if not api_key:
        sys.exit(1)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        print("Modelul Gemini a fost initializat.")
    except Exception as e:
        print(f"Eroare la configurarea API sau initializarea modelului: {e}")
        sys.exit(1)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Eroare: Nu s-a putut deschide camera.")
        sys.exit(1)

    print("Feed live pornit. Apasa '1' in fereastra pentru captura, 'q' pentru a iesi.")

    program_state = "ASTEPTARE"
    countdown_active = False
    countdown_end_time = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Eroare: Cadru gol.")
                break

            clean_frame = frame.copy() 
            
            if countdown_active:
                current_time = time.time()
                remaining = int(countdown_end_time - current_time)
                
                if remaining > 0:
                    program_state = f"NUMARATOARE: {remaining}"
                    cv2.putText(frame, str(remaining), POS_COUNTDOWN, FONT, FONT_SCALE * 1.5, COLOR_RED, THICKNESS + 1)
                else:
                    countdown_active = False
                    program_state = "PROCESARE..."
                    
                    cv2.putText(frame, program_state, POS_STATE, FONT, FONT_SCALE, COLOR_WHITE, THICKNESS)
                    cv2.imshow('Live Feed', frame)
                    cv2.waitKey(1) 
                    
                    capture_num = get_next_capture_number()
                    img_path = os.path.join(IMAGE_FOLDER, f"img{capture_num}.jpg")
                    log_path = os.path.join(LOG_CONTENT_FOLDER, f"textLog{capture_num}.txt")
                    
                    cv2.imwrite(img_path, clean_frame)
                    print(f"Imagine salvata: {img_path}")
                    
                    try:
                        content_for_tts = process_image_with_gemini(model, img_path, log_path)
                        
                        program_state = "REDARE AUDIO..."
                        cv2.putText(frame, program_state, POS_STATE, FONT, FONT_SCALE, COLOR_WHITE, THICKNESS)
                        cv2.imshow('Live Feed', frame)
                        cv2.waitKey(1)
                        
                        speak_text(content_for_tts, LANGUAGE)
                        
                    except Exception as e:
                        print(f"Eroare majora in bucla de procesare: {e}")
                    
                    print("Procesare terminata. Se revine la ASTEPTARE.")
                    program_state = "ASTEPTARE"


            cv2.putText(frame, program_state, POS_STATE, FONT, FONT_SCALE, COLOR_WHITE, THICKNESS)
            cv2.imshow('Live Feed', frame)
            
            # Acum senzorul ruleaza non-stop, independent de starea programului
            object_present = sensor.check_object_presence()
            sensor.control_led(object_present) # Actualizam LED-ul
            
            key = cv2.waitKey(1) & 0xFF

            if key == ord('1') and program_state == "ASTEPTARE":
                print("Tasta '1' apasata! Incep numaratoarea...")
                program_state = "NUMARATOARE"
                countdown_active = True
                countdown_end_time = time.time() + COUNTDOWN_SECONDS

            if key == ord('q'):
                print("Se inchide programul...")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        sensor.cleanup_sensor()
        print("Resurse eliberate. Program incheiat.")


# --- 5. Punct de Intrare ---
if __name__ == "__main__":

    print("Se porneste aplicatia...")
    try:
        print("Se porneste aplicatia...")
        
        # Initializam senzorul
        if not sensor.setup_sensor():
            # Daca setup-ul esueaza (ex: lipsa sudo), ne oprim.
            sys.exit(1)
            
        # Pornim bucla principala a camerei
        main()
        
    except KeyboardInterrupt:
        print("\nProgram incheiat manual (Ctrl+C).")
        sys.exit(0)
    except Exception as e:
        print(f"A aparut o eroare neasteptata: {e}")
        sys.exit(1)