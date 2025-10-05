#!/usr/bin/env python3
"""
Serveur Flask pour l'outil de pair ranking.
Interface web minimaliste pour classer des films.
"""

import csv
import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from flask import Flask, render_template, request, jsonify, session
from trueskill import Rating, rate, setup

app = Flask(__name__)
app.secret_key = "flims_ranking_secret_key_2024"

# Configuration TrueSkill
setup(mu=25.0, sigma=8.333, beta=4.166, tau=0.0833, draw_probability=0.0)


class PairRankingWeb:
    def __init__(self, source_file: str = "ListeATrier.md"):
        self.source_file = source_file
        self.films = []
        self.user_ratings = {}  # {film_id: Rating}
        self.comparisons_made = 0
        self.user_name = ""
        self.output_file = ""

    def load_films(self) -> None:
        """Charge la liste de films depuis le fichier source."""
        try:
            with open(self.source_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            self.films = []
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not line.startswith("#"):
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

        except FileNotFoundError:
            print(f"❌ Fichier {self.source_file} non trouvé")
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")

    def get_random_pair(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Sélectionne une paire aléatoire de films pour comparaison."""
        if len(self.films) < 2:
            return None, None
        film1, film2 = random.sample(self.films, 2)
        return film1, film2

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
            film1["rating"] = new_rating1[0]
            film2["rating"] = new_rating2[0]

    def generate_ranking(self) -> List[Dict]:
        """Génère la liste finale triée par rating."""
        sorted_films = sorted(self.films, key=lambda x: x["rating"].mu, reverse=True)
        return sorted_films

    def save_final_ranking(self, ranked_films: List[Dict]) -> None:
        """Sauvegarde le classement final au format CSV."""
        with open(self.output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([f"# Classement personnel de {self.user_name}"])
            writer.writerow([f"# Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}"])
            writer.writerow([f"# Comparaisons effectuées: {self.comparisons_made}"])
            writer.writerow([f"# Score de confiance moyen: {self.calculate_confidence():.2f}"])
            writer.writerow([])
            writer.writerow(["Rang", "Description", "Genre", "Catégorie", "Score_Mu", "Score_Sigma", "Score_Confiance"])

            for i, film in enumerate(ranked_films, 1):
                confidence = max(0, 1 - (film["rating"].sigma / 8.333))
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

    def calculate_confidence(self) -> float:
        """Calcule un score de confiance basé sur la variance des ratings."""
        if not self.user_ratings:
            return 0.0
        avg_sigma = sum(rating.sigma for rating in self.user_ratings.values()) / len(self.user_ratings)
        return max(0, 1 - (avg_sigma / 8.333))


# Instance globale
ranking_tool = PairRankingWeb()
ranking_tool.load_films()


@app.route("/")
def index():
    response = render_template("index.html")
    return response


@app.route("/start", methods=["POST"])
def start_session():
    data = request.get_json()
    user_name = data.get("user_name", "Anonyme")
    max_comparisons = int(data.get("max_comparisons", 50))

    session["user_name"] = user_name
    session["max_comparisons"] = max_comparisons
    session["comparisons_made"] = 0
    session["user_ratings"] = {}

    ranking_tool.user_name = user_name
    ranking_tool.output_file = f"ListeATrier.{user_name}.csv"
    ranking_tool.comparisons_made = 0
    ranking_tool.user_ratings = {film["id"]: film["rating"] for film in ranking_tool.films}

    return jsonify({"status": "success", "message": "Session démarrée"})


@app.route("/get_pair")
def get_pair():
    if not session.get("user_name"):
        return jsonify({"error": "Session non démarrée"}), 400

    film1, film2 = ranking_tool.get_random_pair()
    if not film1 or not film2:
        return jsonify({"error": "Pas assez de films"}), 400

    return jsonify(
        {
            "film1": {
                "id": film1["id"],
                "description": film1["description"],
                "genre": film1["genre"],
                "category": film1["category"],
            },
            "film2": {
                "id": film2["id"],
                "description": film2["description"],
                "genre": film2["genre"],
                "category": film2["category"],
            },
        }
    )


@app.route("/compare", methods=["POST"])
def compare():
    if not session.get("user_name"):
        return jsonify({"error": "Session non démarrée"}), 400

    data = request.get_json()
    film1_id = data.get("film1_id")
    film2_id = data.get("film2_id")
    result = data.get("result")  # 1, 2, 3, ou 0

    if result == 0:  # Passer
        return jsonify({"status": "skipped"})

    # Trouver les films
    film1 = next((f for f in ranking_tool.films if f["id"] == film1_id), None)
    film2 = next((f for f in ranking_tool.films if f["id"] == film2_id), None)

    if not film1 or not film2:
        return jsonify({"error": "Films non trouvés"}), 400

    # Mettre à jour les ratings
    ranking_tool.update_ratings(film1, film2, result)
    session["comparisons_made"] = session.get("comparisons_made", 0) + 1
    ranking_tool.comparisons_made = session["comparisons_made"]

    return jsonify(
        {
            "status": "success",
            "comparisons_made": session["comparisons_made"],
            "max_comparisons": session.get("max_comparisons", 50),
        }
    )


@app.route("/finish")
def finish():
    if not session.get("user_name"):
        return jsonify({"error": "Session non démarrée"}), 400

    # Générer le classement final
    ranked_films = ranking_tool.generate_ranking()
    ranking_tool.save_final_ranking(ranked_films)

    # Préparer les données pour l'affichage
    results = []
    for i, film in enumerate(ranked_films, 1):
        confidence = max(0, 1 - (film["rating"].sigma / 8.333))
        results.append(
            {
                "rank": i,
                "description": film["description"],
                "genre": film["genre"],
                "category": film["category"],
                "score_mu": round(film["rating"].mu, 2),
                "score_sigma": round(film["rating"].sigma, 2),
                "confidence": round(confidence, 2),
            }
        )

    return jsonify(
        {
            "status": "success",
            "results": results,
            "comparisons_made": session["comparisons_made"],
            "confidence": round(ranking_tool.calculate_confidence(), 2),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
