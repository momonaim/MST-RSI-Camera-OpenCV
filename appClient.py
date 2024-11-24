import socket
import cv2
import pickle
import struct
from ultralytics import YOLO
import csv
from datetime import datetime

# Initialiser YOLOv8
model = YOLO('yolov8n.pt')  # Utilisez un modèle YOLO préentraîné

# Configurer le serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(('localhost', 5000))
print("[INFO] Connecté au serveur.")

# Ouvrir le flux vidéo (depuis l'URL de la caméra)
cap = cv2.VideoCapture('http://159.130.70.206/mjpg/video.mjpg')

# Initialiser le fichier CSV
csv_file = 'detections.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Écrire l'en-tête
    writer.writerow(['time', 'people'])

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERREUR] Impossible de lire la vidéo.")
        break

    # Analyser l'image avec YOLOv8
    results = model(frame)

    # Dessiner des boîtes autour des personnes détectées et afficher "Person"
    for result in results:
        for box in result.boxes:
            if int(box.cls) == 0:  # La classe "0" correspond aux personnes
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Boîte verte
                cv2.putText(frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Afficher la frame avec les détections
    cv2.imshow('Detection Client', frame)

    # Calculer le nombre de personnes détectées
    people_count = sum(1 for result in results for box in result.boxes if int(box.cls) == 0)
    print(f"[INFO] Nombre de personnes détectées : {people_count}")

    # Enregistrer les données dans le fichier CSV
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([current_time, people_count])

    # Envoyer le nombre de personnes détectées au serveur
    server_socket.send(str(people_count).encode('utf-8'))

    # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
server_socket.close()
cv2.destroyAllWindows()