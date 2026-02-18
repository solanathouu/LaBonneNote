"""
Script de test : Classification de 10 leçons pour valider le système.
"""

import json
import time
from openai import OpenAI
from dotenv import load_dotenv
from rag import RAGChain

load_dotenv()
client = OpenAI()

CLASSIFICATION_PROMPT = """Tu es un expert du programme scolaire français au collège.

Analyse ce cours et détermine à quel niveau il correspond le mieux :
- 6eme : Introduction aux concepts, bases fondamentales
- 5eme : Approfondissement progressif
- 4eme : Concepts intermédiaires avancés
- 3eme : Préparation au lycée, concepts complexes

Titre : {titre}
Matière : {matiere}
Extrait : {extrait}

Réponds UNIQUEMENT par un JSON :
{{"niveau": "6eme|5eme|4eme|3eme", "confiance": 0-100, "raison": "explication courte"}}

Exemples de référence :
- Théorème de Pythagore -> 4eme
- Fractions simples -> 6eme
- Équations du premier degré -> 5eme
- Révolution française -> 4eme
"""


def classify_lesson(titre: str, matiere: str, extrait: str):
    """Classifie une leçon avec GPT-4o-mini."""

    prompt = CLASSIFICATION_PROMPT.format(
        titre=titre,
        matiere=matiere,
        extrait=extrait[:500]
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=100,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        return {"niveau": "college", "confiance": 0, "raison": "erreur"}


def test_classification():
    """Teste la classification sur 10 leçons."""

    print("Test de classification sur 10 lecons\n")

    # Initialiser RAG
    rag_chain = RAGChain()

    # Récupérer quelques leçons de mathématiques
    lessons = rag_chain.get_all_lessons("mathematiques", niveau=None, limit=10)

    print(f"[LESSONS] {len(lessons)} leçons récupérées\n")
    print("=" * 80)

    results = []

    for i, lesson in enumerate(lessons, 1):
        print(f"\n[{i}/10] [MATH] {lesson['titre']}")
        print(f"       Matière: {lesson['matiere']}")

        # Classifier
        classification = classify_lesson(
            titre=lesson["titre"],
            matiere=lesson["matiere"],
            extrait=lesson["resume"]
        )

        niveau = classification["niveau"]
        confiance = classification["confiance"]
        raison = classification["raison"]

        print(f"       -> Niveau détecté: {niveau} (confiance: {confiance}%)")
        print(f"       -> Raison: {raison}")

        results.append({
            "titre": lesson["titre"],
            "niveau_detecte": niveau,
            "confiance": confiance,
            "raison": raison
        })

        # Rate limiting
        time.sleep(1)

    print("\n" + "=" * 80)
    print("\n[OK] Test terminé !\n")

    # Statistiques
    stats = {}
    for r in results:
        niveau = r["niveau_detecte"]
        stats[niveau] = stats.get(niveau, 0) + 1

    print("[STATS] Répartition :")
    for niveau, count in sorted(stats.items()):
        print(f"  - {niveau}: {count} leçons")

    # Sauvegarder
    with open("test_classification_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[SAVE] Résultats sauvegardés dans test_classification_results.json")
    print("\n[INFO] Si les résultats sont satisfaisants, lancez :")
    print("   python classify_levels.py --all")


if __name__ == "__main__":
    test_classification()
