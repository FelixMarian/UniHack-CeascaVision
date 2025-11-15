# sensor.py
# Contine logica pentru senzorul de distanta HC-SR04

import RPi.GPIO as GPIO
import time
import config

def setup_sensor():
    """Configureaza pinii GPIO pentru senzor."""
    try:
        GPIO.setwarnings(False) # Dezactivam avertismentele
        GPIO.setmode(GPIO.BCM) # Folosim numerotarea BCM
        
        GPIO.setup(config.PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(config.PIN_ECHO, GPIO.IN)
        
        # NOU: Setup LED (din config.py)
        GPIO.setup(config.PIN_LED, GPIO.OUT)
        
        # Initializam trigger-ul pe LOW si LED-ul pe OFF
        GPIO.output(config.PIN_TRIGGER, False)
        GPIO.output(config.PIN_LED, False)
        
        print("Asteptam ca senzorul sa se stabilizeze...")
        time.sleep(2) # Asteptam 2 secunde
        print("Senzorul este gata.")
        
    except Exception as e:
        print(f"Eroare la initializarea GPIO: {e}")
        print("Asigura-te ca rulezi scriptul cu 'sudo' (sudo python main.py)")
        return False
    return True

def get_distance_meters():
    """Masoara si returneaza distanta in metri."""
    
    # Trimitem un puls de 10us
    GPIO.output(config.PIN_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(config.PIN_TRIGGER, False)

    start_time = time.time()
    stop_time = time.time()
    
    timeout = time.time() + 0.1 # Timeout de 100ms

    # Asteptam ca ECHO sa devina HIGH
    while GPIO.input(config.PIN_ECHO) == 0:
        start_time = time.time()
        if start_time > timeout:
            print("Eroare senzor: Timeout la asteptare ECHO HIGH")
            return None # Eroare de citire

    # Asteptam ca ECHO sa revina la LOW
    timeout = time.time() + 0.1 # Resetam timeout-ul
    while GPIO.input(config.PIN_ECHO) == 1:
        stop_time = time.time()
        if stop_time > timeout:
            print("Eroare senzor: Timeout la asteptare ECHO LOW")
            return None # Eroare de citire

    # Calculam distanta
    time_elapsed = stop_time - start_time
    # Viteza sunetului = 343 m/s (sau 34300 cm/s)
    # Distanta (cm) = (Timp * 34300) / 2 (dus-intors)
    # Distanta (m) = (Timp * 343) / 2
    distance_m = (time_elapsed * 343) / 2
    
    return distance_m

def check_object_presence():
    """
    Functia principala ceruta.
    Returneaza 1 daca un obiect e mai aproape decat pragul, altfel 0.
    """
    distance = get_distance_meters()
    
    if distance is not None:
        # Afisam distanta pentru debugging
        # print(f"Distanta: {distance:.2f} m") 
        
        if distance < config.DISTANCE_THRESHOLD_METERS:
            return 1 # Obiect detectat
            
    return 0 # Niciun obiect sau eroare senzor

# NOU: Functie pentru a controla LED-ul
def control_led(is_present):
    """Aprinde sau stinge LED-ul in functie de starea 'is_present' (1 sau 0)."""
    try:
        if is_present == 1:
            GPIO.output(config.PIN_LED, True)
        else:
            GPIO.output(config.PIN_LED, False)
    except Exception as e:
        # Nu oprim programul principal pentru o eroare de LED
        print(f"Eroare la controlul LED-ului: {e}")

def cleanup_sensor():
    """Curata setarile GPIO la iesire."""
    print("Curatare pini GPIO.")
    # NOU: Stingem LED-ul la iesire
    try:
        GPIO.output(config.PIN_LED, False)
    except Exception as e:
        pass # Ignoram erorile la cleanup
    GPIO.cleanup()