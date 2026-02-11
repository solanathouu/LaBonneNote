"""Service de génération de quiz à partir du contenu des leçons."""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class QuizService:
    """Service pour générer et valider des quiz QCM."""

    def __init__(self, rag_chain):
        """Initialise le service de quiz.

        Args:
            rag_chain: Instance de RAGChain pour accéder aux leçons.
        """
        self.rag_chain = rag_chain
        # LLM avec temperature plus haute pour créativité dans les questions
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        logger.info("QuizService initialisé")

    async def generate_quiz(
        self,
        matiere: str,
        titre: str,
        nb_questions: int = 5,
        niveau: str = "college"
    ) -> Dict:
        """Génère un quiz à partir du contenu d'une leçon.

        Args:
            matiere: Matière de la leçon (mathematiques, francais, etc.)
            titre: Titre exact de la leçon
            nb_questions: Nombre de questions à générer (3-10)
            niveau: Niveau scolaire (6eme, 5eme, 4eme, 3eme, college)

        Returns:
            Dict contenant le quiz complet avec questions.

        Raises:
            ValueError: Si la leçon n'existe pas ou n'a pas assez de contenu.
        """
        logger.info(f"Génération quiz: {matiere} - {titre} ({nb_questions} questions)")

        # 1. Récupérer le contenu complet de la leçon
        try:
            lesson = self.rag_chain.get_lesson_content(matiere, titre)
        except Exception as e:
            logger.error(f"Leçon non trouvée: {e}")
            raise ValueError(f"Leçon '{titre}' non trouvée pour {matiere}")

        # Vérifier qu'il y a assez de contenu
        if not lesson or "contenu_complet" not in lesson:
            raise ValueError("Leçon sans contenu")

        # 2. Extraire et sélectionner des chunks diversifiés
        chunks = self._extract_chunks_from_lesson(lesson)
        if len(chunks) < nb_questions:
            logger.warning(f"Seulement {len(chunks)} chunks disponibles pour {nb_questions} questions")
            nb_questions = len(chunks)

        selected_chunks = self._select_diverse_chunks(chunks, nb_questions)

        # 3. Générer questions en parallèle (asyncio.gather)
        logger.info(f"Génération de {nb_questions} questions en parallèle...")
        tasks = [
            self._generate_question(chunk, niveau, i + 1)
            for i, chunk in enumerate(selected_chunks)
        ]
        questions = await asyncio.gather(*tasks)

        # 4. Filtrer les questions valides (fallback si erreur parsing)
        valid_questions = [q for q in questions if q is not None]

        if not valid_questions:
            raise ValueError("Aucune question valide générée")

        # 5. Construire le quiz final
        quiz_id = str(uuid.uuid4())
        quiz = {
            "quiz_id": quiz_id,
            "titre": titre,
            "matiere": matiere,
            "niveau": niveau,
            "nb_questions": len(valid_questions),
            "questions": valid_questions,
            "created_at": datetime.now().isoformat()
        }

        logger.info(f"✅ Quiz généré avec succès: {len(valid_questions)} questions")
        return quiz

    def _extract_chunks_from_lesson(self, lesson: Dict) -> List[str]:
        """Extrait les chunks de texte depuis une leçon.

        Args:
            lesson: Dictionnaire de leçon avec contenu_complet

        Returns:
            Liste de chunks de texte (strings).
        """
        contenu = lesson.get("contenu_complet", "")

        # Découper le contenu en paragraphes (chunks naturels)
        paragraphs = [p.strip() for p in contenu.split("\n\n") if p.strip()]

        # Filtrer les paragraphes trop courts (< 100 chars)
        chunks = [p for p in paragraphs if len(p) >= 100]

        return chunks

    def _select_diverse_chunks(self, chunks: List[str], nb_questions: int) -> List[str]:
        """Sélectionne des chunks espacés uniformément pour diversité.

        Args:
            chunks: Liste de tous les chunks disponibles
            nb_questions: Nombre de chunks à sélectionner

        Returns:
            Liste de chunks sélectionnés.
        """
        total = len(chunks)

        if total <= nb_questions:
            return chunks

        # Prendre des chunks espacés uniformément
        step = total // nb_questions
        selected_indices = [i * step for i in range(nb_questions)]

        return [chunks[i] for i in selected_indices]

    async def _generate_question(
        self,
        chunk: str,
        niveau: str,
        index: int
    ) -> Dict:
        """Génère une question QCM depuis un chunk de texte.

        Args:
            chunk: Texte du chunk à utiliser comme contexte
            niveau: Niveau scolaire pour adapter la difficulté
            index: Numéro de la question (pour l'ID)

        Returns:
            Dict avec la question générée, ou None si erreur.
        """
        from prompts import QUIZ_GENERATION_PROMPT

        prompt = QUIZ_GENERATION_PROMPT.format(
            context=chunk[:1000],  # Limiter à 1000 chars pour éviter dépassement tokens
            niveau=niveau
        )

        try:
            # Appel asynchrone au LLM
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()

            # Nettoyer le JSON si enveloppé dans des backticks
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            # Parser le JSON
            question_data = json.loads(content)

            # Valider la structure
            if not self._validate_question_structure(question_data):
                logger.warning(f"Question {index} invalide, utilisation fallback")
                return self._fallback_question(index)

            # Ajouter l'ID
            question_data["id"] = index

            logger.info(f"Question {index} générée avec succès")
            return question_data

        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON question {index}: {e}")
            logger.error(f"Contenu reçu: {content[:200]}")
            return self._fallback_question(index)

        except Exception as e:
            logger.error(f"Erreur génération question {index}: {e}")
            return self._fallback_question(index)

    def _validate_question_structure(self, question_data: Dict) -> bool:
        """Valide qu'une question a la structure correcte.

        Args:
            question_data: Dictionnaire de question à valider

        Returns:
            True si valide, False sinon.
        """
        required_fields = ["question", "options", "correct_answer", "explanation"]

        # Vérifier présence des champs
        for field in required_fields:
            if field not in question_data:
                logger.warning(f"Champ manquant: {field}")
                return False

        # Vérifier 4 options
        if not isinstance(question_data["options"], list) or len(question_data["options"]) != 4:
            logger.warning(f"Options invalides: {question_data.get('options')}")
            return False

        # Vérifier correct_answer est un index valide (0-3)
        if not isinstance(question_data["correct_answer"], int) or not (0 <= question_data["correct_answer"] <= 3):
            logger.warning(f"Index correct_answer invalide: {question_data.get('correct_answer')}")
            return False

        return True

    def _fallback_question(self, index: int) -> Dict:
        """Crée une question de fallback en cas d'erreur.

        Args:
            index: Numéro de la question

        Returns:
            Question générique valide.
        """
        return {
            "id": index,
            "question": "Cette question n'a pas pu être générée correctement. Passez à la suivante.",
            "options": [
                "Option A (placeholder)",
                "Option B (placeholder)",
                "Option C (placeholder)",
                "Option D (placeholder)"
            ],
            "correct_answer": 0,
            "explanation": "Question de fallback suite à une erreur de génération."
        }

    def validate_answers(
        self,
        quiz_id: str,
        questions: List[Dict],
        answers: List[int]
    ) -> Dict:
        """Valide les réponses d'un quiz et calcule le score.

        Args:
            quiz_id: ID du quiz
            questions: Liste des questions du quiz
            answers: Liste des réponses de l'utilisateur (indices 0-3)

        Returns:
            Dict avec score, pourcentage, niveau de performance et détails.
        """
        logger.info(f"Validation quiz {quiz_id}: {len(answers)} réponses")

        results = []
        score = 0

        for i, (question, user_answer) in enumerate(zip(questions, answers)):
            correct_answer = question["correct_answer"]
            is_correct = (user_answer == correct_answer)

            if is_correct:
                score += 1

            results.append({
                "question_id": i + 1,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", "")
            })

        # Calculer le pourcentage
        total = len(questions)
        percentage = (score / total) * 100 if total > 0 else 0

        # Déterminer le niveau de performance
        if percentage >= 80:
            performance = "Excellent"
        elif percentage >= 60:
            performance = "Bien"
        elif percentage >= 40:
            performance = "Moyen"
        else:
            performance = "À revoir"

        logger.info(f"Score: {score}/{total} ({percentage:.0f}%) - {performance}")

        return {
            "score": score,
            "total": total,
            "percentage": percentage,
            "performance_level": performance,
            "results": results
        }
