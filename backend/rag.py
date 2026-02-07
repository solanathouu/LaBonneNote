"""Chaîne RAG LangChain: retrieval + generation."""

import logging
from typing import List, Dict, Optional

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document

from prompts import get_prompt, REFUS_MESSAGE

logger = logging.getLogger(__name__)

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
CHROMA_DIR = "../chromadb"  # Relatif au dossier backend -> remonte à la racine
COLLECTION_NAME = "cours_college"
SIMILARITY_THRESHOLD = 0.3  # Seuil minimum de similarité
TOP_K = 5  # Nombre de chunks à récupérer


class RAGChain:
    """Chaîne RAG complète: retrieval depuis ChromaDB + generation via OpenAI."""

    def __init__(
        self,
        chroma_dir: str = CHROMA_DIR,
        embedding_model: str = EMBEDDING_MODEL,
        llm_model: str = LLM_MODEL,
        top_k: int = TOP_K,
        similarity_threshold: float = SIMILARITY_THRESHOLD
    ):
        """Initialise la chaîne RAG.

        Args:
            chroma_dir: Chemin vers la base ChromaDB.
            embedding_model: Modèle d'embedding OpenAI.
            llm_model: Modèle LLM OpenAI.
            top_k: Nombre de chunks à récupérer.
            similarity_threshold: Seuil minimum de similarité.
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.chroma_dir = chroma_dir

        # Initialiser embeddings
        logger.info(f"Initialisation embeddings: {embedding_model}")
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        # Initialiser ChromaDB - Collection Vikidia
        logger.info(f"Connexion à ChromaDB: {chroma_dir}")
        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=chroma_dir
        )

        # Initialiser ChromaDB - Collection Mes Cours
        self.vector_store_personal = Chroma(
            collection_name="mes_cours",
            embedding_function=self.embeddings,
            persist_directory=chroma_dir
        )

        # Initialiser LLM
        logger.info(f"Initialisation LLM: {llm_model}")
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.3,  # Peu créatif, reste sur les faits
        )

        logger.info("RAG Chain initialisée avec succès")

    def is_general_question(self, question: str) -> bool:
        """Détecte si une question est générale (salutations, politesse) ou thématique.

        Args:
            question: La question de l'utilisateur.

        Returns:
            True si c'est une question générale, False si c'est thématique.
        """
        question_lower = question.lower().strip()

        # Mots-clés pour questions générales (salutations, politesse, etc.)
        general_patterns = [
            # Salutations
            "salut", "bonjour", "bonsoir", "coucou", "hello", "hi", "hey",
            # Questions sur le bot
            "qui es-tu", "qui es tu", "c'est quoi", "c est quoi", "comment tu",
            "tu fais quoi", "tu es qui", "ton nom", "que fais-tu", "que fais tu",
            # Politesse
            "merci", "merci beaucoup", "d'accord", "d accord", "ok", "okay",
            "au revoir", "bye", "à bientôt", "a bientot", "à plus", "a plus",
            # Questions très courtes sans contexte scolaire
            "ça va", "ca va", "comment vas-tu", "comment vas tu", "quoi de neuf"
        ]

        # Si la question est très courte (< 15 caractères) et contient un pattern général
        if len(question_lower) < 15:
            for pattern in general_patterns:
                if pattern in question_lower:
                    return True

        # Si la question est exactement un pattern général
        for pattern in general_patterns:
            if question_lower == pattern or question_lower == pattern + "?" or question_lower == pattern + " !":
                return True

        return False

    def retrieve(
        self,
        question: str,
        matiere: Optional[str] = None,
        niveau: Optional[str] = None,
        source: str = "vikidia"
    ) -> List[Document]:
        """Récupère les chunks pertinents depuis ChromaDB.

        Args:
            question: Question de l'élève.
            matiere: Filtre optionnel par matière.
            niveau: Filtre optionnel par niveau.
            source: Source des documents ("vikidia", "mes_cours", "tous").

        Returns:
            Liste de documents pertinents.
        """
        # Construire les filtres de métadonnées (seulement pour Vikidia)
        filters = {}
        if matiere and source != "mes_cours":
            filters["matiere"] = matiere
        if niveau and niveau != "college" and source != "mes_cours":
            # Chercher niveau exact OU college (fallback)
            # Note: ChromaDB ne supporte pas OR, donc on fait 2 requêtes
            pass

        # Recherche de similarité selon la source
        all_results = []

        if source == "vikidia" or source == "tous":
            # Rechercher dans Vikidia
            if filters:
                results = self.vector_store.similarity_search_with_score(
                    question,
                    k=self.top_k,
                    filter=filters
                )
            else:
                results = self.vector_store.similarity_search_with_score(
                    question,
                    k=self.top_k
                )
            all_results.extend(results)
            logger.info(f"Vikidia: {len(results)} résultats")

        if source == "mes_cours" or source == "tous":
            # Rechercher dans Mes Cours
            results_personal = self.vector_store_personal.similarity_search_with_score(
                question,
                k=self.top_k
            )
            all_results.extend(results_personal)
            logger.info(f"Mes Cours: {len(results_personal)} résultats")

        # Si "tous", limiter au top_k global et trier par score
        if source == "tous":
            all_results.sort(key=lambda x: x[1])  # Trier par score (ascending = meilleur)
            all_results = all_results[:self.top_k]

        # Filtrer par seuil de similarité
        # Note: ChromaDB retourne distance (plus petit = plus similaire)
        # On garde seulement les résultats pertinents
        filtered_docs = []
        for doc, score in all_results:
            source_label = doc.metadata.get('source', 'unknown')
            titre = doc.metadata.get('titre', doc.metadata.get('filename', 'Sans titre'))
            logger.debug(f"Document trouvé (score: {score:.3f}, source: {source_label}): {titre}")
            filtered_docs.append(doc)

        logger.info(f"Retrieval ({source}): {len(filtered_docs)} chunks pertinents trouvés")
        return filtered_docs

    def generate(
        self,
        question: str,
        documents: List[Document],
        niveau: str = "college"
    ) -> str:
        """Génère la réponse en utilisant les documents et le LLM.

        Args:
            question: Question de l'élève.
            documents: Documents récupérés (contexte).
            niveau: Niveau scolaire pour adapter le langage.

        Returns:
            Réponse générée par le LLM.
        """
        if not documents:
            logger.warning("Aucun document pertinent trouvé")
            return REFUS_MESSAGE

        # Construire le contexte à partir des documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            titre = doc.metadata.get("titre", "Sans titre")
            source = doc.metadata.get("source", "")
            matiere = doc.metadata.get("matiere", "")

            context_parts.append(
                f"[Source {i}] {titre} ({matiere})\n{doc.page_content}\n"
            )

        context = "\n---\n".join(context_parts)

        # Construire le prompt avec niveau adapté
        prompt = get_prompt(question, context, niveau)

        # Appeler le LLM
        logger.info(f"Génération de la réponse (niveau: {niveau})")
        response = self.llm.invoke(prompt)

        return response.content

    def run(
        self,
        question: str,
        matiere: Optional[str] = None,
        niveau: str = "college",
        source: str = "vikidia"
    ) -> Dict[str, any]:
        """Exécute la chaîne RAG complète.

        Args:
            question: Question de l'élève.
            matiere: Filtre optionnel par matière.
            niveau: Niveau scolaire (6eme, 5eme, 4eme, 3eme, college).
            source: Source des documents ("vikidia", "mes_cours", "tous").

        Returns:
            Dict avec la réponse et les sources.
        """
        logger.info(f"RAG Query: '{question}' (matiere={matiere}, niveau={niveau}, source={source})")

        # Vérifier si c'est une question générale (salutations, etc.)
        if self.is_general_question(question):
            logger.info("Question générale détectée - réponse sans sources")

            # Réponses amicales pour questions générales
            general_responses = {
                "salut": "Salut ! 👋 Je suis ton assistant scolaire. Pose-moi des questions sur tes cours de collège (maths, français, histoire-géo, SVT, physique-chimie, etc.) et je t'aiderai avec plaisir !",
                "bonjour": "Bonjour ! 😊 Je suis là pour t'aider avec tes cours de collège. N'hésite pas à me poser des questions sur les matières que tu étudies !",
                "merci": "De rien ! 😊 N'hésite pas si tu as d'autres questions sur tes cours !",
                "ça va": "Je vais bien, merci ! 😊 Et toi, as-tu des questions sur tes cours ? Je suis là pour t'aider !",
                "qui es-tu": "Je suis un assistant scolaire qui t'aide avec tes cours de collège ! 📚 Je peux répondre à tes questions sur toutes les matières : maths, français, histoire-géo, SVT, physique-chimie, technologie, anglais et espagnol. Pose-moi une question !",
            }

            # Trouver une réponse appropriée
            question_lower = question.lower().strip()
            answer = None
            for key, response in general_responses.items():
                if key in question_lower:
                    answer = response
                    break

            # Réponse par défaut si aucun match
            if not answer:
                answer = "Bonjour ! 😊 Je suis ton assistant scolaire pour le collège. Pose-moi des questions sur tes cours et je t'aiderai !"

            return {
                "answer": answer,
                "sources": [],
                "nb_sources": 0
            }

        # Question thématique : procéder avec le RAG normal
        # 1. Retrieval
        documents = self.retrieve(question, matiere, niveau, source)

        # 2. Generation
        answer = self.generate(question, documents, niveau)

        # 3. Préparer les sources
        sources = []
        for doc in documents:
            # Déterminer le titre selon la source
            titre = doc.metadata.get("titre", doc.metadata.get("filename", "Sans titre"))

            sources.append({
                "titre": titre,
                "url": doc.metadata.get("url", ""),
                "matiere": doc.metadata.get("matiere", ""),
                "source": doc.metadata.get("source", ""),
                "filename": doc.metadata.get("filename", ""),
                "page": doc.metadata.get("page", 0)
            })

        return {
            "answer": answer,
            "sources": sources,
            "nb_sources": len(sources)
        }

    def get_all_lessons(
        self,
        matiere: str,
        niveau: Optional[str] = None,
        limit: int = 50000
    ) -> List[Dict[str, any]]:
        """Récupère la liste de toutes les leçons disponibles pour une matière.

        Args:
            matiere: Matière à filtrer.
            niveau: Niveau optionnel (6eme, 5eme, 4eme, 3eme).
            limit: Nombre maximum de leçons à retourner (défaut: 50000 pour tout récupérer).

        Returns:
            Liste de dicts avec titre, url, resume, niveau, nb_chunks.
        """
        logger.info(f"Fetching lessons: matiere={matiere}, niveau={niveau}")

        # Construire le filtre avec opérateur ChromaDB
        if niveau and niveau != "college":
            # Filtrer par matière ET niveau
            filters = {
                "$and": [
                    {"matiere": {"$eq": matiere}},
                    {"niveau": {"$eq": niveau}}
                ]
            }
        else:
            # Filtrer uniquement par matière
            filters = {"matiere": {"$eq": matiere}}

        # Récupérer tous les documents de la matière (sans query spécifique)
        # On utilise une query générique pour obtenir tous les docs
        try:
            collection = self.vector_store._collection
            results = collection.get(
                where=filters,
                limit=100000  # Récupère beaucoup de chunks (plusieurs par leçon)
            )
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des leçons: {e}")
            return []

        # Grouper par titre (chaque leçon a plusieurs chunks)
        lessons_map = {}
        if results and results.get("metadatas"):
            for metadata, doc_id in zip(results["metadatas"], results["ids"]):
                titre = metadata.get("titre", "Sans titre")
                if titre not in lessons_map:
                    # Prendre les 200 premiers caractères comme résumé
                    page_content = results["documents"][results["ids"].index(doc_id)]
                    resume = page_content[:200] + "..." if len(page_content) > 200 else page_content

                    lessons_map[titre] = {
                        "titre": titre,
                        "url": metadata.get("url", ""),
                        "resume": resume,
                        "matiere": metadata.get("matiere", ""),
                        "niveau": metadata.get("niveau", "college"),
                        "source": metadata.get("source", ""),
                        "nb_chunks": 1
                    }
                else:
                    lessons_map[titre]["nb_chunks"] += 1

        # Convertir en liste et trier par titre
        lessons = sorted(lessons_map.values(), key=lambda x: x["titre"])
        logger.info(f"Found {len(lessons)} unique lessons")

        return lessons[:limit]

    def get_lesson_content(
        self,
        matiere: str,
        titre: str
    ) -> Optional[Dict[str, any]]:
        """Récupère le contenu complet d'une leçon spécifique.

        Args:
            matiere: Matière de la leçon.
            titre: Titre exact de la leçon.

        Returns:
            Dict avec titre, resume, contenu_complet, url, niveau, nb_chunks.
        """
        logger.info(f"Fetching lesson content: {titre} (matiere={matiere})")

        # Récupérer tous les chunks de cette leçon
        # ChromaDB nécessite l'opérateur $and pour plusieurs conditions
        filters = {
            "$and": [
                {"matiere": {"$eq": matiere}},
                {"titre": {"$eq": titre}}
            ]
        }

        try:
            collection = self.vector_store._collection
            logger.info(f"Querying ChromaDB with filters: {filters}")
            results = collection.get(
                where=filters,
                limit=1000  # Une leçon peut avoir beaucoup de chunks
            )
            logger.info(f"ChromaDB returned {len(results.get('documents', []))} documents")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contenu: {e}", exc_info=True)
            return None

        if not results or not results.get("documents"):
            logger.warning(f"Aucun contenu trouvé pour: {titre} dans {matiere}")
            logger.warning(f"Filters used: {filters}")
            return None

        # Reconstruire le contenu complet en concaténant les chunks
        chunks = []
        metadata = None
        for doc_content, meta in zip(results["documents"], results["metadatas"]):
            chunks.append(doc_content)
            if metadata is None:
                metadata = meta

        contenu_complet = "\n\n".join(chunks)
        resume = chunks[0][:300] + "..." if len(chunks[0]) > 300 else chunks[0]

        logger.info(f"Lesson content retrieved: {len(chunks)} chunks")

        return {
            "titre": titre,
            "resume": resume,
            "contenu_complet": contenu_complet,
            "url": metadata.get("url", "") if metadata else "",
            "matiere": metadata.get("matiere", "") if metadata else matiere,
            "niveau": metadata.get("niveau", "college") if metadata else "college",
            "source": metadata.get("source", "") if metadata else "",
            "nb_chunks": len(chunks)
        }
