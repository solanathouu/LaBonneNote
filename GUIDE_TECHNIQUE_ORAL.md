# Guide Technique LaBonneNote - Preparation Oral

> Ce document explique **chaque fichier, chaque fonction, chaque concept** pour que tu puisses repondre a toutes les questions techniques lors de ta soutenance.

---

## TABLE DES MATIERES

1. [Vue d'ensemble : le pipeline RAG](#1-vue-densemble--le-pipeline-rag)
2. [Le Scraping (collecte des donnees)](#2-le-scraping-collecte-des-donnees)
3. [Le Nettoyage (cleaner.py)](#3-le-nettoyage-cleanerpy)
4. [Le Chunking (chunker.py)](#4-le-chunking-chunkerpy)
5. [L'Ingestion ChromaDB (ingest_chromadb.py)](#5-lingestion-chromadb-ingest_chromadbpy)
6. [La Chaine RAG (rag.py) - LE COEUR](#6-la-chaine-rag-ragpy---le-coeur)
7. [Les Prompts (prompts.py)](#7-les-prompts-promptspy)
8. [La Detection automatique (detection.py)](#8-la-detection-automatique-detectionpy)
9. [Le Service PDF (pdf_service.py)](#9-le-service-pdf-pdf_servicepy)
10. [Le Service Quiz (quiz_service.py)](#10-le-service-quiz-quiz_servicepy)
11. [L'API FastAPI (main.py)](#11-lapi-fastapi-mainpy)
12. [Glossaire des concepts cles](#12-glossaire-des-concepts-cles)
13. [Questions probables du jury et reponses](#13-questions-probables-du-jury-et-reponses)

---

## 1. Vue d'ensemble : le pipeline RAG

```
PHASE 1 : PREPARATION (une seule fois)
========================================

  Vikidia.org                    data/raw/           data/processed/          chromadb/
  (24 321 articles)              (JSON brut)         (JSON chunks)            (base vectorielle)
       |                             |                     |                       |
       v                             v                     v                       v
  [SCRAPER]  ------>  [CLEANER]  ------>  [CHUNKER]  ------>  [INGESTION]
  vikidia.py          cleaner.py          chunker.py          ingest_chromadb.py
  API MediaWiki       Regex/nettoyage     500 tokens/chunk    OpenAI Embeddings
  cloudscraper        Suppression LaTeX   Overlap 50 tokens   → vecteurs 1536 dim
                      Suppression Wiki                        Stockage ChromaDB


PHASE 2 : UTILISATION (a chaque question)
==========================================

  Eleve tape             Backend              ChromaDB             OpenAI GPT-4o-mini
  une question           FastAPI              (recherche)          (generation)
       |                    |                     |                       |
       v                    v                     v                       v
  [FRONTEND]  --->  [API /chat]  --->  [RETRIEVE]  --->  [GENERATE]  --->  Reponse
  app.js            main.py            rag.py             rag.py           + sources
                    detection.py       similarity_search   prompt + LLM
```

**En une phrase** : On scrape des articles, on les decoupe en morceaux, on les transforme en vecteurs numeriques, et quand un eleve pose une question, on cherche les morceaux les plus proches puis on demande au LLM de repondre UNIQUEMENT avec ces morceaux.

---

## 2. Le Scraping (collecte des donnees)

### Fichier : `scraper/vikidia.py`

**But** : Collecter les 24 321 articles de Vikidia organises par matiere scolaire.

### Classe `VikidiaScraper`

#### `__init__(self, dossier_sortie)`
- Cree le dossier de sortie (`data/raw/vikidia/`)
- Initialise `cloudscraper.create_scraper()` : c'est comme `requests` mais il bypass automatiquement la protection **Cloudflare** (anti-bot). Vikidia utilise Cloudflare, donc `requests` seul serait bloque avec une erreur 403.
- Initialise un `set()` `articles_vus` pour eviter les **doublons** (un article peut etre dans 2 categories)

#### `scraper_tout(self)` → liste d'articles
- Boucle sur `CATEGORIES_RACINES` (defini dans `metadata.py`) : 8 matieres, chacune avec ses categories Vikidia racines
- Pour chaque matiere, appelle `_scraper_categorie()` pour chaque categorie
- Sauvegarde les articles bruts en JSON par matiere

#### `_scraper_categorie(self, categorie, matiere, profondeur)` → liste d'articles
- **Recursion** : explore une categorie ET ses sous-categories (profondeur max = 3)
- Verifie si la categorie est dans la liste noire (`est_categorie_ignoree()`) pour eviter les categories inutiles (ex: "Categorie:Mathematicien")
- Appelle `_lister_pages_categorie()` pour obtenir les titres d'articles
- Pour chaque article non encore vu, appelle `_extraire_article()`
- Puis explore les sous-categories recursivement

#### `_lister_pages_categorie(self, categorie, type_page)` → liste de titres
- **C'est ici qu'on parle a l'API MediaWiki**
- Requete GET vers `https://fr.vikidia.org/w/api.php` avec :
  - `action=query` : on veut interroger l'API
  - `list=categorymembers` : on veut les membres d'une categorie
  - `cmtype=page` ou `subcat` : articles ou sous-categories
  - `cmlimit=50` : 50 resultats par page (max autorise)
  - `format=json` : reponse en JSON
- **Pagination** : l'API retourne un champ `continue` s'il y a plus de 50 resultats. On re-fait la requete avec `cmcontinue` pour avoir la suite.
- `time.sleep(DELAI_REQUETE)` : on attend 1 seconde entre chaque requete pour ne pas surcharger le serveur (politesse du scraping)

#### `_extraire_article(self, titre, matiere, categorie)` → dict ou None
- Requete GET avec :
  - `prop=extracts` : on veut le contenu texte de la page
  - `explaintext=1` : texte brut (pas de HTML)
  - `redirects=1` : suivre les redirections
- Filtre les articles trop courts (< 50 caracteres)
- Construit l'URL (`https://fr.vikidia.org/wiki/Titre_Article`)
- Attache les **metadonnees** via `creer_metadata()` : source, matiere, titre, url, categorie

### Fichier : `scraper/metadata.py`

**But** : Mapper les categories Vikidia aux matieres scolaires + filtrer les categories inutiles.

#### `CATEGORIES_RACINES` (dict)
- Definit les categories de depart pour chaque matiere
- Ex: `"mathematiques": ["Categorie:Mathematiques"]`
- Ex: `"histoire_geo": ["Categorie:Histoire", "Categorie:Geographie"]`

#### `CATEGORIES_MATIERES` (dict)
- Mapping de ~60 categories Vikidia vers 8 matieres
- Ex: `"Categorie:Algebre"` → `"mathematiques"`

#### `CATEGORIES_IGNOREES` (set)
- Categories a ne pas explorer (biographies de scientifiques, images, quiz existants...)
- Ex: `"Categorie:Mathematicien"`, `"Categorie:Physicien"`, `"Categorie:Astronomie"`

#### `creer_metadata(source, matiere, titre, url, categorie, niveau)` → dict
- Cree un dictionnaire standardise avec toutes les infos d'un article
- Ce dict sera attache a chaque chunk pour le filtrage dans ChromaDB

---

## 3. Le Nettoyage (`cleaner.py`)

**But** : Transformer le texte brut MediaWiki en texte propre, lisible et pret pour le chunking.

### `nettoyer_texte(texte)` → texte propre
Enchaine 4 etapes de nettoyage :

#### Etape 1 : `_supprimer_sections(texte)`
- Supprime les sections non pedagogiques : "Voir aussi", "References", "Bibliographie", "Liens externes"
- Utilise des **regex** : `==+\s*Voir aussi\s*==+.*?(?===|\Z)`
  - `==+` : detecte les titres wiki (`== Titre ==`)
  - `.*?(?===|\Z)` : capture tout jusqu'au prochain titre ou la fin du texte
  - Flag `re.DOTALL` : le `.` capture aussi les retours a la ligne

#### Etape 2 : `_nettoyer_latex(texte)`
- Les articles de maths contiennent du LaTeX (`\frac{a}{b}`, `\displaystyle`, `\alpha`)
- 15+ patterns regex pour supprimer les commandes LaTeX
- Catch-all final : `\\[a-zA-Z]+` capture toute commande LaTeX restante
- Nettoie les accolades orphelines laissees par le nettoyage

#### Etape 3 : `_nettoyer_wiki(texte)`
- `={2,}\s*(.+?)\s*={2,}` → Transforme `== Titre ==` en juste `Titre`
- `<[^>]+>` → Supprime les balises HTML residuelles
- `\{\{[^}]*\}\}` → Supprime les modeles wiki (`{{citation|...}}`)
- `\[\[(?:[^|\]]*\|)?([^\]]*)\]\]` → `[[Lien|Texte affiché]]` devient `Texte affiché`
- `^\*+\s*` → Transforme les puces wiki (`* item`) en tirets (`- item`)

#### Etape 4 : `_normaliser_espaces(texte)`
- Espaces multiples → un seul espace
- 3+ sauts de ligne → 2 sauts de ligne
- Espaces en debut/fin de ligne supprimes

---

## 4. Le Chunking (`chunker.py`)

**But** : Decouper un article en morceaux de ~500 tokens avec chevauchement.

### Pourquoi chunker ?
- Les modeles d'embedding ont une **limite de tokens** (8191 pour text-embedding-3-small)
- Un article peut faire 10 000 tokens → il faut le decouper
- Des chunks de ~500 tokens donnent la meilleure precision en recherche : assez de contexte mais assez specifiques

### Constantes
```python
CHARS_PAR_TOKEN = 4          # 1 token ≈ 4 caracteres en francais
TAILLE_CHUNK_TOKENS = 500    # Taille cible
OVERLAP_TOKENS = 50          # Chevauchement entre chunks
TAILLE_CHUNK_CHARS = 2000    # 500 * 4
OVERLAP_CHARS = 200          # 50 * 4
TAILLE_MIN_CHUNK_CHARS = 100 # Minimum pour garder un chunk
```

### `decouper_en_chunks(texte, titre)` → liste de dicts
1. Si texte < 100 caracteres → retourne un seul chunk (ou rien)
2. Decoupe par **paragraphes** (`\n\n`) d'abord (decoupe naturelle)
3. Accumule dans un buffer jusqu'a depasser 2000 chars
4. Si un paragraphe seul depasse 2000 chars → `_decouper_par_phrases()`
5. Ajoute le titre en prefixe de chaque chunk : `[Titre de l'article]\nContenu...`

### `_decouper_par_phrases(texte)` → liste de strings
- Decoupe par `(?<=[.!?])\s+` : coupe apres un point/exclamation/interrogation suivi d'un espace
- Meme logique de buffer que la fonction principale

### `_extraire_overlap(texte)` → string
- Prend les 200 derniers caracteres du chunk precedent
- **Pourquoi l'overlap ?** Pour ne pas perdre le contexte a la frontiere entre 2 chunks. Si une phrase est coupee entre 2 chunks, l'overlap garantit qu'elle apparait dans les deux.
- Coupe au dernier espace pour ne pas couper un mot en plein milieu

### `_prepend_titre(texte, titre)` → string
- Ajoute `[Titre]\n` au debut de chaque chunk
- **Pourquoi ?** Pour que l'embedding du chunk "sache" de quel article il vient. Quand on cherchera "Pythagore", le chunk aura `[Theoreme de Pythagore]` en prefixe, ce qui ameliore la pertinence de la recherche.

---

## 5. L'Ingestion ChromaDB (`ingest_chromadb.py`)

**But** : Prendre tous les chunks JSON et les stocker dans ChromaDB avec leurs embeddings.

### Pipeline d'ingestion

```
data/processed/           LangChain              OpenAI API           ChromaDB
(JSON chunks)             Document               (embedding)          (stockage)
     |                       |                       |                    |
     v                       v                       v                    v
load_all_chunks()  →  chunks_to_documents()  →  ingest_to_chromadb()
     |                       |                       |
  Lit les JSON         Convertit en objet       Appelle OpenAI pour
  depuis chaque        Document(page_content,   chaque batch de 100
  matiere              metadata)                docs, stocke dans
                                                chromadb/
```

### `load_all_chunks()` → liste de dicts
- Parcourt `data/processed/*/chunks.json`
- Charge et concatene tous les chunks de toutes les matieres

### `chunks_to_documents(chunks)` → liste de Documents
- Convertit chaque chunk en objet `Document` de LangChain
- `Document(page_content="texte...", metadata={source, matiere, titre, url...})`
- **C'est le format standard de LangChain** : `page_content` = le texte, `metadata` = les infos associees

### `ingest_to_chromadb(documents, batch_size=100)`
- Initialise `OpenAIEmbeddings(model="text-embedding-3-small")`
  - Ce modele transforme du texte en **vecteur de 1536 dimensions**
  - Chaque dimension est un nombre decimal (float)
  - Le vecteur capture le **sens semantique** du texte
- Cree/charge ChromaDB avec `Chroma(collection_name, embedding_function, persist_directory)`
  - `collection_name="cours_college"` : nom de la collection (comme une "table" en SQL)
  - `embedding_function=embeddings` : ChromaDB appellera automatiquement OpenAI pour vectoriser
  - `persist_directory` : stocke sur disque (pas en memoire)
- `vector_store.add_documents(batch)` : pour chaque batch de 100 documents :
  1. ChromaDB envoie les 100 textes a OpenAI
  2. OpenAI retourne 100 vecteurs de 1536 dimensions
  3. ChromaDB stocke les vecteurs + textes + metadonnees sur disque

### Que contient ChromaDB apres ingestion ?
```
Collection "cours_college" :
  - 43 857 documents
  - Chacun a : un vecteur (1536 floats), un texte, des metadonnees
  - Index optimise pour la recherche par similarite cosinus
```

---

## 6. La Chaine RAG (`rag.py`) - LE COEUR

**C'est le fichier le plus important.** Il fait le lien entre la question de l'eleve et la reponse.

### Classe `RAGChain`

#### `__init__(self, ...)`
Initialise 4 composants :

1. **`self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")`**
   - Meme modele que pour l'ingestion (OBLIGATOIRE : il faut le meme modele pour que la recherche fonctionne)
   - Sera utilise pour transformer la question de l'eleve en vecteur

2. **`self.vector_store = Chroma(collection_name="cours_college", ...)`**
   - Se connecte a la collection principale (Vikidia, 43 857 chunks)
   - `embedding_function=self.embeddings` : LangChain l'utilise pour vectoriser les queries

3. **`self.vector_store_personal = Chroma(collection_name="mes_cours", ...)`**
   - Deuxieme collection pour les PDFs uploades par l'utilisateur
   - Meme embeddings, meme base ChromaDB, collection differente

4. **`self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)`**
   - `temperature=0.3` : basse = reponses factuelles et coherentes. Haute (1.0) = plus creatif mais moins fiable.
   - GPT-4o-mini : modele rapide et pas cher (~0.15$/1M tokens en input)

#### `is_general_question(self, question)` → bool
- Detecte les messages non-scolaires : "salut", "merci", "qui es-tu", "ca va"
- **Pourquoi ?** Pour ne pas gaspiller un appel API (embedding + LLM) pour un simple "bonjour"
- Logique : si le message < 15 caracteres ET contient un pattern general → True
- Ou si le message est exactement un pattern general → True

#### `retrieve(self, question, matiere, niveau, source)` → liste de Documents

**C'est la premiere moitie du RAG : le R (Retrieval).**

```
Question de l'eleve : "C'est quoi le theoreme de Pythagore ?"
                           |
                           v
          OpenAI text-embedding-3-small
                           |
                           v
          Vecteur [0.023, -0.087, 0.142, ..., 0.056]  (1536 nombres)
                           |
                           v
          ChromaDB : similarity_search_with_score()
          Compare ce vecteur avec les 43 857 vecteurs stockes
          Retourne les 5 plus proches (top_k=5)
                           |
                           v
          [Doc1: "Theoreme de Pythagore" (score: 0.12)]
          [Doc2: "Triangle rectangle" (score: 0.28)]
          [Doc3: "Geometrie euclidienne" (score: 0.35)]
          [Doc4: "Pythagore (mathematicien)" (score: 0.41)]
          [Doc5: "Trigonometrie" (score: 0.52)]
```

**Etapes detaillees** :
1. Construit les filtres de metadonnees (`matiere`, `niveau`) si fournis
2. Selon le parametre `source` :
   - `"vikidia"` → cherche dans `self.vector_store` (collection Vikidia)
   - `"mes_cours"` → cherche dans `self.vector_store_personal` (collection PDFs)
   - `"tous"` → cherche dans les deux, fusionne, trie par score, garde les top 5
3. `similarity_search_with_score(question, k=5, filter=filters)` :
   - LangChain vectorise la question via OpenAI
   - ChromaDB calcule la **distance cosinus** entre le vecteur de la question et chaque vecteur de la collection
   - Retourne les 5 documents avec la plus petite distance (= plus similaires)
   - Le score est une **distance** : 0 = identique, 2 = completement different
4. Retourne la liste de `Document` (avec `page_content` et `metadata`)

#### `generate(self, question, documents, niveau)` → string

**C'est la deuxieme moitie du RAG : le G (Generation).**

```
5 documents recuperes + question + niveau
                |
                v
        Construire le contexte :
        "[Source 1] Theoreme de Pythagore (mathematiques)
         Dans un triangle rectangle, le carre de l'hypotenuse..."
        ---
        "[Source 2] Triangle rectangle (mathematiques)
         Un triangle rectangle est un triangle qui possede..."
                |
                v
        Construire le prompt complet via get_prompt()
        (adapte au niveau de l'eleve)
                |
                v
        self.llm.invoke(prompt)  →  GPT-4o-mini genere la reponse
                |
                v
        "Le theoreme de Pythagore dit que dans un triangle rectangle..."
```

**Etapes detaillees** :
1. Si `documents` est vide → retourne `REFUS_MESSAGE` ("Je ne trouve pas cette info dans mes cours")
2. Construit un string `context` en concatenant les 5 documents avec leurs metadonnees
3. Appelle `get_prompt(question, context, niveau)` pour construire le prompt adapte
4. `self.llm.invoke(prompt)` : envoie le prompt complet a GPT-4o-mini
5. Retourne `response.content` (le texte de la reponse)

**Pourquoi c'est mieux qu'un chatbot classique ?**
- Un chatbot classique utilise les connaissances du LLM → peut inventer des choses (hallucinations)
- Notre RAG donne au LLM UNIQUEMENT les documents de notre base → il ne peut repondre QUE depuis des sources verifiees
- Le prompt dit explicitement : "Ne jamais inventer ou utiliser tes connaissances generales"

#### `run(self, question, matiere, niveau, source)` → dict

**Fonction principale qui orchestre tout.**

```python
# 1. Question generale ? (salut, merci, etc.)
if self.is_general_question(question):
    return {"answer": "Salut ! ...", "sources": [], "nb_sources": 0}

# 2. Retrieval : chercher les documents pertinents
documents = self.retrieve(question, matiere, niveau, source)

# 3. Generation : produire la reponse
answer = self.generate(question, documents, niveau)

# 4. Deduplication des sources (1 lien par article, pas 5x le meme)
seen_titles = set()
sources = []
for doc in documents:
    titre = doc.metadata.get("titre", ...)
    if titre in seen_titles:
        continue           # Skip les doublons
    seen_titles.add(titre)
    sources.append({...})  # titre, url, matiere, source

# 5. Retourner le resultat
return {"answer": answer, "sources": sources, "nb_sources": len(sources)}
```

#### `get_all_lessons(self, matiere, niveau, limit)` → liste de dicts
- Utilise `collection.get(where=filters, limit=100000)` pour obtenir TOUS les chunks d'une matiere
- **Attention** : `collection.get()` est different de `similarity_search()` :
  - `get()` = requete par metadonnees (filtre exact, comme SQL WHERE)
  - `similarity_search()` = requete par vecteur (recherche semantique)
- Regroupe les chunks par `titre` (car un article a plusieurs chunks) dans un `dict` `lessons_map`
- Compte `nb_chunks` par lecon et prend les 200 premiers caracteres comme resume

#### `get_lesson_content(self, matiere, titre)` → dict ou None
- Recupere TOUS les chunks d'une lecon specifique (filtre matiere + titre)
- Concatene les chunks avec `"\n\n".join(chunks)` pour reconstruire le contenu complet
- Utilise `$and` de ChromaDB : `{"$and": [{"matiere": matiere}, {"titre": titre}]}`

---

## 7. Les Prompts (`prompts.py`)

**But** : Contraindre le LLM a repondre UNIQUEMENT depuis les documents fournis.

### `SYSTEM_PROMPT_BASE`
```
Tu es un assistant pedagogique pour les eleves de college en France.

REGLES STRICTES:
1. Tu dois repondre UNIQUEMENT en utilisant les informations fournies dans le contexte
2. Si l'information n'est pas dans le contexte, tu dois dire: "Je ne trouve pas cette information"
3. Ne jamais inventer ou utiliser tes connaissances generales
4. Toujours citer tes sources

CONTEXTE:
{context}     ← les 5 chunks recuperes

Question de l'eleve: {question}
```

### `PROMPTS_PAR_NIVEAU` (dict)
- 5 niveaux : `6eme`, `5eme`, `4eme`, `3eme`, `college`
- Chaque niveau ajoute un "STYLE DE REPONSE" autour du prompt de base
- 6eme : "vocabulaire simple, exemples concrets du quotidien"
- 3eme : "vocabulaire academique, prepare au lycee, synthese et argumentation"

### `get_prompt(question, context, niveau)` → string
```python
# 1. Injecte le contexte et la question dans le prompt de base
base_with_context = SYSTEM_PROMPT_BASE.format(context=context, question=question)

# 2. Enveloppe avec le prompt de niveau
niveau_prompt = PROMPTS_PAR_NIVEAU.get(niveau, PROMPTS_PAR_NIVEAU["college"])
final_prompt = niveau_prompt.format(base_prompt=base_with_context)
```

### `QUIZ_GENERATION_PROMPT`
- Prompt specialise pour generer des QCM en JSON
- Force le LLM a retourner du JSON strict (pas de texte avant/apres)
- Specifie : 4 options, 1 seule correcte, 3 distracteurs plausibles, explication

---

## 8. La Detection automatique (`detection.py`)

**But** : Deviner la matiere et le niveau scolaire depuis la question de l'eleve.

### `detect_matiere(question)` → dict
- Dictionnaire `KEYWORDS_BY_MATIERE` : ~25 mots-cles par matiere
  - Ex maths : "theoreme", "equation", "fraction", "geometrie"...
  - Ex SVT : "cellule", "organe", "photosynthese", "volcan"...
- **Algorithme** : compter combien de mots-cles matchent pour chaque matiere
- Si une matiere a clairement plus de matches → `matiere_principale`
- Si 2 matieres ont des scores proches (ecart <= 1) → `ambigue: true` + `matieres_possibles`
- Si aucun match → `matiere_principale: null`

### `detect_niveau(question)` → string
- **Explicite** : si la question contient "6eme", "cinquieme", "brevet" → retourne directement
- **Heuristique** : sinon, estime via la complexite de la question
  - Nombre de mots + longueur moyenne des mots
  - < 8 mots courts → 6eme
  - < 12 mots → 5eme
  - < 16 mots → 4eme
  - 16+ mots → 3eme

### `auto_detect(question)` → dict
- Combine `detect_niveau()` + `detect_matiere()`
- Retourne un dict avec `niveau_detecte`, `matiere_detectee`, `matieres_possibles`, `ambigue`

---

## 9. Le Service PDF (`pdf_service.py`)

**But** : Permettre a l'utilisateur d'importer ses propres cours en PDF.

### Classe `PDFService`

#### `__init__(...)`
- Cree le dossier `data/user_pdfs/`
- Initialise les embeddings OpenAI (meme modele que pour Vikidia)
- Se connecte a la collection ChromaDB `"mes_cours"` (separee de `"cours_college"`)
- Cree un `RecursiveCharacterTextSplitter` de LangChain :
  - `chunk_size=500` : taille cible en **caracteres** (pas tokens ici)
  - `chunk_overlap=50` : chevauchement
  - `separators=["\n\n", "\n", ". ", " ", ""]` : essaie de couper d'abord par paragraphes, puis par lignes, puis par phrases, puis par mots, puis par caracteres

#### `save_pdf(file_content, filename)` → chemin
- Sauvegarde le fichier binaire avec un timestamp pour eviter les conflits de noms

#### `process_pdf(file_path)` → dict
```python
# 1. Charger le PDF page par page
loader = PyPDFLoader(file_path)       # LangChain: extrait le texte de chaque page
documents = loader.load()              # → Liste de Document (1 par page)

# 2. Chunker les documents
chunks = self.text_splitter.split_documents(documents)  # → chunks de ~500 chars

# 3. Ajouter les metadonnees
for chunk in chunks:
    chunk.metadata.update({
        "filename": "mon_cours.pdf",
        "source": "pdf_personnel",
        "chunk_index": i,
        "uploaded_at": "2026-02-18T..."
    })

# 4. Ajouter a ChromaDB
self.vector_store.add_documents(chunks)  # Vectorise + stocke automatiquement
```

**Difference avec le scraper** :
- Le scraper utilise notre propre `chunker.py` (decoupe par paragraphes)
- Le PDF service utilise `RecursiveCharacterTextSplitter` de LangChain (plus generique, gere bien les PDF)
- Les deux finissent dans ChromaDB, mais dans des **collections differentes**

---

## 10. Le Service Quiz (`quiz_service.py`)

**But** : Generer automatiquement des QCM a partir du contenu d'une lecon.

### Classe `QuizService`

#### `__init__(self, rag_chain)`
- Recoit le `RAGChain` pour acceder au contenu des lecons
- Cree un `ChatOpenAI(temperature=0.7)` : temperature plus haute que le chat (0.3) car on veut de la **variete** dans les questions generees

#### `generate_quiz(matiere, titre, nb_questions, niveau)` → dict (async)

```python
# 1. Recuperer le contenu complet de la lecon
lesson = self.rag_chain.get_lesson_content(matiere, titre)

# 2. Extraire les chunks (paragraphes >= 100 chars)
chunks = self._extract_chunks_from_lesson(lesson)

# 3. Selectionner des chunks espaces pour diversite
selected_chunks = self._select_diverse_chunks(chunks, nb_questions)

# 4. Generer les questions EN PARALLELE
tasks = [self._generate_question(chunk, niveau, i) for i, chunk in enumerate(selected)]
questions = await asyncio.gather(*tasks)   # ← Execute tous les appels LLM en meme temps !

# 5. Filtrer les questions valides
valid_questions = [q for q in questions if q is not None]

# 6. Retourner le quiz
return {"quiz_id": uuid4(), "questions": valid_questions, ...}
```

**Point cle : `asyncio.gather(*tasks)`**
- Au lieu d'appeler le LLM 5 fois en sequence (5 × 3 secondes = 15s), on lance les 5 appels **en parallele** (≈ 3-4s total)
- C'est possible car `self.llm.ainvoke()` est **asynchrone** (non-bloquant)

#### `_select_diverse_chunks(chunks, nb_questions)` → liste
- Si on a 20 chunks et on veut 5 questions, on prend les chunks aux positions 0, 4, 8, 12, 16
- **Pourquoi ?** Pour ne pas avoir 5 questions sur le meme paragraphe. On espace uniformement pour couvrir toute la lecon.

#### `_generate_question(chunk, niveau, index)` → dict (async)
```python
# 1. Construire le prompt avec le chunk comme contexte
prompt = QUIZ_GENERATION_PROMPT.format(context=chunk[:1000], niveau=niveau)

# 2. Appel asynchrone au LLM
response = await self.llm.ainvoke(prompt)

# 3. Nettoyer le JSON (enlever les backticks ```)
content = response.content.strip()
if content.startswith("```json"):
    content = content.replace("```json", "").replace("```", "")

# 4. Parser le JSON
question_data = json.loads(content)

# 5. Valider la structure (4 options, correct_answer 0-3, etc.)
if not self._validate_question_structure(question_data):
    return self._fallback_question(index)  # Question generique de secours

return question_data
```

#### `validate_answers(quiz_id, questions, answers)` → dict
- Compare chaque reponse de l'eleve avec la bonne reponse
- Calcule le score et le pourcentage
- Attribue un niveau : Excellent (80%+), Bien (60%+), Moyen (40%+), A revoir (<40%)

---

## 11. L'API FastAPI (`main.py`)

**But** : Exposer toutes les fonctionnalites via des endpoints HTTP.

### Demarrage
```python
@app.on_event("startup")
async def startup_event():
    rag_chain = RAGChain()          # Connecte a ChromaDB + OpenAI
    pdf_service = PDFService()      # Service PDF
    quiz_service = QuizService(rag_chain)  # Service Quiz (a besoin du RAG)
```

### Endpoints principaux

| Endpoint | Methode | Role |
|----------|---------|------|
| `/health` | GET | Verifier que l'API fonctionne |
| `/api/chat` | POST | Poser une question (RAG) |
| `/api/chat/auto` | POST | Chat avec auto-detection niveau/matiere |
| `/api/matieres` | GET | Liste des 8 matieres |
| `/api/niveaux` | GET | Liste des 5 niveaux |
| `/api/lecons/{matiere}` | GET | Liste des lecons d'une matiere |
| `/api/lecons/{matiere}/detail` | GET | Contenu complet d'une lecon |
| `/api/upload-pdf` | POST | Uploader un PDF |
| `/api/mes-cours` | GET | Liste des PDFs importes |
| `/api/mes-cours/{filename}` | DELETE | Supprimer un PDF |
| `/api/quiz/generate` | POST | Generer un quiz |
| `/api/quiz/validate` | POST | Valider les reponses d'un quiz |

### Validation Pydantic
```python
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)  # Obligatoire, non-vide
    niveau: Optional[str] = "college"         # Optionnel, defaut "college"
    matiere: Optional[str] = None             # Optionnel
    source: Optional[str] = "vikidia"         # Optionnel
```
- Pydantic valide automatiquement le JSON entrant
- Si `question` est vide → erreur 422 (Unprocessable Entity)
- Les types sont verifies (str, int, etc.)

### Servir le frontend
```python
app.mount("/", StaticFiles(directory="frontend/", html=True), name="frontend")
```
- FastAPI sert les fichiers statiques (HTML, CSS, JS) directement
- Pas besoin d'un serveur web separe (Nginx, Apache)

---

## 12. Glossaire des concepts cles

### Embedding (vecteur d'embedding)
- Representation numerique d'un texte sous forme de vecteur (liste de nombres)
- Modele utilise : `text-embedding-3-small` → vecteurs de **1536 dimensions**
- Textes similaires en sens → vecteurs proches dans l'espace a 1536 dimensions
- Ex: "chat" et "felin" auront des vecteurs proches

### Similarite cosinus (cosine similarity)
- Mesure de proximite entre 2 vecteurs (angle entre eux)
- 1.0 = identiques, 0 = aucun rapport, -1 = opposes
- ChromaDB utilise la **distance** (1 - similarite) : 0 = identique, 2 = oppose

### ChromaDB
- Base de donnees vectorielle open source
- Stocke : vecteur + texte + metadonnees
- Optimisee pour la recherche par similarite (ANN = Approximate Nearest Neighbors)
- Persistance sur disque (dossier `chromadb/`)

### LangChain
- Framework Python pour construire des applications avec des LLM
- On utilise 4 composants :
  - `OpenAIEmbeddings` : interface pour l'API d'embeddings OpenAI
  - `ChatOpenAI` : interface pour l'API de chat OpenAI (GPT-4o-mini)
  - `Chroma` : connecteur LangChain pour ChromaDB
  - `Document` : objet standard (page_content + metadata)
  - `PyPDFLoader` : charge un PDF en Documents LangChain
  - `RecursiveCharacterTextSplitter` : decoupe du texte intelligemment

### RAG (Retrieval-Augmented Generation)
- **R**etrieval : chercher les documents pertinents (embedding + similarite)
- **A**ugmented : augmenter le prompt du LLM avec ces documents
- **G**eneration : le LLM genere la reponse en se basant sur les documents
- **Avantage vs. chatbot classique** : reponses sourcees, pas d'hallucinations, base de connaissances controllable

### Token
- Unite de base pour les modeles de langage
- ≈ 4 caracteres en francais, ≈ 0.75 mots
- "Bonjour comment allez-vous" ≈ 6-7 tokens

### Temperature (LLM)
- Parametre de creativite du LLM (0.0 a 2.0)
- 0.0 = toujours la meme reponse (deterministe)
- 0.3 = peu creatif (notre chat, pour rester factuel)
- 0.7 = assez creatif (notre quiz, pour varier les questions)
- 1.0+ = tres creatif (risque d'incoherence)

### API MediaWiki
- API REST de Wikipedia/Vikidia pour acceder au contenu programmatiquement
- `action=query` : interroger la base
- `prop=extracts` : obtenir le contenu texte d'une page
- `list=categorymembers` : lister les pages d'une categorie
- Pagination avec `continue` / `cmcontinue`

### cloudscraper
- Librairie Python qui simule un vrai navigateur
- Resout les challenges JavaScript de Cloudflare automatiquement
- Utilise a la place de `requests` car Vikidia est protege par Cloudflare

---

## 13. Questions probables du jury et reponses

### Q: "Comment tu t'assures que le bot ne repond pas des betises ?"
**R**: Trois mecanismes :
1. Le prompt systeme interdit au LLM d'utiliser ses propres connaissances
2. Si aucun document pertinent n'est trouve dans ChromaDB, le bot retourne un message de refus ("Je ne trouve pas cette info dans mes cours")
3. Chaque reponse est accompagnee de sources verifiables (liens vers Vikidia)

### Q: "Pourquoi chunker en 500 tokens et pas plus ?"
**R**: C'est un compromis :
- Trop petit (100 tokens) → pas assez de contexte, le morceau est incomprehensible
- Trop grand (2000 tokens) → le morceau couvre trop de sujets, la recherche est moins precise
- 500 tokens (≈ 375 mots) → un paragraphe bien contextualise, assez precis pour la recherche

### Q: "Pourquoi ChromaDB et pas une base SQL classique ?"
**R**: Une base SQL fait de la recherche exacte (mot-cle, titre). ChromaDB fait de la recherche **semantique** : elle comprend le **sens**. Si l'eleve demande "comment fonctionne la respiration", ChromaDB trouve des documents sur "echanges gazeux" ou "poumons" meme si ces mots ne sont pas dans la question, car les embeddings capturent le sens.

### Q: "C'est quoi la difference entre ton scraper et un simple copier-coller ?"
**R**: Le scraper est **automatise et structure** :
1. Il navigue les categories automatiquement (recursion jusqu'a profondeur 3)
2. Il evite les doublons (set d'articles deja vus)
3. Il nettoie le texte (LaTeX, HTML, sections inutiles)
4. Il decoupe en chunks avec overlap
5. Il attache les metadonnees (matiere, source, URL)
6. Il respecte les limites du serveur (1 requete/seconde)
7. Il a traite 24 321 articles automatiquement

### Q: "Pourquoi text-embedding-3-small et pas un autre modele ?"
**R**:
- **Prix** : 0.02$/1M tokens (tres econome, on a 43 857 chunks)
- **Performance** : excellent pour la recherche semantique en francais
- **Taille** : 1536 dimensions (bon compromis qualite/stockage)
- **Alternative** : text-embedding-3-large (3072 dim, meilleur mais 2x plus cher)

### Q: "Comment fonctionne la recherche par similarite dans ChromaDB ?"
**R**:
1. La question est convertie en vecteur de 1536 nombres par OpenAI
2. ChromaDB compare ce vecteur avec les 43 857 vecteurs stockes
3. La comparaison utilise la **distance cosinus** (mesure de l'angle entre les vecteurs)
4. Les 5 vecteurs les plus proches sont retournes avec leur texte et metadonnees
5. C'est optimise : ChromaDB utilise des index ANN (Approximate Nearest Neighbors) pour ne pas comparer avec tous les vecteurs un par un

### Q: "Pourquoi le quiz utilise asyncio.gather() ?"
**R**: Pour generer 5 questions, il faut 5 appels a l'API OpenAI. Chaque appel prend ~3 secondes. En sequentiel : 5 × 3 = 15 secondes. Avec `asyncio.gather()`, les 5 appels partent en meme temps et on attend juste le plus lent : ~3-4 secondes total. C'est 4x plus rapide.

### Q: "Quel est le role de LangChain dans ton projet ?"
**R**: LangChain fournit 4 briques que j'assemble :
1. `OpenAIEmbeddings` : simplifie les appels a l'API d'embeddings
2. `ChatOpenAI` : simplifie les appels a l'API de chat GPT-4o-mini
3. `Chroma` : connecteur qui lie ChromaDB aux embeddings de facon transparente
4. `Document` : format standard pour representer un texte + ses metadonnees
5. `PyPDFLoader` : extraction de texte depuis un PDF
6. `RecursiveCharacterTextSplitter` : decoupe intelligente du texte

Sans LangChain, il faudrait coder tout ca a la main (appels HTTP, gestion des tokens, batch, etc.).

### Q: "Ton bot peut-il se tromper ?"
**R**: Oui, dans 2 cas :
1. **Mauvais retrieval** : si ChromaDB retourne des documents pas pertinents (question ambigue, pas assez de donnees sur le sujet)
2. **Mauvaise generation** : si le LLM interprete mal les documents fournis (rare avec le prompt strict)
Mais il ne peut PAS inventer des faits : il ne repond que depuis les documents fournis.

### Q: "Pourquoi tu as choisi GPT-4o-mini ?"
**R**: Compromis optimal pour un chatbot scolaire :
- **Rapide** : reponse en 1-2 secondes
- **Pas cher** : ~0.15$/1M tokens (vs 2.50$ pour GPT-4o)
- **Suffisamment intelligent** : pour synthetiser des documents et adapter au niveau scolaire, il est largement suffisant
- **Pas besoin du meilleur modele** : le RAG fournit deja les bonnes informations, le LLM n'a qu'a les reformuler

### Q: "Comment tu geres les PDFs de l'utilisateur ?"
**R**: Pipeline en 4 etapes :
1. **Upload** : le PDF est sauvegarde sur disque avec un timestamp
2. **Extraction** : `PyPDFLoader` extrait le texte page par page
3. **Chunking** : `RecursiveCharacterTextSplitter` decoupe en morceaux de 500 chars
4. **Ingestion** : les chunks sont vectorises et ajoutes dans la collection ChromaDB `"mes_cours"` (separee de Vikidia)
Ensuite l'eleve peut choisir de chercher dans Vikidia seul, ses PDFs seuls, ou les deux fusionnes.

### Q: "C'est quoi l'overlap et pourquoi c'est important ?"
**R**: L'overlap c'est le fait de repeter les 50 derniers tokens du chunk precedent au debut du chunk suivant. Imagine un article qui dit "Le theoreme de Pythagore. Dans un triangle rectangle, le carre de l'hypotenuse est egal a la somme des carres des deux autres cotes." Si on coupe pile apres "Pythagore.", le chunk 2 commence par "Dans un triangle rectangle..." et perd le contexte. Avec l'overlap, le chunk 2 contient aussi "Le theoreme de Pythagore" au debut.

---

## Recapitulatif : ce qu'il faut retenir absolument

1. **RAG = Retrieval + Augmented Generation** : chercher les docs, les injecter dans le prompt, generer la reponse
2. **Embedding = representer du texte en vecteurs de nombres** pour comparer leur sens
3. **ChromaDB = base vectorielle** optimisee pour la recherche par similarite
4. **Le prompt interdit au LLM d'inventer** : il ne peut repondre que depuis les documents fournis
5. **Le scraper collecte automatiquement** 24 321 articles en naviguant les categories recursives
6. **Le chunking** decoupe en morceaux de 500 tokens avec overlap pour la precision de recherche
7. **LangChain** fournit les briques (Embeddings, LLM, ChromaDB connector, PDF loader, Text splitter)
8. **FastAPI** expose tout via des endpoints REST
9. **asyncio.gather** accelere le quiz en generant les questions en parallele
