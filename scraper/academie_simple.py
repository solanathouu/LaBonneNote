"""Scraper simple Académie en Ligne avec requests/BeautifulSoup.

Alternative à crawl4ai qui a des problèmes d'encodage sur Windows.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict

import cloudscraper
from bs4 import BeautifulSoup

# Logging avec UTF-8
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.StreamHandler(
            open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
        ),
    ],
)
logger = logging.getLogger(__name__)

# URLs Académie en Ligne par niveau EXACT
ACADEMIE_URLS = {
    "6eme": "https://www.academie-en-ligne.fr/Ecole/Cours.aspx?INSTANCEID=103&PORTAL_ID=&NODEID=3489&level=6",
    "5eme": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3491",
    "4eme": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3493",
    "3eme": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3495"
}

# Matières
MATIERES_KEYWORDS = {
    "mathematiques": ["mathematique", "maths", "math"],
    "francais": ["francais", "lettre"],
    "histoire_geo": ["histoire", "geographie", "hist", "geo"],
    "svt": ["svt", "sciences vie", "biologie", "geologie"],
    "physique_chimie": ["physique", "chimie"],
    "technologie": ["technologie", "techno"],
    "anglais": ["anglais", "english"],
    "espagnol": ["espagnol", "spanish"]
}


def detecter_matiere(titre: str, url: str) -> str:
    """Détecte la matière depuis le titre ou l'URL."""
    texte = (titre + " " + url).lower()

    for matiere, keywords in MATIERES_KEYWORDS.items():
        if any(kw in texte for kw in keywords):
            return matiere

    return "autre"


def scraper_niveau(niveau: str, url: str, dossier_sortie: Path) -> List[Dict]:
    """Scrape un niveau de l'Académie en Ligne."""
    logger.info(f"Scraping niveau {niveau}: {url}")

    session = cloudscraper.create_scraper()
    cours = []

    try:
        # 1. Page principale
        response = session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. Extraire les liens de cours
        # Note: La structure exacte dépend du site, adapter si nécessaire
        liens = soup.find_all('a', href=True)

        liens_cours = []
        for link in liens:
            href = link.get('href', '')
            texte = link.get_text(strip=True)

            # Filtrer les liens pertinents
            if any(kw in href.lower() or kw in texte.lower() for kw in ["cours", "sequence", "chapitre", "lecon"]):
                # Construire URL absolue si nécessaire
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = f"https://www.academie-en-ligne.fr{href}"
                else:
                    full_url = f"https://www.academie-en-ligne.fr/{href}"

                if full_url not in liens_cours:
                    liens_cours.append(full_url)

        logger.info(f"  Trouve {len(liens_cours)} liens de cours")

        # 3. Scraper chaque cours (limiter pour test)
        max_cours = 5  # Limiter pour test initial
        for i, link in enumerate(liens_cours[:max_cours]):
            logger.info(f"  [{i+1}/{min(max_cours, len(liens_cours))}] {link}")

            time.sleep(2)  # Respecter le serveur

            try:
                sub_response = session.get(link, timeout=30)
                sub_response.raise_for_status()

                sub_soup = BeautifulSoup(sub_response.text, 'html.parser')

                # Extraire titre
                titre_elem = sub_soup.find('title') or sub_soup.find('h1')
                titre = titre_elem.get_text(strip=True) if titre_elem else "Sans titre"

                # Extraire contenu principal
                # Essayer plusieurs sélecteurs possibles
                contenu = None
                for selector in ['main', '.main-content', '.content', 'article', '#content']:
                    contenu_elem = sub_soup.select_one(selector)
                    if contenu_elem:
                        contenu = contenu_elem.get_text(separator='\n', strip=True)
                        break

                if not contenu:
                    # Fallback: tout le body
                    body = sub_soup.find('body')
                    if body:
                        contenu = body.get_text(separator='\n', strip=True)

                if contenu and len(contenu) > 100:
                    matiere = detecter_matiere(titre, link)

                    doc = {
                        "titre": titre,
                        "texte": contenu,
                        "url": link,
                        "metadata": {
                            "source": "academie_en_ligne",
                            "matiere": matiere,
                            "niveau": niveau,
                            "categorie": f"Cours {niveau}"
                        }
                    }
                    cours.append(doc)
                    logger.info(f"    OK {matiere} - {titre[:50]}...")

            except Exception as e:
                logger.warning(f"    ERREUR: {e}")
                continue

    except Exception as e:
        logger.error(f"Erreur scraping {url}: {e}")

    logger.info(f"Total {niveau}: {len(cours)} cours extraits")

    # Sauvegarder
    if cours:
        fichier = dossier_sortie / f"{niveau}.json"
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(cours, f, ensure_ascii=False, indent=2)
        logger.info(f"Sauvegarde: {fichier}")

    return cours


def main():
    """Fonction principale."""
    logger.info("=== Scraping Academie en Ligne (simple) ===")

    dossier_sortie = Path("data/raw/academie_en_ligne")
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    tous_cours = []

    for niveau, url in ACADEMIE_URLS.items():
        cours = scraper_niveau(niveau, url, dossier_sortie)
        tous_cours.extend(cours)

    # Statistiques
    logger.info(f"\n=== TERMINE: {len(tous_cours)} cours total ===")

    if tous_cours:
        par_niveau = {}
        par_matiere = {}
        for c in tous_cours:
            n = c["metadata"]["niveau"]
            m = c["metadata"]["matiere"]
            par_niveau[n] = par_niveau.get(n, 0) + 1
            par_matiere[m] = par_matiere.get(m, 0) + 1

        logger.info("\nPar niveau:")
        for n in ["6eme", "5eme", "4eme", "3eme"]:
            logger.info(f"  {n}: {par_niveau.get(n, 0)} cours")

        logger.info("\nPar matiere:")
        for m, count in sorted(par_matiere.items()):
            logger.info(f"  {m}: {count} cours")


if __name__ == "__main__":
    main()
