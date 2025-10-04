# Frontend Web pour l'Outil de Pair Ranking

## Description
Interface web minimaliste pour l'outil de classement de films par comparaisons par paires. Cette interface web remplace l'interface en ligne de commande tout en conservant la même logique de classement basée sur TrueSkill.

## Fonctionnalités
- **Interface intuitive** : Comparaison visuelle de films par paires
- **Authentification simple** : Saisie du nom d'utilisateur
- **Configuration flexible** : Choix du nombre de comparaisons (20, 50, 100)
- **Progression visuelle** : Barre de progression et compteur
- **Résultats détaillés** : Classement final avec scores et confiance
- **Responsive** : Interface adaptée aux mobiles et tablettes

## Installation et Lancement

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancer le serveur web
```bash
python app.py
```

### 3. Accéder à l'interface
Ouvrir votre navigateur à l'adresse : `http://localhost:5000`

## Structure du Projet
```
Flims_Ranking/
├── app.py                 # Serveur Flask principal
├── pair_ranking.py        # Backend original (TUI)
├── templates/
│   └── index.html         # Interface web
├── static/
│   ├── style.css          # Styles CSS
│   └── script.js          # Logique JavaScript
├── ListeATrier.md         # Liste des films à classer
└── requirements.txt       # Dépendances Python
```

## Utilisation

1. **Démarrage** : Entrez votre nom et choisissez le nombre de comparaisons
2. **Comparaisons** : Pour chaque paire de films, choisissez votre préférence :
   - Cliquez sur "Choisir A" ou "Choisir B"
   - Ou cliquez sur "Égalité" si les films sont équivalents
   - Utilisez "Passer" pour ignorer une comparaison
3. **Résultats** : Consultez votre classement final avec les scores de confiance

## Fonctionnalités Techniques

- **Backend Flask** : API REST simple pour gérer les sessions et comparaisons
- **Frontend Vanilla** : HTML/CSS/JavaScript sans frameworks lourds
- **Algorithme TrueSkill** : Même logique de classement que l'outil original
- **Sauvegarde automatique** : Les résultats sont sauvegardés en CSV

## Compatibilité
- Navigateurs modernes (Chrome, Firefox, Safari, Edge)
- Responsive design pour mobile et desktop
- Fonctionne avec Python 3.7+
