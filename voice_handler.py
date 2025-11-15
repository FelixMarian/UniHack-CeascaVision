# voice_handler.py
# Gestioneaza recunoasterea vocala (STT) pentru intrebarile suplimentare.

import speech_recognition as sr
import config
from utils import speak_text
import time
import os # NOU
import google.generativeai as genai # NOU

# Obiecte pentru STT (Recunoastere Vocala)
recognizer = None
microphone = None

# NOU: Obiect pentru modelul de text
text_model = None 

def setup_voice_input():
    """
    Initializeaza microfonul, recunoasterea vocala SI modelul de text Gemini.
    """
    global recognizer, microphone, text_model
    try:
        # --- Setup STT ---
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            print("CALIBRARE ZGOMOT: Te rog sa taci 1-2 secunde...")
            recognizer.adjust_for_ambient_noise(source, duration=1.5)
        print("Microfonul este gata de ascultare.")
        
        # --- NOU: Setup Model Text Gemini ---
        print(f"Se initializeaza modelul de text: {config.MODEL_NAME_TEXT}...")
        text_model = genai.GenerativeModel(config.MODEL_NAME_TEXT)
        print("Modelul Gemini (Text) a fost initializat.")
        
        return True
        
    except AttributeError:
        # ... (eroare microfon) ...
        return False
    except Exception as e:
        print(f"EROARE la initializarea microfonului sau modelului text: {e}")
        return False

def handle_follow_up_question(last_log_path): # NOU: Accepta un parametru
    """
    Functia principala care asculta raspunsul utilizatorului.
    Gestioneaza cele 3 cazuri.
    """
    if not recognizer or not microphone:
        print("Eroare: Recunoasterea vocala (STT) nu a fost initializata.")
        return
    if not text_model:
        print("Eroare: Modelul text Gemini nu a fost initializat.")
        return

    # 1. Punem intrebarea cu voce
    question_text = "Aveți întrebări suplimentare?"
    print(f"\nTTS: {question_text}")
    speak_text(question_text)

    # 2. Incepem sa ascultam
    print(f"Se asculta pentru un raspuns... (Timeout de liniste: {config.VOICE_SILENCE_TIMEOUT}s)")
    
    try:
        with microphone as source:
            audio = recognizer.listen(
                source, 
                timeout=config.VOICE_SILENCE_TIMEOUT, 
                phrase_time_limit=config.VOICE_PHRASE_LIMIT 
            )
        
        print("Audio capturat. Se trimite pentru recunoastere...")
        text = recognizer.recognize_google(audio, language='ro-RO').lower()
        print(f"Utilizatorul a spus: '{text}'")

        # 4. Gestionam raspunsul
        
        # Cazul #2: Utilizatorul a spus "NU"
        end_keywords = ["nu", "gata", "terminat", "mulțumesc", "stop"]
        if any(keyword in text for keyword in end_keywords):
            print("Utilizatorul a terminat conversatia.")
            speak_text("Am înțeles. O zi bună!")
            time.sleep(1) 
            return

        # --- NOU: Implementare Cazul #1: Utilizatorul a pus o intrebare ---
        print("Utilizatorul a pus o intrebare. Se pregateste raspunsul...")
        
        # Verificam daca avem un log la care sa ne referim
        if not last_log_path or not os.path.exists(last_log_path):
            print("Eroare: Nu gasesc fisierul de log.")
            speak_text("Imi pare rau, nu gasesc contextul documentului anterior.")
            return

        try:
            # Citim contextul din fisierul de log
            with open(last_log_path, 'r', encoding='utf-8') as f:
                context = f.read()
            
            # Construim promptul pentru modelul de text
            prompt = f"""
Ești un asistent care răspunde la întrebări specifice bazate pe un text. Răspunde scurt și la obiect, în limba română. Folosește DOAR informațiile din textul de mai jos ("CONTEXT"). Nu inventa informații.

---
CONTEXT (Textul extras din document):
{context}
---

ÎNTREBAREA UTILIZATORULUI:
"{text}"
---

RĂSPUNS:
"""
            print("Trimit intrebarea si contextul catre Gemini (text)...")
            
            # Apelam modelul de text
            response = text_model.generate_content(prompt)
            answer = response.text
            
            print(f"Raspunsul Gemini: {answer}")
            speak_text(answer) # Redam raspunsul
            time.sleep(1) # Pauza
            
            # Optional: Am putea intra intr-o bucla aici pentru mai multe intrebari,
            # dar deocamdata iesim dupa o intrebare.
            return

        except Exception as e:
            print(f"Eroare la generarea raspunsului text: {e}")
            speak_text("A aparut o eroare la procesarea intrebarii dumneavoastra.")
            return
        # --- Sfarsit Cazul #1 ---

    except sr.WaitTimeoutError:
        # Cazul #3: Timeout
        print(f"Timeout. Niciun raspuns vocal detectat.")
        return
        
    except sr.UnknownValueError:
        # STT nu a inteles
        print("Nu am inteles ce ati spus. Se revine la ASTEPTARE.")
        speak_text("Nu am înțeles.")
        return
        
    except sr.RequestError as e:
        # Eroare API STT
        print(f"Eroare API Google STT: {e}. Se revine la ASTEPTARE.")
        speak_text("A apărut o eroare de rețea.")
        return