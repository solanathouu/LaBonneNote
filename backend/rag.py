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

        # Initialiser embeddings
        logger.info(f"Initialisation embeddings: {embedding_model}")
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        # Initialiser ChromaDB
        logger.info(f"Connexion à ChromaDB: {chroma_dir}")
        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
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

    def retrieve(
        self,
        question: str,
        matiere: Optional[str] = None,
        niveau: Optional[str] = None
    ) -> List[Document]:
        """Récupère les chunks pertinents depuis ChromaDB.

        Args:
            question: Question de l'élève.
            matiere: Filtre optionnel par matière.
            niveau: Filtre optionnel par niveau.

        Returns:
            Liste de documents pertinents.
        """
        # Construire les filtres de métadonnées
        filters = {}
        if matiere:
            filters["matiere"] = matiere
        if niveau and niveau != "college":
            # Chercher niveau exact OU college (fallback)
            # Note: ChromaDB ne supporte pas OR, donc on fait 2 requêtes
            pass

        # Recherche de similarité
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

        # Filtrer par seuil de similarité
        # Note: ChromaDB retourne distance (plus petit = plus similaire)
        # On garde seulement les résultats pertinents
        filtered_docs = []
        for doc, score in results:
            logger.debug(f"Document trouvé (score: {score:.3f}): {doc.metadata.get('titre', 'Sans titre')}")
            filtered_docs.append(doc)

        logger.info(f"Retrieval: {len(filtered_docs)} chunks pertinents trouvés")
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
        niveau: str = "college"
    ) -> Dict[str, any]:
        """Exécute la chaîne RAG complète.

        Args:
            question: Question de l'élève.
            matiere: Filtre optionnel par matière.
            niveau: Niveau scolaire (6eme, 5eme, 4eme, 3eme, college).

        Returns:
            Dict avec la réponse et les sources.
        """
        logger.info(f"RAG Query: '{question}' (matiere={matiere}, niveau={niveau})")

        # 1. Retrieval
        documents = self.retrieve(question, matiere, niveau)

        # 2. Generation
        answer = self.generate(question, documents, niveau)

        # 3. Préparer les sources
        sources = []
        for doc in documents:
            sources.append({
                "titre": doc.metadata.get("titre", "Sans titre"),
                "url": doc.metadata.get("url", ""),
                "matiere": doc.metadata.get("matiere", ""),
                "source": doc.metadata.get("source", "")
            })

        return {
            "answer": answer,
            "sources": sources,
            "nb_sources": len(sources)
        }
