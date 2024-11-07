import socket
import pickle
import os
import sys
import numpy as np
import cv2
from ultralytics import YOLO
from datetime import datetime
import threading


# Define the server class
class Server:
    def __init__(self, host='localhost', port=80):
        self.host = host
        self.port = port
        self.client_sockets = []
        self.csv = [["time", "people"]]
        self.yolo_net = YOLO("yolov8n.pt")

    def start(self):
        # Start the server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print("Server started, waiting for clients to connect...")

        # Launch a thread to continuously accept new clients
        threading.Thread(target=self.accept_clients, args=(server_socket,), daemon=True).start()

        # Start processing client data
        self.collect_results()

    def accept_clients(self, server_socket):
        while True:
            client, addr = server_socket.accept()
            self.client_sockets.append(client)
            print(f"Client {addr} connected.")

    def collect_results(self):
        try:
            while True:
                for client_socket in list(self.client_sockets):
                    try:
                        data = b""
                        result = None
                        while True:
                            packet = client_socket.recv(4096)
                            if not packet:
                                raise ConnectionResetError  # Client disconnected
                            if str.encode("foto") in packet:
                                index = packet.find(str.encode("foto"))
                                packet = packet[:index]
                                data += packet
                                break
                            else:
                                data += packet
                        try:
                            result = pickle.loads(data)
                        except:
                            client_socket.sendall(str(0).encode('utf8'))
                            continue

                        if result is not None:
                            print(f"[INFO] Data received from {client_socket.getpeername()}")
                            detections = self.yolo_net.predict(source=result)
                            person_count = sum(1 for detection in detections[0]
                                               if detection.boxes.cls.item() == 0
                                               and detection.boxes.conf.item() > 0.5)

                            print(f"People Counter: {person_count}\n")
                            self.csv.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), person_count])
                            client_socket.sendall(str(person_count).encode('utf8'))

                    except (ConnectionResetError, BrokenPipeError):
                        # Remove the client if disconnected
                        print(f"Client {client_socket.getpeername()} disconnected.")
                        self.client_sockets.remove(client_socket)
                        client_socket.close()

                    print("-" * 80)

        except KeyboardInterrupt:
            self.stop_server()

    def save_csv(self):
        with open("people_counter.csv", "w") as f:
            for row in self.csv:
                f.write(",".join(map(str, row)) + "\n")
        print("CSV file saved.")

    def close_connections(self):
        for client_socket in self.client_sockets:
            client_socket.close()
        print("All connections closed.")

    def stop_server(self):
        self.save_csv()
        self.close_connections()
        sys.exit(0)


# Start the server
if __name__ == "__main__":
    server = Server()
    server.start()
