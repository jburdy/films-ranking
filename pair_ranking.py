#!/usr/bin/env python3
"""
Outil de pair ranking pour classer des films selon les préférences utilisateur.
Utilise TrueSkill pour optimiser le nombre de comparaisons nécessaires.
"""

import csv
import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import questionary
from trueskill import Rating, rate, setup


class PairRankingTool:
    def __init__(self, source_file: str = "ListeATrier.md"):
        self.source_file = source_file
        self.films = []
        self.user_ratings = {}  # {film_id: Rating}
        self.comparisons_made = 0
        self.user_name = ""
        self.output_file = ""

        # Configuration TrueSkill
        setup(mu=25.0, sigma=8.333, beta=4.166, tau=0.0833, draw_probability=0.0)

    def load_films(self) -> None:
        """Charge la liste de films depuis le fichier source."""
        try:
            with open(self.source_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            self.films = []
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Format: description \t genre \t catégorie
                    parts = line.split("\t")
                    if len(parts) >= 1:
                        film_data = {
                            "id": i + 1,
                            "description": parts[0].strip(),
                            "genre": parts[1].strip() if len(parts) > 1 else "",
                            "category": parts[2].strip() if len(parts) > 2 else "",
                            "rating": Rating(),
                        }
                        self.films.append(film_data)
                        self.user_ratings[film_data["id"]] = film_data["rating"]

            print(f"✓ {len(self.films)} films chargés depuis {self.source_file}")

        except FileNotFoundError:
            print(f"❌ Fichier {self.source_file} non trouvé")
            exit(1)
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            exit(1)

    def detect_existing_csv(self) -> Optional[str]:
        """Détecte s'il existe un fichier CSV pour reprendre le classement."""
        csv_files = []
        for file in os.listdir("."):
            if file.startswith("ListeATrier.") and file.endswith(".csv"):
                # Extraire le nom d'utilisateur du fichier
                user_name = file.replace("ListeATrier.", "").replace(".csv", "")
                csv_files.append((file, user_name))

        if not csv_files:
            return None

        print(f"\n📁 Fichiers CSV existants détectés:")
        for i, (file, user) in enumerate(csv_files, 1):
            print(f"  {i}. {file} (utilisateur: {user})")

        choice = questionary.select(
            "Voulez-vous reprendre un classement existant?",
            choices=["Nouveau classement"] + [f"Reprendre {user}" for _, user in csv_files],
        ).ask()

        if choice == "Nouveau classement":
            return None

        # Trouver le fichier correspondant au choix
        for i, (file, user) in enumerate(csv_files, 1):
            if choice == f"Reprendre {user}":
                return file

        return None

    def load_existing_ratings(self, csv_file: str) -> None:
        """Charge les ratings existants depuis un fichier CSV."""
        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=";")

                # Lire les métadonnées
                metadata = {}
                for row in reader:
                    if row and row[0].startswith("#"):
                        if "Comparaisons effectuées:" in row[0]:
                            metadata["comparisons"] = int(row[0].split(":")[1].strip())
                        elif "utilisateur" in row[0].lower():
                            metadata["user"] = row[0].split("de")[1].strip()
                    elif row and row[0] == "Rang":  # En-tête des colonnes
                        break

                # Lire les données des films
                for row in reader:
                    if len(row) >= 7 and row[0].isdigit():
                        try:
                            film_id = int(row[0])  # Le rang
                            mu = float(row[4])  # Score_Mu
                            sigma = float(row[5])  # Score_Sigma

                            # Trouver le film correspondant par description
                            for film in self.films:
                                if film["id"] == film_id:
                                    # Créer un nouveau Rating avec les valeurs chargées
                                    film["rating"] = Rating(mu=mu, sigma=sigma)
                                    self.user_ratings[film["id"]] = film["rating"]
                                    break
                        except (ValueError, IndexError):
                            continue

                # Mettre à jour les métadonnées
                if "comparisons" in metadata:
                    self.comparisons_made = metadata["comparisons"]
                if "user" in metadata:
                    self.user_name = metadata["user"]
                    self.output_file = csv_file

                print(f"✓ Classement existant chargé: {self.comparisons_made} comparaisons effectuées")
                print(f"✓ Utilisateur: {self.user_name}")

        except Exception as e:
            print(f"❌ Erreur lors du chargement du CSV existant: {e}")
            print("✓ Démarrage d'un nouveau classement...")
            self.comparisons_made = 0

    def authenticate_user(self) -> None:
        """Authentification simple de l'utilisateur."""
        self.user_name = questionary.text("Entrez votre nom d'utilisateur:").ask()

        if not self.user_name:
            self.user_name = "Anonyme"

        self.output_file = f"ListeATrier.{self.user_name}.csv"
        print(f"✓ Utilisateur: {self.user_name}")
        print(f"✓ Fichier de sortie: {self.output_file}")

    def select_comparison_count(self) -> int:
        """Permet à l'utilisateur de choisir le nombre de comparaisons."""
        choices = [
            ("Rapide (20 comparaisons)", 20),
            ("Standard (50 comparaisons)", 50),
            ("Complet (100 comparaisons)", 100),
            ("Personnalisé", -1),
        ]

        choice = questionary.select(
            "Combien de comparaisons souhaitez-vous faire?", choices=[c[0] for c in choices]
        ).ask()

        if choice == "Personnalisé":
            count = questionary.text("Nombre de comparaisons:", validate=lambda x: x.isdigit() and int(x) > 0).ask()
            return int(count)

        for desc, count in choices:
            if choice == desc:
                return count

        return 50  # Par défaut

    def get_random_pair(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Sélectionne une paire aléatoire de films pour comparaison."""
        if len(self.films) < 2:
            return None, None

        film1, film2 = random.sample(self.films, 2)
        return film1, film2

    def display_film(self, film: Dict) -> str:
        """Affiche un film de manière formatée."""
        return f"{film['genre']} | {film['category']}\n\n  {film['description']}\n"

    def make_comparison(self, film1: Dict, film2: Dict) -> Optional[int]:
        """Effectue une comparaison entre deux films."""
        print(f"\n{'='*60}")
        print(f"Comparaison {self.comparisons_made + 1}")
        print(f"{'='*60}")

        print(f"\n🎬 FILM A: {self.display_film(film1)}")
        print(f"\n🎬 FILM B: {self.display_film(film2)}")

        choice = questionary.select(
            "\nQuel film préférez-vous?",
            choices=["Film A", "Film B", "Égalité", "Passer cette comparaison", "Arrêter le classement"],
        ).ask()

        if choice == "Arrêter le classement":
            return None
        elif choice == "Passer cette comparaison":
            return 0
        elif choice == "Film A":
            return 1
        elif choice == "Film B":
            return 2
        elif choice == "Égalité":
            return 3

        return 0

    def update_ratings(self, film1: Dict, film2: Dict, result: int) -> None:
        """Met à jour les ratings TrueSkill selon le résultat de la comparaison."""
        if result == 0:  # Passer
            return

        rating1 = self.user_ratings[film1["id"]]
        rating2 = self.user_ratings[film2["id"]]

        new_rating1 = None
        new_rating2 = None

        if result == 1:  # Film A gagne
            new_rating1, new_rating2 = rate([(rating1,), (rating2,)])
        elif result == 2:  # Film B gagne
            new_rating2, new_rating1 = rate([(rating2,), (rating1,)])
        elif result == 3:  # Égalité
            new_rating1, new_rating2 = rate([(rating1,), (rating2,)], ranks=[0, 0])

        if new_rating1 is not None and new_rating2 is not None:
            self.user_ratings[film1["id"]] = new_rating1[0]
            self.user_ratings[film2["id"]] = new_rating2[0]

            # Mettre à jour les films
            film1["rating"] = new_rating1[0]
            film2["rating"] = new_rating2[0]

    def save_progress(self) -> None:
        """Sauvegarde le progrès actuel."""
        # Sauvegarde des ratings en JSON pour reprise possible
        progress_file = f"progress_{self.user_name}.json"
        progress_data = {
            "user_name": self.user_name,
            "comparisons_made": self.comparisons_made,
            "ratings": {
                str(film_id): {"mu": rating.mu, "sigma": rating.sigma} for film_id, rating in self.user_ratings.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=2)

    def generate_ranking(self) -> List[Dict]:
        """Génère la liste finale triée par rating."""
        # Trier par mu (rating moyen) décroissant
        sorted_films = sorted(self.films, key=lambda x: x["rating"].mu, reverse=True)
        return sorted_films

    def save_final_ranking(self, ranked_films: List[Dict]) -> None:
        """Sauvegarde le classement final au format CSV."""
        with open(self.output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")

            # En-tête avec métadonnées
            writer.writerow([f"# Classement personnel de {self.user_name}"])
            writer.writerow([f"# Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}"])
            writer.writerow([f"# Comparaisons effectuées: {self.comparisons_made}"])
            writer.writerow([f"# Score de confiance moyen: {self.calculate_confidence():.2f}"])
            writer.writerow([])  # Ligne vide

            # En-têtes des colonnes
            writer.writerow(["Rang", "Description", "Genre", "Catégorie", "Score_Mu", "Score_Sigma", "Score_Confiance"])

            # Données des films
            for i, film in enumerate(ranked_films, 1):
                confidence = max(0, 1 - (film["rating"].sigma / 8.333))  # Score de confiance individuel
                writer.writerow(
                    [
                        i,
                        film["description"],
                        film["genre"],
                        film["category"],
                        f"{film['rating'].mu:.2f}",
                        f"{film['rating'].sigma:.2f}",
                        f"{confidence:.2f}",
                    ]
                )

        print(f"✓ Classement sauvegardé dans {self.output_file}")

    def calculate_confidence(self) -> float:
        """Calcule un score de confiance basé sur la variance des ratings."""
        if not self.user_ratings:
            return 0.0

        # Score basé sur l'inverse de la variance moyenne
        avg_sigma = sum(rating.sigma for rating in self.user_ratings.values()) / len(self.user_ratings)
        return max(0, 1 - (avg_sigma / 8.333))  # Normalisé par rapport à sigma initial

    def run(self) -> None:
        """Lance l'outil de pair ranking."""
        print("🎬 Outil de Pair Ranking pour Films")
        print("=" * 40)

        # Chargement des données
        self.load_films()

        # Détection et chargement d'un classement existant
        existing_csv = self.detect_existing_csv()
        if existing_csv:
            self.load_existing_ratings(existing_csv)
        else:
            self.authenticate_user()

        # S'assurer qu'un fichier de sortie est défini
        if not self.output_file:
            self.output_file = f"ListeATrier.{self.user_name}.csv"

        # Configuration du nombre de comparaisons
        max_comparisons = self.select_comparison_count()

        print(f"\n✓ Prêt à commencer! {max_comparisons} comparaisons maximum.")
        if self.comparisons_made > 0:
            print(f"✓ Reprise: {self.comparisons_made} comparaisons déjà effectuées")
        print("Appuyez sur Entrée pour commencer...")
        input()

        # Boucle principale de comparaisons
        while self.comparisons_made < max_comparisons:
            film1, film2 = self.get_random_pair()
            if not film1 or not film2:
                break

            result = self.make_comparison(film1, film2)

            if result is None:  # Arrêt demandé
                break

            if result > 0:  # Comparaison valide
                self.update_ratings(film1, film2, result)
                self.comparisons_made += 1

                # Sauvegarde après chaque comparaison
                self.save_progress()

                print(f"✓ Comparaison {self.comparisons_made}/{max_comparisons} terminée")

        # Génération du classement final
        if self.comparisons_made > 0:
            print(f"\n🎯 Génération du classement final...")
            ranked_films = self.generate_ranking()
            self.save_final_ranking(ranked_films)
        else:
            print(f"\n⚠️  Aucune comparaison effectuée. Aucun classement généré.")
            return

        # Nettoyage
        progress_file = f"progress_{self.user_name}.json"
        if os.path.exists(progress_file):
            os.remove(progress_file)

        print(f"\n✅ Classement terminé!")
        print(f"📊 {self.comparisons_made} comparaisons effectuées")
        print(f"📁 Résultat sauvegardé: {self.output_file}")


if __name__ == "__main__":
    tool = PairRankingTool()
    tool.run()
