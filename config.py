# config.py
# Acest fisier contine toate variabilele de configurare

# === Setari Fisiere & Foldere ===
API_KEY_FILE = "apiKey.txt"
IMAGE_FOLDER = "images"
LOG_CONTENT_FOLDER = "content_logs"
LOG_TYPE_FILE = "typesLogs.txt"

# === Setari Model Gemini ===
MODEL_NAME = 'gemini-2.5-light'

# === Setari TTS (Text-to-Speech) ===
LANGUAGE = 'ro'
TEMP_AUDIO_FILE = "temp_speech.mp3"

# === Setari Camera & UI ===
COUNTDOWN_SECONDS = 5
POS_STATE = (10, 30)  # Sus-stanga pentru Stare
POS_COUNTDOWN = (10, 70) # Sub stare, pentru numaratoare
FONT = 0 # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (0, 0, 255)
THICKNESS = 2

# === NOU: Setari Senzor HC-SR04 & LED Test ===
# Seteaza pinii BCM pe care i-ai conectat
PIN_TRIGGER = 18
PIN_ECHO = 24
PIN_LED = 25 # Pinul pentru LED-ul de test
# Pragul in metri (1.5 metri)
DISTANCE_THRESHOLD_METERS = 1.5