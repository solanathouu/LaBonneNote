# LaBonneNote

**Assistant scolaire intelligent pour le college francais (6eme - 3eme)**

LaBonneNote est un chatbot RAG (Retrieval-Augmented Generation) qui repond aux questions des collegiens **uniquement a partir de sa base de connaissances**. Il ne fabule jamais : si l'information n'est pas dans la base, il le dit.

<p align="center">
  <img src="frontend/assets/mascot/mascot-base.png" alt="Marianne - Mascotte LaBonneNote" width="200">
</p>

---

## Fonctionnalites

### Chat intelligent
- Reponses basees exclusivement sur 43 857 chunks de cours (zero hallucination)
- Auto-detection du niveau (6eme/5eme/4eme/3eme) et de la matiere
- Prompts pedagogiques adaptes a chaque niveau
- Sources affichees avec liens Vikidia

### Bibliotheque
- 24 321 articles organises en 8 matieres
- Recherche full-text en temps reel (insensible aux accents et a la casse)
- Pagination intelligente (50 lecons par page)
- Tri par pertinence (titre > resume)

### Quiz automatiques
- Generation de QCM (3-10 questions) a partir de n'importe quelle lecon
- Generation parallele asynchrone via LLM
- Scoring + feedback detaille par question
- Historique des quiz dans localStorage

### Mes Cours (PDF)
- Upload drag & drop de PDF personnels
- Extraction, chunking et ingestion automatique dans ChromaDB
- Interrogation separee ou combinee avec la base generale

### UX
- Mode sombre / clair avec detection des preferences systeme
- Mascotte "Marianne" dynamique (change selon la matiere et le contexte)
- Design "Cahier Numerique" (grille, typographie Lexend/DM Sans, couleurs par matiere)
- Interface responsive (desktop, tablette, mobile)
- Systeme de favoris persistant

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.11+ / FastAPI / Uvicorn |
| RAG | LangChain + LangChain-OpenAI |
| Base vectorielle | ChromaDB (persistance locale) |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small (1536 dimensions) |
| Frontend | HTML / CSS / JS vanilla (zero dependance npm) |
| Scraping | cloudscraper + BeautifulSoup + API MediaWiki |

---

## Architecture RAG

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1 : Preparation (offline)                        │
│                                                         │
│  Vikidia API ──> Scraping ──> Nettoyage ──> Chunking    │
│       │              │            │             │        │
│       │         cloudscraper  regex/LaTeX   500 tokens   │
│       │                                    overlap 50    │
│       └──────────────────────────────────────────┐       │
│                                                  v       │
│                                             ChromaDB     │
│                                          (43 857 chunks) │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PHASE 2 : Utilisation (runtime)                        │
│                                                         │
│  Question ──> Detection niveau/matiere                  │
│     │              │                                    │
│     v              v                                    │
│  ChromaDB ──> Top 5 chunks ──> Prompt adapte ──> LLM   │
│  (similarity)                    (niveau)      (GPT-4o) │
│                                                  │      │
│                                                  v      │
│                                        Reponse + Sources│
└─────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequis
- Python 3.11+
- Une cle API OpenAI

### Etapes

```bash
# 1. Cloner le projet
git clone https://github.com/<votre-username>/LaBonneNote.git
cd LaBonneNote

# 2. Creer un environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Installer les dependances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Editer .env avec votre cle OpenAI
```

### Lancer le scraping (optionnel)

Si vous souhaitez reconstituer la base de donnees depuis zero :

```bash
# Toutes les matieres
python -m scraper.pipeline

# Une seule matiere
python -m scraper.pipeline --matiere mathematiques

# Ingestion dans ChromaDB
cd backend && python ingest_chromadb.py
```

> Les donnees pre-scrapees sont fournies dans `data/` pour eviter de re-scraper.

### Lancer l'application

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Ouvrir http://localhost:8000 dans le navigateur.

---

## Structure du projet

```
LaBonneNote/
├── backend/                    # API FastAPI + RAG + services
│   ├── main.py                 # 11 endpoints API + modeles Pydantic
│   ├── rag.py                  # Chaine RAG : retrieve + generate
│   ├── prompts.py              # Prompts adaptes par niveau + quiz
│   ├── detection.py            # Auto-detection niveau / matiere
│   ├── pdf_service.py          # Upload, extraction, chunking PDF
│   ├── quiz_service.py         # Generation async de QCM via LLM
│   └── ingest_chromadb.py      # Script d'ingestion ChromaDB
├── scraper/                    # Pipeline de collecte de donnees
│   ├── vikidia.py              # Scraper API MediaWiki Vikidia
│   ├── cleaner.py              # Nettoyage (LaTeX, wiki, sections)
│   ├── chunker.py              # Decoupage en chunks (~500 tokens)
│   ├── metadata.py             # Categories et metadonnees
│   └── pipeline.py             # Orchestration du pipeline complet
├── frontend/                   # SPA vanilla (HTML/CSS/JS)
│   ├── index.html              # Structure HTML
│   ├── app.js                  # Router SPA + 8 vues
│   ├── style.css               # Design system "Cahier Numerique"
│   └── assets/mascot/          # 20 illustrations "Marianne"
├── data/
│   ├── raw/vikidia/            # Articles bruts (JSON par matiere)
│   └── processed/              # Chunks prets pour embedding
├── tests/                      # Tests unitaires et integration
├── presentation.html           # Presentation orale (15 slides)
├── GUIDE_TECHNIQUE_ORAL.md     # Guide technique pour soutenance
├── requirements.txt            # Dependances Python
└── .env.example                # Template variables d'environnement
```

---

## Endpoints API

| Methode | Route | Description |
|---------|-------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat` | Chat avec question + niveau/matiere optionnels |
| `POST` | `/api/chat/auto` | Chat avec auto-detection niveau/matiere |
| `GET` | `/api/matieres` | Liste des 8 matieres |
| `GET` | `/api/niveaux` | Liste des niveaux (6eme-3eme) |
| `GET` | `/api/lecons/{matiere}` | Liste des lecons d'une matiere |
| `GET` | `/api/lecons/{matiere}/detail` | Detail complet d'une lecon |
| `POST` | `/api/upload-pdf` | Upload et traitement d'un PDF |
| `GET` | `/api/mes-cours` | Liste des PDFs importes |
| `DELETE` | `/api/mes-cours/{filename}` | Suppression d'un PDF |
| `POST` | `/api/quiz/generate` | Generation d'un quiz depuis une lecon |
| `POST` | `/api/quiz/validate` | Validation des reponses + scoring |

---

## Donnees

| Matiere | Articles | Chunks |
|---------|----------|--------|
| Histoire-Geographie | 13 112 | 25 474 |
| SVT | 5 454 | 8 481 |
| Francais | 3 040 | 4 835 |
| Physique-Chimie | 1 439 | 2 751 |
| Technologie | 724 | 1 349 |
| Mathematiques | 543 | 967 |
| Anglais | 6 | - |
| Espagnol | 3 | - |
| **Total** | **24 321** | **43 857** |

Source : [Vikidia](https://fr.vikidia.org/) - encyclopedie pour les 8-13 ans.

---

## Comment ca marche ?

1. **Le scraper** parcourt recursivement les categories Vikidia via l'API MediaWiki, avec contournement Cloudflare (cloudscraper)
2. **Le cleaner** supprime les sections non-educatives, le LaTeX, le balisage wiki et normalise les espaces
3. **Le chunker** decoupe chaque article en morceaux de ~500 tokens avec un overlap de 50 tokens
4. **L'ingestion** envoie les chunks dans ChromaDB avec des embeddings OpenAI (1536 dimensions)
5. **A chaque question**, le systeme recupere les 5 chunks les plus similaires, construit un prompt adapte au niveau, et genere une reponse avec GPT-4o-mini
6. **Contrainte stricte** : le LLM repond uniquement a partir du contexte fourni, jamais de ses connaissances propres

---

## Variables d'environnement

| Variable | Description | Defaut |
|----------|-------------|--------|
| `OPENAI_API_KEY` | Cle API OpenAI (obligatoire) | - |
| `CHROMA_PERSIST_DIR` | Chemin de persistance ChromaDB | `./chromadb` |
| `EMBEDDING_MODEL` | Modele d'embeddings | `text-embedding-3-small` |
| `LLM_MODEL` | Modele LLM | `gpt-4o-mini` |
| `SIMILARITY_THRESHOLD` | Seuil de similarite cosinus | `0.3` |
| `TOP_K_RESULTS` | Nombre de chunks recuperes | `5` |

---

## Contexte

Projet realise dans le cadre d'un cursus scolaire. LaBonneNote repond a un constat : les collegiens manquent d'outils adaptes a leur niveau pour reviser efficacement. Le chatbot garantit des reponses fiables en s'appuyant exclusivement sur du contenu encyclopedique adapte aux jeunes (Vikidia), sans jamais inventer d'information.

---

## Licence

Ce projet est un projet educatif. Les donnees proviennent de [Vikidia](https://fr.vikidia.org/) (licence CC BY-SA 3.0).
