"""Scraper Académie en Ligne (CNED) avec Crawl4AI.

Collecte les cours du CNED par niveau EXACT (6ème, 5ème, 4ème, 3ème).
Permet le regroupement précis par classe.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

logger = logging.getLogger(__name__)

# URLs Académie en Ligne par niveau EXACT
ACADEMIE_URLS = {
    "6eme": {
        "url": "https://www.academie-en-ligne.fr/Ecole/Cours.aspx?INSTANCEID=103&PORTAL_ID=&NODEID=3489&level=6",
        "description": "Cours 6ème"
    },
    "5eme": {
        "url": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3491",
        "description": "Cours 5ème"
    },
    "4eme": {
        "url": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3493",
        "description": "Cours 4ème"
    },
    "3eme": {
        "url": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3495",
        "description": "Cours 3ème"
    }
}

# Matières à extraire
MATIERES_KEYWORDS = {
    "mathematiques": ["mathématique", "maths", "math"],
    "francais": ["français", "lettre"],
    "histoire_geo": ["histoire", "géographie", "hist", "geo"],
    "svt": ["svt", "sciences vie", "biologie", "géologie"],
    "physique_chimie": ["physique", "chimie"],
    "technologie": ["technologie", "techno"],
    "anglais": ["anglais", "english"],
    "espagnol": ["espagnol", "spanish"]
}


class AcademieEnLigneCrawler:
    """Scraper Académie en Ligne avec Crawl4AI."""

    def __init__(self, dossier_sortie: str = "data/raw/academie_en_ligne"):
        self.dossier_sortie = Path(dossier_sortie)
        self.dossier_sortie.mkdir(parents=True, exist_ok=True)

    def _detecter_matiere(self, titre: str, url: str) -> str:
        """Détecte la matière depuis le titre ou l'URL."""
        titre_lower = titre.lower()
        url_lower = url.lower()
        texte = titre_lower + " " + url_lower

        for matiere, keywords in MATIERES_KEYWORDS.items():
            if any(kw in texte for kw in keywords):
                return matiere

        return "autre"

    async def scraper_niveau(self, niveau: str, config: dict) -> List[Dict]:
        """Scrape un niveau complet depuis Académie en Ligne.

        Args:
            niveau: Niveau scolaire (6eme, 5eme, 4eme, 3eme).
            config: Configuration du niveau (url, description).

        Returns:
            Liste des cours extraits.
        """
        url = config["url"]

        logger.info(f"Scraping {config['description']}: {url}")

        # Configuration browser
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080
        )

        # Configuration crawler
        crawler_config = CrawlerRunConfig(
            page_timeout=60000,
            screenshot=True,
            remove_overlay_elements=True,
            wait_for="css:body",
        )

        cours = []

        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 1. Scraper la page principale du niveau
            result = await crawler.arun(url, config=crawler_config)

            if not result.success:
                logger.error(f"Échec scraping {url}: {result.error_message}")
                return cours

            # 2. Extraire tous les liens de cours
            all_links = result.links.get("internal", []) + result.links.get("external", [])

            # Filtrer les liens de cours (contiennent "Cours", "Sequence", "Chapitre")
            liens_cours = []
            for link in all_links:
                link_lower = link.lower()
                if any(kw in link_lower for kw in ["cours", "sequence", "chapitre", "lecon"]):
                    # Éviter doublons
                    if link not in liens_cours:
                        liens_cours.append(link)

            logger.info(f"Liens de cours trouvés: {len(liens_cours)}")

            # 3. Scraper chaque cours (limiter pour test)
            max_cours = 10  # Limiter pour test, retirer en production
            for i, link in enumerate(liens_cours[:max_cours]):
                logger.info(f"  [{i+1}/{min(max_cours, len(liens_cours))}] {link}")

                sub_result = await crawler.arun(link, config=crawler_config)

                if sub_result.success and len(sub_result.markdown) > 100:
                    titre = sub_result.metadata.get("title", "Sans titre")
                    matiere = self._detecter_matiere(titre, link)

                    doc = {
                        "titre": titre,
                        "texte": sub_result.markdown,
                        "url": link,
                        "metadata": {
                            "source": "academie_en_ligne",
                            "matiere": matiere,
                            "niveau": niveau,  # Niveau EXACT!
                            "categorie": f"Cours {niveau}"
                        }
                    }
                    cours.append(doc)
                    logger.info(f"    ✅ {matiere} - {titre[:50]}...")

                await asyncio.sleep(2)  # Respecter le serveur

        logger.info(f"Total cours extraits pour {niveau}: {len(cours)}")
        return cours

    async def scraper_tout(self) -> List[Dict]:
        """Scrape tous les niveaux collège."""
        tous_cours = []

        for niveau, config in ACADEMIE_URLS.items():
            cours = await self.scraper_niveau(niveau, config)
            tous_cours.extend(cours)

            # Sauvegarder par niveau
            if cours:
                fichier = self.dossier_sortie / f"{niveau}.json"
                with open(fichier, "w", encoding="utf-8") as f:
                    json.dump(cours, f, ensure_ascii=False, indent=2)
                logger.info(f"Sauvegardé {len(cours)} cours -> {fichier}")

        logger.info(f"\n✅ Total cours tous niveaux: {len(tous_cours)}")
        return tous_cours


async def main():
    """Fonction principale."""
    import sys

    # Logging vers fichier pour éviter problèmes encodage Windows
    log_file = Path("scraper_academie.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
    )

    # Désactiver les logs verbeux de crawl4ai
    logging.getLogger("crawl4ai").setLevel(logging.WARNING)

    logger.info("=== Scraping Académie en Ligne (CNED) ===")
    print("Logs détaillés dans:", log_file)

    scraper = AcademieEnLigneCrawler()
    cours = await scraper.scraper_tout()

    # Statistiques
    if cours:
        par_niveau = {}
        par_matiere = {}
        for c in cours:
            niveau = c["metadata"]["niveau"]
            matiere = c["metadata"]["matiere"]
            par_niveau[niveau] = par_niveau.get(niveau, 0) + 1
            par_matiere[matiere] = par_matiere.get(matiere, 0) + 1

        logger.info("\n📊 Répartition par niveau:")
        for niveau in ["6eme", "5eme", "4eme", "3eme"]:
            count = par_niveau.get(niveau, 0)
            logger.info(f"  {niveau}: {count} cours")

        logger.info("\n📊 Répartition par matière:")
        for matiere, count in sorted(par_matiere.items()):
            logger.info(f"  {matiere}: {count} cours")


if __name__ == "__main__":
    asyncio.run(main())
