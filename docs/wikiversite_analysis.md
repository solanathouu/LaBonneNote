# Analyse Wikiversité - Faisabilité pour enrichissement de niveaux

## Date: 2026-02-07

## 🎯 Objectif
Valider si Wikiversité peut servir de référentiel pour assigner des niveaux scolaires (6ème-3ème) aux chunks Vikidia.

## 📊 Volume de leçons disponibles

| Niveau Wikiversité | Nombre de leçons | Exemples de contenu |
|-------------------|------------------|---------------------|
| Niveau 7 | 27 leçons | Proportionnalité, Grammaire, Géométrie |
| Niveau 8 | 31 leçons | Fraction, Chimie de l'eau, Géologie |
| Niveau 9 | 39 leçons | Pythagore, Calcul littéral, Air et molécules |
| Niveau 10 | 45 leçons | Première Guerre mondiale, Équations |
| **Niveau 11** | **128 leçons** | ADN, Air, Aménager la ville |
| **Niveau 12** | **114 leçons** | Alcanes, Alcools |
| **Niveau 13** | **123 leçons** | Acidité/basicité, Nombres complexes |

**Total niveaux 7-13**: ~507 leçons

## 🔍 Détection de matières

### Niveau 8 (exemple détaillé):
- ✅ **Mathématiques**: Fraction, Enchainement d'opérations
- ✅ **Physique-Chimie**: Approche de la chimie par l'eau
- ✅ **SVT**: Géologie des paysages
- ✅ **Français**: Grammaire grecque
- ✅ **Histoire**: Histoire de la chimie

### Niveau 9 (exemple détaillé):
- ✅ **Mathématiques**: Calcul littéral, Équations
- ✅ **Physique-Chimie**: Air et ses molécules
- ✅ **Histoire**: Civilisation anglo-saxonne en quatrième

## 💡 Hypothèse de correspondance Wikiversité ↔ Collège

Basé sur les contenus observés (Pythagore=niveau 9, Fraction=niveau 8):

| Wikiversité | Niveau scolaire | Volume |
|-------------|-----------------|--------|
| Niveaux 7-8 | Fin primaire / **6ème** | ~58 leçons |
| Niveaux 9-10 | **5ème / 4ème** | ~84 leçons |
| Niveaux 11-12 | **3ème / 2nde** | ~242 leçons |
| Niveau 13+ | Lycée | ~123 leçons |

**⚠️ À confirmer**: Cette correspondance est une hypothèse basée sur l'analyse du contenu.

## ✅ FAISABILITÉ: OUI avec réserves

### Points positifs:
1. ✅ **Structure claire par niveaux** (API fonctionnelle avec cloudscraper)
2. ✅ **Niveaux extractibles** depuis catégories "Leçons de niveau X"
3. ✅ **Matières du collège présentes** (maths, français, histoire-géo, sciences)
4. ✅ **Volume raisonnable** (~507 leçons pour 7 niveaux)

### Points d'attention:
1. ⚠️ **Correspondance niveaux incertaine** - besoin de validation
2. ⚠️ **Volume modeste** comparé à Vikidia (507 vs 43 868)
3. ⚠️ **Répartition inégale** (11-13 = 73% du volume)

## 🎯 Stratégie recommandée

### Option A: Scraping direct avec correspondance fixe
```python
NIVEAU_MAPPING = {
    7: "6eme",
    8: "6eme",
    9: "5eme",
    10: "4eme",
    11: "3eme",
    12: "3eme",
    13: "3eme"  # ou exclure car lycée
}
```

### Option B: Scraping + validation manuelle
1. Scraper tous les niveaux 7-13
2. Analyser manuellement un échantillon pour confirmer correspondance
3. Ajuster le mapping

### Option C: Utiliser uniquement pour enrichissement partiel
1. Scraper Wikiversité (507 leçons avec niveaux)
2. Matching par titre/similarité avec Vikidia
3. Garder niveau "college" pour chunks Vikidia sans match
4. **Résultat**: Base hybride avec ~5-10% de chunks niveau spécifique, 90% niveau "college"

## 📈 Estimation enrichissement

Si on utilise le matching sémantique entre Wikiversité (507) et Vikidia (43 868):

- **Matches directs par titre**: ~100-200 chunks (~0.5%)
- **Matches par similarité (score > 0.8)**: ~2 000-5 000 chunks (~5-10%)
- **Reste niveau "college"**: ~38 000-41 000 chunks (~90%)

## 💰 Coût estimé

- Scraping Wikiversité: Gratuit (API MediaWiki)
- Embedding Wikiversité: ~$0.01 (507 leçons)
- Matching sémantique: ~$0.26 (déjà budgété pour Vikidia)
- **Total supplémentaire**: ~$0.01

## 🚀 Recommandation finale

**OUI, scraper Wikiversité MAIS** avec attentes réalistes:

1. **Ne résoudra pas 100% du problème de niveaux**
2. **Apportera une base de ~500 leçons structurées** (utile!)
3. **Permettra enrichissement partiel de Vikidia** (~5-10%)
4. **Complément nécessaire**:
   - Continuer avec Éduscol pour programmes officiels
   - Ou utiliser LLM pour classifier le reste

## 🎬 Prochaines actions

1. ✅ Valider la correspondance niveaux (chercher doc officielle Wikiversité)
2. Implémenter scraper Wikiversité
3. Tester matching sur échantillon (100 chunks)
4. Décider: enrichissement complet ou hybride
