"""Service pour gérer l'import et le traitement de PDFs personnels."""

import logging
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = "../data/user_pdfs"  # Dossier pour stocker les PDFs uploadés
CHROMA_DIR = "../chromadb"
PERSONAL_COLLECTION_NAME = "mes_cours"
EMBEDDING_MODEL = "text-embedding-3-small"

# Créer le dossier d'upload s'il n'existe pas
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


class PDFService:
    """Service pour gérer l'import de PDFs personnels."""

    def __init__(
        self,
        upload_dir: str = UPLOAD_DIR,
        chroma_dir: str = CHROMA_DIR,
        embedding_model: str = EMBEDDING_MODEL
    ):
        """Initialise le service PDF.

        Args:
            upload_dir: Dossier où stocker les PDFs uploadés.
            chroma_dir: Chemin vers la base ChromaDB.
            embedding_model: Modèle d'embedding OpenAI.
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Initialiser embeddings
        logger.info(f"Initialisation embeddings: {embedding_model}")
        self.embeddings = OpenAIEmbeddings(model=embedding_model)

        # Initialiser ChromaDB pour la collection personnelle
        logger.info(f"Connexion à ChromaDB: {chroma_dir}")
        self.vector_store = Chroma(
            collection_name=PERSONAL_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=chroma_dir
        )

        # Text splitter pour chunker les PDFs
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        logger.info("PDF Service initialisé avec succès")

    def save_pdf(self, file_content: bytes, filename: str) -> str:
        """Sauvegarde un PDF uploadé.

        Args:
            file_content: Contenu binaire du PDF.
            filename: Nom du fichier.

        Returns:
            Chemin du fichier sauvegardé.
        """
        # Générer un nom de fichier unique avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = self.upload_dir / safe_filename

        # Sauvegarder le fichier
        with open(file_path, "wb") as f:
            f.write(file_content)

        logger.info(f"PDF sauvegardé: {file_path}")
        return str(file_path)

    def process_pdf(self, file_path: str) -> Dict[str, any]:
        """Traite un PDF : extraction, chunking, et ajout à ChromaDB.

        Args:
            file_path: Chemin du fichier PDF.

        Returns:
            Dict avec infos sur le traitement (nb_pages, nb_chunks, etc.).
        """
        logger.info(f"Traitement du PDF: {file_path}")

        # 1. Charger le PDF avec PyPDFLoader
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        logger.info(f"PDF chargé: {len(documents)} pages")

        # 2. Chunker les documents
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Chunking terminé: {len(chunks)} chunks créés")

        # 3. Ajouter des métadonnées
        filename = Path(file_path).name
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "filename": filename,
                "source": "pdf_personnel",
                "chunk_index": i,
                "uploaded_at": datetime.now().isoformat()
            })

        # 4. Ajouter à ChromaDB
        self.vector_store.add_documents(chunks)
        logger.info(f"Chunks ajoutés à ChromaDB (collection: {PERSONAL_COLLECTION_NAME})")

        return {
            "filename": filename,
            "nb_pages": len(documents),
            "nb_chunks": len(chunks),
            "uploaded_at": chunks[0].metadata["uploaded_at"]
        }

    def list_pdfs(self) -> List[Dict[str, any]]:
        """Liste tous les PDFs importés.

        Returns:
            Liste de dicts avec infos sur chaque PDF.
        """
        pdfs = []
        for pdf_file in self.upload_dir.glob("*.pdf"):
            stat = pdf_file.stat()
            pdfs.append({
                "filename": pdf_file.name,
                "size": stat.st_size,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(pdf_file)
            })

        # Trier par date (plus récents en premier)
        pdfs.sort(key=lambda x: x["uploaded_at"], reverse=True)
        return pdfs

    def delete_pdf(self, filename: str) -> bool:
        """Supprime un PDF et ses chunks de ChromaDB.

        Args:
            filename: Nom du fichier à supprimer.

        Returns:
            True si suppression réussie, False sinon.
        """
        file_path = self.upload_dir / filename

        if not file_path.exists():
            logger.warning(f"PDF non trouvé: {filename}")
            return False

        # Supprimer le fichier
        file_path.unlink()
        logger.info(f"PDF supprimé: {filename}")

        # Supprimer les chunks de ChromaDB
        # Note: ChromaDB ne permet pas de supprimer par metadata facilement
        # On garde les chunks pour l'instant (optionnel: recréer la collection)

        return True

    def search_in_personal_docs(
        self,
        question: str,
        top_k: int = 5
    ) -> List[Dict[str, any]]:
        """Recherche dans les documents personnels.

        Args:
            question: Question de l'utilisateur.
            top_k: Nombre de résultats.

        Returns:
            Liste de documents pertinents.
        """
        results = self.vector_store.similarity_search_with_score(
            question,
            k=top_k
        )

        documents = []
        for doc, score in results:
            documents.append({
                "content": doc.page_content,
                "score": float(score),
                "filename": doc.metadata.get("filename", ""),
                "page": doc.metadata.get("page", 0),
                "source": doc.metadata.get("source", "")
            })

        return documents
