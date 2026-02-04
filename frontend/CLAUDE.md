# Module Frontend

## Rôle
Interface chat simple pour les collégiens. HTML/CSS/JS vanilla, pas de framework.

## Architecture
```
frontend/
├── index.html       # Page principale avec le chat
├── style.css        # Styles de l'interface
└── app.js           # Logique : appels API, gestion du chat
```

## Fonctionnalités
- Zone de chat avec historique des messages (bulles utilisateur/bot)
- Sélecteurs de filtre : niveau (6ème-3ème) et matière (maths, français, histoire-géo)
- Champ de saisie + bouton envoyer
- Affichage des sources utilisées pour chaque réponse
- Message d'accueil expliquant le périmètre du bot
- Indicateur de chargement pendant la génération

## Connexion au backend
- Appels à `POST /api/chat` via `fetch()`
- Chargement des filtres depuis `/api/matieres` et `/api/niveaux`

## Conventions
- Pas de framework JS (vanilla uniquement)
- CSS responsive (mobile-first, les collégiens sont souvent sur téléphone)
- Pas de dépendances externes (pas de CDN)
- Le frontend est servi comme fichiers statiques par FastAPI
- Nommage des classes CSS en français pour cohérence avec le projet
