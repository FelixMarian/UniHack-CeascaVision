import cv2
import time
import os

#Camera 0 (singura)

folder_name = "images"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

    print(f"Director creat: {folder_name}")

#Verificam ca s-a pornit
cap = cv2.VideoCapture(0)
if not cap.isOpened():
 
    print("Eroare: Nu s-a putut deschide camera.")
    exit()

print("Feed live pornit. Apasa 'q' pt iesire.")

print("Captura incepe in 5 secunde...")

total_captures = 5
captures_taken = 0

first_capture_delay = 5.0
capture_interval = 2.0

start_time = time.time()
next_capture_time = start_time + first_capture_delay

while True:
    #Afisam feedul
    ret, frame = cap.read()
    if not ret:
        
        print("Eroare: Cadru gol. Se inchide...")
        break

    current_time = time.time()

    #Logica de capturare
    
    if (captures_taken < total_captures) and (current_time >= next_capture_time):
        
        captures_taken += 1
        
        #Salvam imaginea
        filename = os.path.join(folder_name, f"capture_{captures_taken}.jpg")
        cv2.imwrite(filename, frame)
        
        
        print(f"Capturat: {filename}")
        
        next_capture_time += capture_interval
        
        if captures_taken == total_captures:
            
            print("Captura completa. Feedul ramane activ.")

    cv2.imshow('Live Feed', frame)

    if cv2.waitKey(1) == ord('q'):
        break

#Inchidere camera
cap.release()
cv2.destroyAllWindows()

print("Feed oprit.")