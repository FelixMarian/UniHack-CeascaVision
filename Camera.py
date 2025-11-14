import cv2

#Camera 0 (singura)
cap = cv2.VideoCapture(0)

#Verificam ca s-a pornit
if not cap.isOpened():
    print("Nu s-a pornit camera")
    exit()

print("Camera OK. Apasa q pt a iesi")


while True:
    #Citim un frame, ret = 1 daca a mers
    ret, frame = cap.read()

    #Ret = 0, iesim din while
    if not ret:
        print("Error: Can't receive frame (stream end?). Exiting ...")
        break

    #Rezultat
    cv2.imshow('Live feed', frame)

    #Vedem la 1ms daca se apasa q
    if cv2.waitKey(1) == ord('q'):
        break

#Inchidere camera
cap.release()
cv2.destroyAllWindows()

print("Camera feed stopped.")