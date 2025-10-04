# Outil de Pair Ranking pour Films

Un outil simple et efficace pour classer des films selon vos préférences personnelles en utilisant des comparaisons par paires.

## Fonctionnalités

- **Interface TUI intuitive** avec questionary
- **Algorithme TrueSkill** pour optimiser le nombre de comparaisons
- **Sauvegarde automatique** après chaque comparaison
- **Authentification simple** par nom d'utilisateur
- **Génération de classements personnalisés**
- **Système de reprise** : Reprendre un classement existant à partir des fichiers CSV

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python pair_ranking.py
```

L'outil va :
1. Charger la liste de films depuis `ListeATrier.md`
2. **Détecter automatiquement** les fichiers CSV existants
3. Vous proposer de reprendre un classement existant ou d'en créer un nouveau
4. Vous proposer des paires de films à comparer
5. Générer un fichier `ListeATrier.<votre_nom>.csv` avec votre classement

## Système de reprise

L'outil détecte automatiquement les fichiers CSV existants (format `ListeATrier.<utilisateur>.csv`) et vous permet de :
- **Reprendre un classement en cours** avec toutes les comparaisons déjà effectuées
- **Continuer les comparaisons** là où vous vous êtes arrêté
- **Conserver les scores TrueSkill** calculés précédemment

### Comment reprendre un classement

1. Lancez l'outil : `python pair_ranking.py`
2. L'outil détectera automatiquement les fichiers CSV existants
3. Choisissez "Reprendre [nom_utilisateur]" dans le menu
4. Continuez vos comparaisons normalement

## Configuration

- **Nombre de comparaisons** : 20 (rapide), 50 (standard), 100 (complet) ou personnalisé
- **Arrêt possible** à tout moment
- **Reprise automatique** grâce aux fichiers CSV générés

## Format de sortie

Le fichier généré contient :
- Métadonnées (date, nombre de comparaisons, score de confiance)
- Classement numéroté des films
- Scores TrueSkill pour chaque film
- Informations sur le genre et la catégorie

## Algorithme

Utilise TrueSkill pour :
- Minimiser le nombre de comparaisons nécessaires
- Garantir la robustesse du classement
- Gérer les égalités et les comparaisons manquées
- Fournir un score de confiance
