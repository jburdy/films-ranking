# Contexte
Une grande liste de films est à disposition. Plusieurs utilisateurs doivent exprimer leur préférence afin de regarder les films dans l'ordre de plus apprécié au moins apprécier selon les gouts du groupe.


# Cahier des charges "outil de pair ranking"

- **Objectif fonctionnel**  
  Permettre à tout utilisateur de générer sa propre liste de préférences à partir d'une liste source (fichier `ListeATrier.md`) en comparant successivement des paires d'éléments, via une interface simple.  
  Les classements utilisateur sont enregistrés dans des fichiers individuels (par exemple, `ListeATrier.JBU.csv`).

- **Spécification technique**
  - **Format d'entrée** :  
    - Fichier texte markdown (`ListeATrier.md`), une entrée par ligne, sans doublon.
  - **Interface utilisateur** :  
    - Application TUI minimaliste (Questionary) avec présentation aléatoire de paires à comparer.
    - Authentification simple (pseudo en début de session).
    - Nombre de comparaisons configurable, arrêt possible après couverture statistique suffisante.
    - Retour d'information visuel après chaque choix, historique optionnel.
    - **Système de reprise** : Détection automatique des fichiers CSV existants pour reprendre un classement en cours.
  - **Algorithme** :
    - Basé sur TrueSkill configuré pour minimiser le nombre de paires présentées tout en garantissant la robustesse du classement.
  - **Sortie** :  
    - Un fichier `ListeATrier.<utilisateur>.csv` contenant la liste triée pour chaque utilisateur. Avec le score et autres info importante.
    - En-tête facultatif avec métadonnées (date, nombre de comparaisons, score de confiance…).
  - **Robustesse** :
    - Sauvegarde du fichier après chaque réponse (c'est tout petit).
    - **Système de reprise** : Possibilité de reprendre un classement existant à partir des fichiers CSV générés.
    - Logs d'activité utilisateur.
