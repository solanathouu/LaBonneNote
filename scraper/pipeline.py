"""Pipeline d'orchestration : scrape → clean → chunk → sauvegarde.

Point d'entrée principal pour le scraping.
Usage: python -m scraper.pipeline [--matiere MATIERE] [--source SOURCE]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from .cleaner import nettoyer_texte
from .chunker import decouper_en_chunks
from .vikidia import VikidiaScraper

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(
            open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
        ),
    ],
)
logger = logging.getLogger(__name__)

DOSSIER_PROCESSED = Path("data/processed")


def traiter_articles(articles: list[dict]) -> list[dict]:
    """Applique le pipeline clean → chunk sur une liste d'articles bruts.

    Args:
        articles: Liste d'articles bruts (dict avec 'titre', 'texte', 'metadata').

    Returns:
        Liste de chunks prêts pour l'embedding.
    """
    tous_chunks = []

    for article in articles:
        titre = article["titre"]
        texte_brut = article["texte"]
        metadata = article["metadata"]

        # 1. Nettoyage
        texte_propre = nettoyer_texte(texte_brut)
        if not texte_propre or len(texte_propre) < 50:
            logger.debug("Article trop court après nettoyage: %s", titre)
            continue

        # 2. Chunking
        chunks = decouper_en_chunks(texte_propre, titre=titre)

        # 3. Attacher les métadonnées à chaque chunk
        for chunk in chunks:
            tous_chunks.append({
                "text": chunk["text"],
                "metadata": {
                    **metadata,
                    "chunk_index": chunk["index"],
                },
            })

    logger.info(
        "%d articles traites -> %d chunks generes", len(articles), len(tous_chunks)
    )
    return tous_chunks


def sauvegarder_chunks(chunks: list[dict], matiere: str) -> Path:
    """Sauvegarde les chunks traités en JSON.

    Args:
        chunks: Liste de chunks avec texte et métadonnées.
        matiere: Nom de la matière (pour organiser les fichiers).

    Returns:
        Chemin du fichier sauvegardé.
    """
    dossier = DOSSIER_PROCESSED / matiere
    dossier.mkdir(parents=True, exist_ok=True)

    fichier = dossier / "chunks.json"
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    logger.info("Sauvegardé %d chunks dans %s", len(chunks), fichier)
    return fichier


def run_vikidia(matiere: str | None = None) -> None:
    """Lance le pipeline complet pour Vikidia.

    Args:
        matiere: Si spécifié, ne scrape que cette matière.
    """
    scraper = VikidiaScraper()

    if matiere:
        logger.info("Scraping Vikidia - matière: %s", matiere)
        articles = scraper.scraper_matiere(matiere)
        chunks = traiter_articles(articles)
        sauvegarder_chunks(chunks, matiere)
    else:
        logger.info("Scraping Vikidia - toutes les matières")
        articles = scraper.scraper_tout()

        # Grouper les articles par matière pour la sauvegarde des chunks
        par_matiere: dict[str, list[dict]] = {}
        for article in articles:
            m = article["metadata"]["matiere"]
            par_matiere.setdefault(m, []).append(article)

        for m, arts in par_matiere.items():
            chunks = traiter_articles(arts)
            sauvegarder_chunks(chunks, m)


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de scraping pour le chatbot scolaire"
    )
    parser.add_argument(
        "--matiere",
        choices=["mathematiques", "francais", "histoire_geo", "svt", "physique_chimie", "technologie", "anglais", "espagnol"],
        help="Scraper une seule matière (par défaut: toutes)",
    )
    parser.add_argument(
        "--source",
        choices=["vikidia", "wikiversite", "eduscol"],
        default="vikidia",
        help="Source à scraper (par défaut: vikidia)",
    )

    args = parser.parse_args()

    if args.source == "vikidia":
        run_vikidia(args.matiere)
    elif args.source == "wikiversite":
        logger.error("Scraper Wikiversité pas encore implémenté")
    elif args.source == "eduscol":
        logger.error("Scraper Éduscol pas encore implémenté")


if __name__ == "__main__":
    main()
