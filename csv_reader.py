import matplotlib.pyplot as plt
import csv
from datetime import datetime

# Classe contenant la méthode pour lire le fichier et tracer le graphique
class PeopleCounter:
    def __init__(self):
        self.csv = []

    def load_csv(self):
        # Listes pour stocker les données lues
        time_data = []  # Pour les horodatages (axe X)
        people_data = []  # Pour le nombre de personnes (axe Y)

        # Lire les données depuis le fichier CSV
        with open("people_counter.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)  # Passer l'en-tête du fichier CSV
            for row in reader:
                if row:  # Vérifier que la ligne n'est pas vide
                    # Convertir l'horodatage en format datetime pour faciliter l'affichage
                    time_data.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
                    people_data.append(int(row[1]))  # Le nombre de personnes

        print("Données lues depuis le fichier CSV.")
        self.plot_graph(time_data, people_data)

    def plot_graph(self, time_data, people_data):
        # Tracer le graphique de dispersion (scatter plot)
        plt.scatter(time_data, people_data, color='blue')  # Points de dispersion
        plt.xlabel("Temps")  # Étiquette pour l'axe X
        plt.ylabel("Nombre de personnes")  # Étiquette pour l'axe Y
        plt.title("Graphique de dispersion des données du compteur de personnes")

        # Rotation des labels de l'axe X pour une meilleure lisibilité
        plt.xticks(rotation=45)

        plt.tight_layout()  # Pour éviter que les labels se chevauchent
        plt.show()

# Exécution du programme
if __name__ == "__main__":
    # Créer une instance de la classe PeopleCounter
    counter = PeopleCounter()

    # Charger et traiter les données du fichier CSV
    counter.load_csv()
