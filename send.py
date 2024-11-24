import socket
import numpy as np
import cv2
from pynput.mouse import Listener
import pickle
import time

# Classe Client
class Client:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.close_socket = False

    def start(self):
        # Démarrer le socket client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        print("Connecté au serveur.")

        # Initialisation de la caméra avec le flux vidéo
        #cap = cv2.VideoCapture('http://63.142.183.154:6103/mjpg/video.mjpg')
        #cap = cv2.VideoCapture('http://104.207.27.126:8080/mjpg/video.mjpg')
        cap = cv2.VideoCapture('http://159.130.70.206/mjpg/video.mjpg')

        if not cap.isOpened():
            print("[ERREUR] Impossible d'ouvrir la caméra.")
            return

        # Initialisation du détecteur de personnes HOG
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        last_saved_time = time.time()
        save_interval = 5  # secondes

        try:
            while True:
                # Lire une image depuis la caméra
                ret, frame = cap.read()
                if not ret:
                    print("[ERREUR] Impossible de lire l'image depuis la caméra.")
                    break

                # Détection des personnes dans l'image
                boxes, weights = hog.detectMultiScale(frame, winStride=(8,8))

                # Dessiner un cadre autour des personnes détectées
                for (x, y, w, h) in boxes:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Afficher le nombre de personnes détectées en haut de l'image
                people_count = len(boxes)
                cv2.putText(frame, f'Personnes detectees : {people_count}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Afficher le flux vidéo
                cv2.imshow('Camera', frame)

                # Envoi de l'image toutes les 5 secondes
                current_time = time.time()
                if current_time - last_saved_time >= save_interval:
                    print("[INFO] Envoi de l'image...")
                    result = pickle.dumps(frame)
                    client_socket.sendall(result)
                    client_socket.sendall(str.encode("foto"))
                    time.sleep(1)
                    data = client_socket.recv(5)

                    # Décodage du compteur de personnes
                    server_people_count = int(data.decode('utf8'))
                    last_saved_time = current_time
                    print("[INFO] Réception des données...")
                    print(f"[INFO] Personnes detectees (Serveur) : {server_people_count}")
                    print("*" * 80)

                # Quitter si 'q' est pressé
                if (cv2.waitKey(1) & 0xFF) == ord('q'):
                    break

        finally:
            # Fermer la caméra et le socket
            cap.release()
            cv2.destroyAllWindows()
            client_socket.close()
            print("Connexion fermée.")

# Lancer le client
if __name__ == "__main__":
    client = Client()
    client.start()
