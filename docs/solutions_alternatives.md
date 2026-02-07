# Solutions alternatives pour données avec niveaux

## ❌ Wikiversité: ÉCHEC

**Résultat du scraping:**
- 507 pages trouvées → 2 leçons extraites (0.4%)
- 99.6% des pages vides ou inutilisables
- **Conclusion**: Non viable

---

## ✅ SOLUTION 1: Éduscol (OFFICIEL - RECOMMANDÉ)

### Description
**Source officielle de l'Éducation Nationale** avec programmes par cycle.

### URLs principales
- **Cycle 3 (6ème)**: https://eduscol.education.fr/87/j-enseigne-au-cycle-3
- **Cycle 4 (5ème-3ème)**: https://eduscol.education.fr/88/j-enseigne-au-cycle-4

### Avantages
- ✅ Source officielle et fiable
- ✅ Organisé par cycle (3 et 4)
- ✅ Programmes détaillés par matière
- ✅ Documents pédagogiques riches
- ✅ crawl4ai peut extraire proprement

### Volume estimé
- ~50-100 documents par matière
- ~400-800 documents total
- Contenu de haute qualité

### Implémentation
```bash
# Lancer le scraper Éduscol avec crawl4ai
python scraper/eduscol_crawl4ai.py
```

**Fichier créé:** `scraper/eduscol_crawl4ai.py`

---

## ✅ SOLUTION 2: Académie en Ligne (CNED)

### Description
**Cours complets du CNED** (Centre National d'Enseignement à Distance) par niveau.

### URLs par niveau
- **6ème**: https://www.academie-en-ligne.fr/Ecole/Cours.aspx?INSTANCEID=103&PORTAL_ID=&NODEID=3489&level=6
- **5ème**: https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3491
- **4ème**: https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3493
- **3ème**: https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3495

### Avantages
- ✅ Cours structurés par niveau exact (6ème, 5ème, 4ème, 3ème)
- ✅ Toutes les matières du collège
- ✅ Contenu pédagogique validé CNED
- ✅ Format cohérent et bien structuré

### Volume estimé
- ~30-50 cours par niveau et matière
- ~1000-2000 documents total
- Excellente qualité pédagogique

### Implémentation
Similaire à Éduscol mais avec URLs spécifiques par niveau:

```python
ACADEMIE_URLS = {
    "6eme": "https://www.academie-en-ligne.fr/Ecole/Cours.aspx?INSTANCEID=103&PORTAL_ID=&NODEID=3489&level=6",
    "5eme": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3491",
    "4eme": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3493",
    "3eme": "https://www.academie-en-ligne.fr/College/Cours.aspx?NODEID=3495"
}
```

---

## ✅ SOLUTION 3: Kartable

### Description
**Plateforme éducative** avec cours et exercices par niveau et matière.

### URLs
- **Base**: https://www.kartable.fr/ressources/
- Structure: `/ressources/{niveau}/{matiere}`
- Exemple: https://www.kartable.fr/ressources/cinquieme/mathematiques

### Avantages
- ✅ Contenu riche et moderne
- ✅ Structuré par niveau (6ème-3ème)
- ✅ Toutes les matières
- ✅ Cours + exercices + fiches

### Volume estimé
- ~100-200 ressources par niveau/matière
- ~5000-10000 documents total
- Très riche en contenu

### Inconvénients
- ⚠️ Contenu commercial (vérifier CGU)
- ⚠️ Possible protection anti-scraping

---

## ✅ SOLUTION 4: Lumni (France Télévisions)

### Description
**Plateforme éducative publique** avec vidéos et articles validés.

### URLs
- **Base**: https://www.lumni.fr/
- **Collège**: https://www.lumni.fr/college
- Par niveau: `/college/sixieme`, `/college/cinquieme`, etc.

### Avantages
- ✅ Plateforme publique et gratuite
- ✅ Contenu validé Éducation Nationale
- ✅ Multimédia (vidéos + articles)
- ✅ Bien structuré par niveau

### Volume estimé
- ~50-100 ressources par niveau/matière
- ~2000-4000 documents total
- Contenu engageant et moderne

---

## 📊 Comparaison des solutions

| Source | Fiabilité | Niveaux | Volume | Qualité | Facilité scraping |
|--------|-----------|---------|--------|---------|-------------------|
| **Éduscol** | ⭐⭐⭐⭐⭐ | Cycles 3-4 | ~800 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Académie en Ligne** | ⭐⭐⭐⭐⭐ | 6ème-3ème | ~2000 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Kartable** | ⭐⭐⭐⭐ | 6ème-3ème | ~10000 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Lumni** | ⭐⭐⭐⭐⭐ | 6ème-3ème | ~4000 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Vikidia | ⭐⭐⭐ | Aucun | 43868 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Wikiversité | ⭐⭐ | 7-13 | 2 | ⭐ | ❌ |

---

## 🎯 Recommandation finale

### Approche hybride optimale

**1. Base volumétrique (contenu générique):**
- ✅ **Vikidia** (43 868 chunks) → niveau="college"
- Déjà scrapé et traité

**2. Enrichissement par niveau (contenu spécifique):**
- ✅ **Éduscol** (officiel, cycles) → ~800 documents
- ✅ **Académie en Ligne** (cours CNED par niveau) → ~2000 documents
- ⚙️ **Lumni** (optionnel, multimédia) → ~4000 documents

**3. Résultat final estimé:**
```
Total chunks: 43 868 (Vikidia) + ~3000 (Éduscol + CNED) = ~47 000 chunks

Répartition niveaux:
- college: 43 868 chunks (~93%)
- 6eme: ~300 chunks (~0.6%)
- 5eme: ~900 chunks (~2%)
- 4eme: ~900 chunks (~2%)
- 3eme: ~900 chunks (~2%)
```

**4. Logique RAG:**
```python
# Recherche intelligente avec fallback
if niveau_eleve == "5eme":
    # 1. Chercher chunks niveau="5eme" (priorité)
    # 2. Si < 3 résultats → chercher niveau="college" (fallback)
    # 3. Adapter la réponse au niveau 5ème dans le prompt GPT
```

---

## 🚀 Prochaines étapes

### Option A: Scraper Éduscol (rapide, officiel)
```bash
python scraper/eduscol_crawl4ai.py
```
**Durée:** ~10-15 min
**Résultat:** ~800 documents officiels

### Option B: Scraper Académie en Ligne (complet, par niveau)
**À implémenter:** Adapter `eduscol_crawl4ai.py` pour CNED
**Durée:** ~20-30 min
**Résultat:** ~2000 cours CNED par niveau

### Option C: Les deux (recommandé)
**Durée:** ~30-45 min
**Résultat:** ~2800 documents avec niveaux spécifiques

### Option D: Continuer avec Vikidia seul
Ingérer les 43 868 chunks existants, adapter via prompts GPT

---

## 💡 Note importante

Toutes ces sources sont **publiques et éducatives**, mais il est recommandé de:
1. Vérifier les CGU de chaque site
2. Respecter les délais entre requêtes (2-3s)
3. Ajouter un User-Agent identifiable
4. Ne pas surcharger les serveurs

Pour un usage éducatif et non-commercial comme votre projet, ces sources sont généralement acceptables.
