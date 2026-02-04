# Phase 1 : Scraping des contenus scolaires

## Objectif
Collecter, nettoyer et stocker les cours de maths, français et histoire-géo pour les niveaux 6ème à 3ème depuis Vikidia, Wikiversité et Éduscol.

## Étapes d'implémentation

### Étape 1 : Scraper Vikidia (`scraper/vikidia.py`)
- Utiliser l'API MediaWiki pour lister les articles par catégorie
- Catégories cibles :
  - Mathématiques : `Catégorie:Mathématiques`, `Catégorie:Géométrie`, `Catégorie:Algèbre`
  - Français : `Catégorie:Langue française`, `Catégorie:Littérature`, `Catégorie:Grammaire`
  - Histoire-Géo : `Catégorie:Histoire`, `Catégorie:Géographie`
- Extraire le contenu texte via `action=query&prop=extracts&explaintext=1`
- Sauvegarder en JSON dans `data/raw/vikidia/`

### Étape 2 : Scraper Wikiversité (`scraper/wikiversite.py`)
- API MediaWiki pour naviguer les départements collège
- Catégories cibles :
  - `Catégorie:Cours de mathématiques de collège`
  - `Catégorie:Cours de français de collège`
  - `Catégorie:Cours d'histoire de collège`
- Extraire contenu des leçons
- Sauvegarder en JSON dans `data/raw/wikiversite/`

### Étape 3 : Scraper Éduscol (`scraper/eduscol.py`)
- Scraping HTTP des pages programmes
- Pages cibles : programmes cycle 3 et cycle 4
- Extraire les attendus, compétences, repères
- Sauvegarder en JSON dans `data/raw/eduscol/`

### Étape 4 : Nettoyage (`scraper/cleaner.py`)
- Supprimer le HTML résiduel
- Supprimer les références, notes de bas de page, liens internes wiki
- Normaliser les espaces et la ponctuation
- Supprimer les sections non pertinentes (Voir aussi, Liens externes, etc.)

### Étape 5 : Chunking (`scraper/chunker.py`)
- Découper les textes en chunks de ~500 tokens
- Découpage intelligent : respecter les paragraphes et sections
- Overlap de ~50 tokens entre chunks pour le contexte

### Étape 6 : Métadonnées (`scraper/metadata.py`)
- Déduire la matière depuis la catégorie source
- Déduire le niveau quand possible (sinon "college")
- Attacher titre, URL, source à chaque chunk

### Étape 7 : Pipeline (`scraper/pipeline.py`)
- Orchestrer : scrape → clean → chunk → metadata → save
- Sauvegarder les chunks finaux dans `data/processed/`
- Logging de progression
- Mode incrémental : ne pas re-scraper ce qui existe déjà

### Étape 8 : Ingestion ChromaDB
- Lire les chunks depuis `data/processed/`
- Générer les embeddings via OpenAI
- Stocker dans ChromaDB avec métadonnées
- Script séparé ou intégré dans le pipeline
