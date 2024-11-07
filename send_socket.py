import socket
import numpy as np
import cv2
from pynput.mouse import Listener
import pickle
import time

# Classe Client
class Client:
    def __init__(self, host='localhost', port= 80 ):
        self.host = host
        self.port = port
        self.close_socket = False

    def start(self):
        # Démarrer le socket client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        print("Connecté au serveur.")

        # Initialisation de la caméra (indice 0 pour la première caméra disponible)
        cap = cv2.VideoCapture(0)
        #cap = cv2.VideoCapture()
        #cap.open('http://185.18.130.194:8001/mjpg/1/video.mjpg')

        if not cap.isOpened():
            print("[ERREUR] Impossible d'ouvrir la caméra.")
            return

        last_saved_time = time.time()
        save_interval = 5  # secondes

        try:
            while True:
                # Lire une image depuis la caméra
                ret, frame = cap.read()
                if not ret:
                    print("[ERREUR] Impossible de lire l'image depuis la caméra.")
                    break

                # Afficher le flux vidéo
                cv2.imshow('Camera', frame)

                # Vérifier si le temps est écoulé pour envoyer l'image
                current_time = time.time()
                if current_time - last_saved_time >= save_interval:
                    print("[INFO] Envoi de l'image...")
                    result = pickle.dumps(frame)
                    client_socket.sendall(result)
                    client_socket.sendall(str.encode("foto"))
                    time.sleep(1)
                    data = client_socket.recv(5)

                    # Décodage du compteur de personnes
                    people_counter = int(data.decode('utf8'))
                    last_saved_time = current_time
                    print("[INFO] Réception des données...")
                    print(f"[INFO] Personnes détectées : {people_counter}")
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
