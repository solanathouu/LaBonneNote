# PROMPT POUR GEMINI - Preparation Presentation Orale

## INSTRUCTIONS POUR GEMINI

Tu es un expert en presentations orales techniques et en storytelling. Je vais te presenter mon projet de fin d'etudes / projet technique appele **LaBonneNote**. A partir de toutes les informations ci-dessous, cree-moi une **presentation orale structuree, fluide et haut de gamme** que je pourrai presenter demain.

**Ce que j'attends de toi :**
1. Un **plan de presentation detaille** (slide par slide) avec ce que je dois dire a l'oral et ce qui doit apparaitre visuellement
2. Un **script oral** naturel et professionnel (pas robotique, pas scolaire - un vrai pitch tech)
3. Des **transitions fluides** entre chaque partie
4. Une **ouverture accrocheuse** et une **conclusion marquante**
5. Des moments de **demonstration live** integres dans le flow
6. Un aspect **business/marche** clair et chiffre
7. Une duree cible de **15-20 minutes** (adaptable selon mes besoins)

---

## LE PROJET : LABONNENOTE

### Pitch en une phrase
LaBonneNote est un assistant scolaire intelligent base sur l'intelligence artificielle qui aide les collegiens francais (6eme-3eme) a reviser leurs cours en repondant a leurs questions **uniquement** a partir d'une base de connaissances verifiee et fiable.

### Probleme resolu
1. **Les eleves n'ont pas d'outil de revision personnalise** : les manuels sont statiques, les sites web sont disperses, et les parents ne peuvent pas toujours aider
2. **ChatGPT et les IA generiques inventent des reponses (hallucinations)** : un collegien ne peut pas verifier si la reponse est correcte, ce qui est dangereux pour l'apprentissage
3. **Pas de solution adaptee au programme francais** : les outils existants (Khan Academy, etc.) sont americains et ne correspondent pas au programme de l'Education Nationale
4. **Le soutien scolaire coute cher** : 30-50 euros/heure pour un prof particulier, inaccessible pour beaucoup de familles

### Solution LaBonneNote
Un chatbot RAG (Retrieval-Augmented Generation) qui :
- Repond **UNIQUEMENT** a partir de contenus scolaires verifies (pas d'hallucinations)
- Est **adapte au programme du college francais** (6eme a 3eme)
- **Adapte son langage** au niveau de l'eleve (vocabulaire simple en 6eme, plus technique en 3eme)
- Est **gratuit et accessible** depuis n'importe quel navigateur
- Genere des **quiz automatiques** pour tester ses connaissances
- Permet d'**importer ses propres cours** (PDFs) et de les interroger

---

## ARCHITECTURE TECHNIQUE DETAILLEE

### Stack Technologique
| Composant | Technologie | Pourquoi ce choix |
|-----------|-------------|-------------------|
| Backend API | **Python 3.11 + FastAPI** | Performance async, documentation auto OpenAPI, validation Pydantic |
| Base vectorielle | **ChromaDB** | Leger, local, sans infra cloud, ideal pour prototype |
| LLM (generation) | **OpenAI GPT-4o-mini** | Rapport qualite/prix optimal, rapide, bon en francais |
| Embeddings | **OpenAI text-embedding-3-small** | Embeddings de haute qualite pour la recherche semantique |
| Orchestration IA | **LangChain** | Framework standard pour chaines RAG, connecteurs ChromaDB/OpenAI |
| Frontend | **HTML/CSS/JS vanilla** | Zero dependance, charge instantanement, pas de build step |
| Scraping | **cloudscraper + BeautifulSoup + API MediaWiki** | Contournement Cloudflare, parsing HTML robuste |
| Extraction PDF | **PyPDFLoader (LangChain)** | Extraction fiable du texte depuis PDFs |

### Architecture du systeme (pipeline complet)

```
[COLLECTE DES DONNEES]
        |
   Scraper Vikidia (API MediaWiki + cloudscraper)
        |
   24 321 articles bruts (8 matieres)
        |
   Nettoyage (cleaner.py) : suppression LaTeX, HTML, sections inutiles
        |
   Decoupage (chunker.py) : chunks de ~500 tokens avec overlap
        |
   43 857 chunks prets
        |
[INGESTION]
        |
   Embeddings OpenAI (text-embedding-3-small)
        |
   Stockage ChromaDB (collection "cours_college")
        |
   Metadonnees : titre, matiere, niveau, URL source
        |
[UTILISATION - PIPELINE RAG]
        |
   Question de l'eleve
        |
   Auto-detection niveau + matiere (detection.py)
        |
   Embedding de la question
        |
   Recherche semantique ChromaDB (top 5 chunks)
        |
   Filtrage par matiere/niveau si specifie
        |
   Construction du prompt (contexte + question + niveau)
        |
   Generation par GPT-4o-mini (temperature 0.3 = factuel)
        |
   Reponse + sources citees + deduplication
        |
   Affichage frontend avec mascotte contextuelle
```

### Le coeur du systeme : la chaine RAG

**RAG = Retrieval-Augmented Generation** (Generation Augmentee par la Recherche)

C'est l'architecture qui differencie LaBonneNote d'un simple chatbot :

1. **Retrieval (Recuperation)** : Quand l'eleve pose une question, on ne demande PAS directement au LLM de repondre. On cherche d'abord les passages pertinents dans notre base de cours (ChromaDB) en utilisant la similarite semantique entre la question et les chunks de cours.

2. **Augmented (Augmente)** : Les passages trouves sont injectes dans le prompt comme "contexte". Le LLM recoit l'instruction stricte : "Reponds UNIQUEMENT avec ces informations, si tu ne trouves pas l'info, dis-le."

3. **Generation** : Le LLM genere une reponse pedagogique, adaptee au niveau de l'eleve, en citant ses sources. Si aucun chunk pertinent n'est trouve, il refuse poliment de repondre.

**Pourquoi c'est important** : Cela elimine les hallucinations. Un eleve ne recevra jamais une information fausse, car le LLM est contraint de ne repondre qu'a partir de contenus verifies.

### Les prompts adaptatifs par niveau

Le systeme utilise des prompts differents selon le niveau detecte :
- **6eme (11-12 ans)** : "Utilise un vocabulaire simple et accessible, donne des exemples concrets du quotidien, sois encourageant et patient"
- **5eme (12-13 ans)** : "Vocabulaire clair, tu peux introduire des termes techniques en les expliquant, encourage la reflexion"
- **4eme (13-14 ans)** : "Vocabulaire plus technique, exemples qui font appel au raisonnement, encourage l'analyse et la critique"
- **3eme (14-15 ans)** : "Vocabulaire academique, exemples qui preparent au lycee, encourage la synthese et l'argumentation"

---

## DONNEES ET SCRAPING

### Source principale : Vikidia
- **Vikidia** = Wikipedia pour les enfants (8-13 ans)
- Contenu adapte au niveau college, verifie par des contributeurs
- Scrape via l'API MediaWiki (pas de scraping HTML brut)
- **24 321 articles** collectes dans 8 matieres
- **43 857 chunks** apres decoupage et nettoyage

### Statistiques par matiere
| Matiere | Articles | Chunks | Part de la base |
|---------|----------|--------|-----------------|
| Histoire-Geographie | 13 112 | 25 474 | 58% |
| SVT | 5 454 | 8 481 | 19% |
| Francais | 3 040 | 4 835 | 11% |
| Physique-Chimie | 1 439 | 2 751 | 6% |
| Technologie | 724 | 1 349 | 3% |
| Mathematiques | 543 | 967 | 2% |
| Anglais | 6 | ~10 | <1% |
| Espagnol | 3 | ~5 | <1% |

### Sources abandonnees (et pourquoi - important pour montrer la methodologie)
- **Wikiversite** : Teste sur 507 pages, seulement 0.4% exploitables (2 lecons). Le contenu est trop universitaire et mal structure pour le college.
- **Academie en Ligne (CNED)** : URLs obsoletes, site restructure. Sur 8 pages testees, aucune n'etait pertinente pour le college.

**Ce que ca montre** : J'ai eu une demarche rigoureuse de recherche de donnees, j'ai teste plusieurs sources, mesure la qualite, et fait des choix bases sur des donnees. Ce n'est pas un projet ou j'ai pris la premiere source venue.

### Pipeline de traitement des donnees
1. **Scraping** : API MediaWiki → articles bruts JSON (cloudscraper pour bypass Cloudflare)
2. **Nettoyage** : Suppression LaTeX, balises HTML residuelles, sections "Voir aussi" / "References", normalisation Unicode
3. **Chunking** : Decoupage en morceaux de ~500 tokens avec overlap de 50 tokens (RecursiveCharacterTextSplitter de LangChain)
4. **Enrichissement metadonnees** : Ajout automatique de la matiere, sous-categorie, niveau estime, URL source
5. **Embedding + ingestion** : Conversion en vecteurs numeriques → stockage ChromaDB avec metadonnees

---

## FEATURES DE L'APPLICATION

### 1. Chat intelligent (feature principale)
- L'eleve pose une question en langage naturel
- **Auto-detection** du niveau et de la matiere par analyse de mots-cles
- Reponse generee a partir des cours stockes avec **sources citees**
- **Deduplication** des sources (1 lien par article, pas 5x le meme)
- **Detection des questions generales** (salutations, politesse) → reponse amicale sans invoquer le RAG
- Selecteur de source : "Cours generaux" / "Mes Cours" / "Les deux"

### 2. Bibliotheque de 43 870 lecons
- Organisees par **8 matieres** avec grille de mascottes cliquables
- **Pagination intelligente** : 50 lecons a la fois avec chargement progressif
- **Recherche full-text** en temps reel, insensible aux accents et a la casse
- **Tri par pertinence** : scoring (titre commence par > titre contient > resume contient)
- Cartes de lecons avec titre, resume, metadonnees
- Navigation : Bibliotheque → Matiere → Lecon → Detail complet

### 3. Systeme de Quiz automatique (generatif)
- **Generation automatique de QCM** depuis n'importe quelle lecon via GPT-4o-mini
- 3 a 10 questions par quiz, configurables
- Questions generees en **parallele** (asyncio.gather) pour performance
- **4 options** par question avec distracteurs plausibles
- **Scoring + feedback detaille** par question avec explications
- **Badges de performance** : Excellent / Bien / Moyen / A revoir
- **Historique des quiz** persiste en localStorage
- Selection diversifiee de chunks pour couvrir differentes parties de la lecon
- Systeme de fallback si le parsing JSON echoue

### 4. Systeme "Mes Cours" (import PDF)
- **Upload drag & drop** de PDFs personnels
- Extraction automatique du texte (PyPDFLoader)
- Chunking et embeddings automatiques
- Stockage dans une collection ChromaDB separee ("mes_cours")
- L'eleve peut **interroger ses propres cours** via le chat
- Recherche **multi-source** : combiner Vikidia + PDFs personnels
- Gestion complete : liste, suppression, infos (taille, date)

### 5. Systeme de Favoris
- Bouton etoile sur chaque lecon
- Stockage localStorage (persistant entre sessions)
- Vue dediee "Mes Favoris"
- Tri par date d'ajout

### 6. Mode sombre
- Toggle light/dark
- 30+ variables CSS pour coherence
- Detection automatique de la preference OS
- Persistance localStorage

### 7. Mascotte "Marianne Educative"
- **21 images PNG** illustrant une mascotte aux couleurs francaises
- **8 variations par matiere** : chaque matiere a sa Marianne avec accessoires (microscope pour SVT, equerre pour maths, etc.)
- **5 variations contextuelles** : base, loading, thinking, confused, celebrating
- Mascottes dynamiques selon la matiere dans le chat, la bibliotheque, les quiz
- Fond transparent pour integration propre

### 8. Design "Cahier Numerique"
- Background papier avec grille quadrillee 8x8px (comme un cahier Seyes)
- Typography : Lexend (titres) + DM Sans (texte)
- 8 couleurs par matiere (maths=bleu, francais=violet, histoire=orange...)
- Responsive mobile-first (3 breakpoints)
- Zero dependance frontend (HTML/CSS/JS pur)

---

## BACKEND API - 11 ENDPOINTS

| Methode | Route | Description |
|---------|-------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Chat avec question (RAG) |
| POST | `/api/chat/auto` | Chat avec auto-detection niveau/matiere |
| GET | `/api/matieres` | Liste des 8 matieres |
| GET | `/api/niveaux` | Liste des niveaux (6eme-3eme) |
| GET | `/api/lecons/{matiere}` | Liste des lecons d'une matiere |
| GET | `/api/lecons/{matiere}/detail` | Contenu complet d'une lecon |
| POST | `/api/upload-pdf` | Upload et traitement d'un PDF |
| GET | `/api/mes-cours` | Liste des PDFs importes |
| DELETE | `/api/mes-cours/{filename}` | Suppression d'un PDF |
| POST | `/api/quiz/generate` | Generation d'un quiz QCM |
| POST | `/api/quiz/validate` | Validation des reponses + scoring |

---

## ASPECT BUSINESS ET MARCHE

### Le marche du soutien scolaire en France
- **Marche du soutien scolaire** : ~2.5 milliards d'euros/an en France
- **Nombre de collegiens** : ~3.4 millions d'eleves en college en France
- **Taux de recours au soutien scolaire** : ~25% des familles utilisent une forme de soutien
- **Cout moyen** : 30-50 euros/heure pour un professeur particulier (Acadomia, Completus, etc.)
- **EdTech en croissance** : +15% par an en Europe depuis 2020

### Positionnement de LaBonneNote
- **Cible** : Collegiens francais (6eme-3eme), 11-15 ans
- **Proposition de valeur** : Assistant IA fiable (pas d'hallucinations), adapte au programme francais, gratuit
- **Differenciateurs cles** :
  1. **Pas d'hallucinations** : contrairement a ChatGPT, repond uniquement depuis des sources verifiees
  2. **Programme francais** : pas un outil americain traduit, mais un outil pense pour l'Education Nationale
  3. **Adaptation au niveau** : le meme sujet est explique differemment a un 6eme et un 3eme
  4. **Quiz generatifs** : pas une banque statique de questions, mais des quiz crees dynamiquement par IA
  5. **Import de cours personnels** : l'eleve peut importer les PDFs de ses profs

### Modeles de monetisation possibles
1. **Freemium** : Version gratuite (X questions/jour) + Premium illimite (5-10 euros/mois)
2. **B2B Etablissements** : Licence pour colleges/lycees (tableau de bord enseignant, stats eleves)
3. **Partenariat editeurs** : Integration avec les editeurs scolaires (Hatier, Nathan, Bordas) pour des contenus premium
4. **White-label** : Technologie RAG vendue a d'autres plateformes educatives

### Scalabilite technique
- ChromaDB → **Pinecone/Weaviate** pour passage au cloud
- Frontend vanilla → **React/Next.js** pour PWA mobile
- GPT-4o-mini → modele fine-tune sur contenus scolaires pour reduire les couts
- Ajout niveaux : primaire (CM1-CM2) + lycee (2nde-Terminale)
- Ajout langues : adaptation pour systemes educatifs francophones (Belgique, Suisse, Quebec, Afrique)

---

## DEFIS TECHNIQUES RENCONTRES ET SOLUTIONS

### 1. Qualite des donnees sources
- **Probleme** : Wikiversite (99.6% pages vides), Academie en Ligne (URLs obsoletes)
- **Solution** : Pivot vers Vikidia (encyclopedie pour enfants), test systematique avant adoption

### 2. Hallucinations du LLM
- **Probleme** : GPT repond meme quand il ne sait pas, invente des faits
- **Solution** : Architecture RAG avec prompt strict : "Reponds UNIQUEMENT depuis le contexte fourni. Si l'info n'y est pas, dis-le."

### 3. Performance de la recherche
- **Probleme** : 43 857 chunks a chercher rapidement
- **Solution** : ChromaDB avec embeddings pre-calcules, recherche par similarite cosinus en millisecondes

### 4. Deduplication des sources
- **Probleme** : Un article de 5 chunks pouvait apparaitre 5 fois dans les sources
- **Solution** : Set de titres deja vus (`seen_titles`), 1 lien par article

### 5. Recherche pertinente dans la bibliotheque
- **Probleme** : Resultats non tries par pertinence
- **Solution** : Systeme de scoring (titre commence par = 1000 pts, contient = 100 pts, resume = 1 pt)

### 6. Generation de quiz fiable
- **Probleme** : Le LLM ne retourne pas toujours du JSON valide
- **Solution** : Nettoyage des backticks, validation de structure, questions de fallback

### 7. Bypass Cloudflare pour le scraping
- **Probleme** : Vikidia protege par Cloudflare, requetes bloquees
- **Solution** : Library `cloudscraper` qui simule un vrai navigateur

---

## STRUCTURE DU CODE

```
RAG/                           # ~5000 lignes de code total
├── scraper/                   # Pipeline de collecte de donnees
│   ├── vikidia.py             # Scraper API MediaWiki + cloudscraper
│   ├── cleaner.py             # Nettoyage texte (LaTeX, HTML, sections)
│   ├── chunker.py             # Decoupage ~500 tokens avec overlap
│   ├── metadata.py            # Categories, matieres, niveaux
│   └── pipeline.py            # Orchestration scrape→clean→chunk→save
│
├── backend/                   # API REST + Intelligence Artificielle
│   ├── main.py                # FastAPI, 11 endpoints, validation Pydantic
│   ├── rag.py                 # Chaine RAG (retrieve + generate)
│   ├── prompts.py             # Prompts adaptatifs par niveau
│   ├── detection.py           # Auto-detection niveau/matiere
│   ├── pdf_service.py         # Upload, extraction, chunking PDFs
│   ├── quiz_service.py        # Generation QCM + validation + scoring
│   └── ingest_chromadb.py     # Script d'ingestion one-shot
│
├── frontend/                  # Interface SPA sans framework
│   ├── index.html             # Structure + navigation (97 lignes)
│   ├── app.js                 # Router SPA + 8 vues (1500+ lignes)
│   ├── style.css              # Design system complet (2000+ lignes)
│   └── assets/mascot/         # 21 images mascotte PNG
│
├── data/
│   ├── raw/vikidia/           # Articles bruts JSON par matiere
│   └── processed/             # Chunks prets pour embedding
│
├── chromadb/                  # Base vectorielle persistee (~44k vecteurs)
├── requirements.txt           # 12 dependances Python
└── CLAUDE.md                  # Documentation projet complete
```

---

## CHIFFRES CLES A RETENIR POUR LA PRESENTATION

- **43 857 chunks** de cours indexes dans ChromaDB
- **24 321 articles** Vikidia scrapes et nettoyes
- **8 matieres** couvertes (tout le programme college)
- **4 niveaux** adaptatifs (6eme, 5eme, 4eme, 3eme)
- **11 endpoints** API REST
- **5 vues** frontend (Chat, Bibliotheque, Favoris, Mes Cours, Detail)
- **3 vues quiz** (Setup, Active, Results)
- **21 mascottes** illustrees
- **0 dependance** frontend (HTML/CSS/JS pur)
- **12 packages** Python (requirements.txt lean)
- **~5000 lignes** de code total
- **0 hallucination** grace au RAG contraint

---

## SCENARIO DE DEMO SUGGEREE

Pour la presentation, voici un flow de demo efficace :

1. **Ouvrir l'app** → montrer le design "Cahier Numerique" avec la mascotte
2. **Poser une question simple** : "C'est quoi la photosynthese ?" → montrer la reponse avec sources
3. **Poser une question hors-sujet** : "Quelle est la capitale de Mars ?" → montrer le refus poli
4. **Naviguer dans la Bibliotheque** → montrer la grille de mascottes, selectionner SVT
5. **Rechercher** "volcan" dans la bibliotheque → montrer le tri par pertinence
6. **Ouvrir une lecon** → montrer le contenu complet
7. **Lancer un quiz** depuis la lecon → montrer la generation automatique
8. **Repondre au quiz** → montrer le scoring et les explications
9. **Activer le mode sombre** → montrer l'adaptation complete
10. (Bonus) **Uploader un PDF** → montrer l'import et l'interrogation

---

## CONTEXTE PERSONNEL (a adapter selon ta situation)

- Projet realise en solo / en equipe de X personnes
- Duree de developpement : ~12 sessions de travail (environ 2-3 semaines intensives)
- Outils de developpement : VS Code + Claude Code (AI-assisted development)
- Methodologie : iterations rapides, une feature complete par session
- Git : historique propre avec commits descriptifs

---

## CE QUE JE VEUX QUE TU FASSES, GEMINI

1. **Cree-moi un plan de presentation slide par slide** (titre de chaque slide + bullet points visuels + notes orateur)
2. **Ecris-moi un script oral complet** que je pourrai lire/memoriser, avec un ton professionnel mais accessible
3. **Propose des transitions** fluides entre chaque section
4. **Integre les moments de demo** dans le flow narratif
5. **Inclus une section business** convaincante avec des chiffres de marche
6. **Termine avec une vision future** ambitieuse mais realiste
7. Si possible, **sugere des visuels** (diagrammes, schemas) a inclure dans les slides

**Ton cible** : Professionnel, passionne, maitrise technique demontree, mais pas condescendant. Comme un pitch de startup tech devant des investisseurs/professeurs impressionnes.

**Duree** : 15-20 minutes de presentation + 5 minutes de demo live + 5 minutes de Q&A

---
