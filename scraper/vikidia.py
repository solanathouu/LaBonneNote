"""Scraper Vikidia via l'API MediaWiki.

Collecte les articles encyclopédiques depuis fr.vikidia.org
par catégories, avec crawl récursif des sous-catégories.
"""

import json
import logging
import time
from pathlib import Path

import cloudscraper
import requests

from .metadata import (
    CATEGORIES_RACINES,
    determiner_matiere,
    est_categorie_ignoree,
    creer_metadata,
)

logger = logging.getLogger(__name__)

API_URL = "https://fr.vikidia.org/w/api.php"
BASE_URL = "https://fr.vikidia.org/wiki/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 "
    "ChatbotScolaireRAG/1.0 (educational project)"
)
DELAI_REQUETE = 1.0  # secondes entre chaque requête
MAX_PROFONDEUR = 3  # profondeur max du crawl récursif des catégories


class VikidiaScraper:
    """Scraper pour les articles Vikidia via l'API MediaWiki."""

    def __init__(self, dossier_sortie: str = "data/raw/vikidia"):
        self.dossier_sortie = Path(dossier_sortie)
        self.dossier_sortie.mkdir(parents=True, exist_ok=True)
        self.session = cloudscraper.create_scraper()
        self.articles_vus: set[str] = set()  # éviter les doublons
        # Compteurs de progression
        self._articles_ok = 0
        self._articles_skip = 0
        self._articles_err = 0
        self._categories_traitees = 0
        self._derniere_progression = time.time()

    def _afficher_progression(self, force: bool = False) -> None:
        """Affiche la progression toutes les 10 secondes ou si force=True."""
        now = time.time()
        if not force and (now - self._derniere_progression) < 10:
            return
        self._derniere_progression = now
        total = self._articles_ok + self._articles_skip + self._articles_err
        logger.info(
            "[PROGRESSION] %d categories | %d articles extraits | "
            "%d ignores | %d erreurs | %d total traites",
            self._categories_traitees,
            self._articles_ok,
            self._articles_skip,
            self._articles_err,
            total,
        )

    def scraper_tout(self) -> list[dict]:
        """Scrape toutes les matières configurées.

        Returns:
            Liste de tous les articles scrapés (dict avec 'titre', 'texte', 'metadata').
        """
        tous_articles = []

        for matiere, categories in CATEGORIES_RACINES.items():
            logger.info("========================================")
            logger.info("=== Scraping matiere: %s ===", matiere)
            logger.info("========================================")
            articles_matiere = []

            for categorie in categories:
                articles = self._scraper_categorie(
                    categorie, matiere, profondeur=0
                )
                articles_matiere.extend(articles)

            # Sauvegarder les articles bruts par matière
            self._sauvegarder(articles_matiere, matiere)
            tous_articles.extend(articles_matiere)
            logger.info(
                "[RESULTAT] Matiere %s: %d articles scrapes",
                matiere,
                len(articles_matiere),
            )

        logger.info("========================================")
        logger.info("[TERMINE] Total: %d articles scrapes", len(tous_articles))
        self._afficher_progression(force=True)
        return tous_articles

    def scraper_matiere(self, matiere: str) -> list[dict]:
        """Scrape une seule matière.

        Args:
            matiere: Identifiant de la matière (mathematiques, francais, histoire_geo).

        Returns:
            Liste des articles scrapés.
        """
        categories = CATEGORIES_RACINES.get(matiere, [])
        if not categories:
            logger.error("Matiere inconnue: %s", matiere)
            return []

        articles = []
        for categorie in categories:
            articles.extend(
                self._scraper_categorie(categorie, matiere, profondeur=0)
            )

        self._sauvegarder(articles, matiere)
        logger.info(
            "[RESULTAT] Matiere %s: %d articles scrapes", matiere, len(articles)
        )
        self._afficher_progression(force=True)
        return articles

    def _scraper_categorie(
        self, categorie: str, matiere: str, profondeur: int
    ) -> list[dict]:
        """Scrape récursivement une catégorie et ses sous-catégories.

        Args:
            categorie: Nom de la catégorie (ex: "Catégorie:Mathématiques").
            matiere: Matière associée.
            profondeur: Profondeur actuelle du crawl récursif.

        Returns:
            Liste des articles scrapés.
        """
        if profondeur > MAX_PROFONDEUR:
            return []

        if est_categorie_ignoree(categorie):
            logger.debug("Categorie ignoree: %s", categorie)
            return []

        self._categories_traitees += 1
        logger.info(
            "%s[CAT %d] %s (profondeur %d)",
            "  " * profondeur,
            self._categories_traitees,
            categorie,
            profondeur,
        )

        articles = []

        # 1. Récupérer les articles de cette catégorie
        titres_articles = self._lister_pages_categorie(categorie, type_page="page")
        logger.info(
            "%s  -> %d articles trouves dans cette categorie",
            "  " * profondeur,
            len(titres_articles),
        )

        for i, titre in enumerate(titres_articles):
            if titre in self.articles_vus:
                self._articles_skip += 1
                continue
            self.articles_vus.add(titre)

            article = self._extraire_article(titre, matiere, categorie)
            if article:
                articles.append(article)
                self._articles_ok += 1
            else:
                self._articles_skip += 1

            self._afficher_progression()

        # 2. Crawl récursif des sous-catégories
        sous_categories = self._lister_pages_categorie(categorie, type_page="subcat")
        if sous_categories:
            logger.info(
                "%s  -> %d sous-categories a explorer",
                "  " * profondeur,
                len(sous_categories),
            )

        for sous_cat in sous_categories:
            articles.extend(
                self._scraper_categorie(sous_cat, matiere, profondeur + 1)
            )

        return articles

    def _lister_pages_categorie(
        self, categorie: str, type_page: str = "page"
    ) -> list[str]:
        """Liste les pages ou sous-catégories d'une catégorie.

        Args:
            categorie: Nom de la catégorie.
            type_page: "page" pour les articles, "subcat" pour les sous-catégories.

        Returns:
            Liste des titres de pages.
        """
        titres = []
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": categorie,
            "cmtype": type_page,
            "cmlimit": "50",
            "format": "json",
        }

        while True:
            time.sleep(DELAI_REQUETE)
            try:
                response = self.session.get(API_URL, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except (requests.RequestException, json.JSONDecodeError) as e:
                logger.error(
                    "Erreur API pour categorie %s: %s", categorie, e
                )
                self._articles_err += 1
                break

            membres = data.get("query", {}).get("categorymembers", [])
            for membre in membres:
                # Ne garder que les articles (namespace 0) ou catégories (namespace 14)
                if membre.get("ns") in (0, 14):
                    titres.append(membre["title"])

            # Pagination
            if "continue" in data:
                params["cmcontinue"] = data["continue"]["cmcontinue"]
            else:
                break

        return titres

    def _extraire_article(
        self, titre: str, matiere: str, categorie: str
    ) -> dict | None:
        """Extrait le contenu texte d'un article Vikidia.

        Args:
            titre: Titre de la page à extraire.
            matiere: Matière associée.
            categorie: Catégorie d'origine.

        Returns:
            Dict avec 'titre', 'texte', 'url', 'metadata' ou None si échec.
        """
        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": "1",
            "redirects": "1",
            "titles": titre,
            "format": "json",
        }

        time.sleep(DELAI_REQUETE)
        try:
            response = self.session.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error("[ERREUR] Article '%s': %s", titre, e)
            self._articles_err += 1
            return None

        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            # Pages inexistantes ont un id négatif
            if int(page_id) < 0:
                logger.debug("Page inexistante: %s", titre)
                return None

            extrait = page.get("extract", "")
            titre_reel = page.get("title", titre)

            if not extrait or len(extrait.strip()) < 50:
                logger.debug("Article trop court ou vide: %s", titre_reel)
                return None

            url = BASE_URL + titre_reel.replace(" ", "_")
            metadata = creer_metadata(
                source="vikidia",
                matiere=matiere,
                titre=titre_reel,
                url=url,
                categorie=categorie,
            )

            logger.debug(
                "Article extrait: %s (%d chars)", titre_reel, len(extrait)
            )
            return {
                "titre": titre_reel,
                "texte": extrait,
                "url": url,
                "metadata": metadata,
            }

        return None

    def _sauvegarder(self, articles: list[dict], matiere: str) -> None:
        """Sauvegarde les articles bruts en JSON.

        Args:
            articles: Liste des articles à sauvegarder.
            matiere: Nom de la matière (pour le nom de fichier).
        """
        if not articles:
            return

        fichier = self.dossier_sortie / f"{matiere}.json"
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        logger.info("[SAUVEGARDE] %d articles -> %s", len(articles), fichier)
