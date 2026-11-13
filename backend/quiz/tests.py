"""
Testes da API do quiz.

Rodam no banco configurado no .env (MySQL por padrão, ou PostgreSQL com
DB_ENGINE=postgres):

    python manage.py test quiz

O usuário do banco precisa de permissão para criar o banco de testes
(test_<nome>). O workflow .github/workflows/db-compat.yml roda os testes
em MySQL 8.0, MySQL 8.4, MariaDB 10.11, MariaDB 11.4 e PostgreSQL 16
a cada push/PR.
"""

from django.db import connection
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Choice, Question, Quiz, QuizSession


class BaseQuizTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="História", description="2ª Guerra")
        cls.quiz = Quiz.objects.create(
            title="Brasil na 2ª Guerra Mundial",
            category=cls.category,
            questions_per_session=3,
        )
        cls.questions = []
        for i in range(5):
            q = Question.objects.create(
                quiz=cls.quiz,
                text=f"Questão {i} — com acentuação e emoji 🇧🇷",
                explanation="Explicação",
                order=i,
            )
            Choice.objects.create(question=q, text="Certa", is_correct=True, order=0)
            Choice.objects.create(question=q, text="Errada", is_correct=False, order=1)
            cls.questions.append(q)

    def setUp(self):
        self.client = APIClient()

    def finished_session(self, name, score, total):
        return QuizSession.objects.create(
            quiz=self.quiz,
            player_name=name,
            score=score,
            total_questions=total,
            completed=True,
        )


class QuizEndpointsTests(BaseQuizTestCase):
    def test_list_quizzes(self):
        r = self.client.get("/api/quizzes/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()[0]["question_count"], 5)

    def test_detail_returns_random_subset(self):
        # order_by("?") vira RAND() no MySQL e RANDOM() no PostgreSQL
        r = self.client.get(f"/api/quizzes/{self.quiz.pk}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["questions"]), 3)

    def test_check_answer(self):
        q = self.questions[0]
        wrong = q.choices.get(is_correct=False)
        r = self.client.post(
            "/api/quiz/answer/",
            {"question_id": q.pk, "choice_id": wrong.pk},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["is_correct"])
        self.assertEqual(r.json()["correct_choice_id"], q.correct_choice.pk)

    def test_unicode_is_stored_intact(self):
        # garante utf8mb4 no MySQL (o utf8 de 3 bytes quebraria o emoji)
        q = Question.objects.get(pk=self.questions[0].pk)
        self.assertIn("🇧🇷", q.text)


class SessionTests(BaseQuizTestCase):
    def create_session(self, name="Kyara"):
        r = self.client.post(
            "/api/quiz/session/", {"quiz": self.quiz.pk, "player_name": name}, format="json"
        )
        self.assertEqual(r.status_code, 201)
        return r.json()["id"]

    def test_full_flow(self):
        sid = self.create_session()
        r = self.client.patch(
            f"/api/quiz/session/{sid}/finish/",
            {"score": 2, "total_questions": 3},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["percentage"], 67)
        self.assertTrue(r.json()["completed"])

    def test_invalid_scores_return_400(self):
        sid = self.create_session()
        for payload in (
            {"score": -1, "total_questions": 3},
            {"score": "abc", "total_questions": 3},
            {"score": 5, "total_questions": 3},
            {},
        ):
            r = self.client.patch(f"/api/quiz/session/{sid}/finish/", payload, format="json")
            self.assertEqual(r.status_code, 400, payload)

        self.assertFalse(QuizSession.objects.get(pk=sid).completed)

    def test_long_player_name_is_rejected_not_truncated(self):
        r = self.client.post(
            "/api/quiz/session/",
            {"quiz": self.quiz.pk, "player_name": "x" * 101},
            format="json",
        )
        self.assertEqual(r.status_code, 400)


class RankingTests(BaseQuizTestCase):
    def ranking(self, **params):
        r = self.client.get("/api/ranking/", params)
        self.assertEqual(r.status_code, 200)
        return r.json()

    def test_ranking_order_and_aggregation(self):
        self.finished_session("Ana", 3, 3)
        self.finished_session("Ana", 1, 3)
        self.finished_session("Bruno", 2, 3)

        data = self.ranking(quiz_id=self.quiz.pk)
        self.assertEqual(data["quiz_title"], self.quiz.title)
        self.assertEqual([e["player_name"] for e in data["ranking"]], ["Ana", "Bruno"])
        self.assertEqual(data["ranking"][0]["games_played"], 2)
        self.assertEqual(data["ranking"][0]["percentage"], 100)

    def test_ranking_excludes_anonymous_and_incomplete(self):
        self.finished_session("Anônimo", 3, 3)
        self.finished_session("anonimo", 3, 3)
        self.finished_session("", 3, 3)
        QuizSession.objects.create(quiz=self.quiz, player_name="Carla", score=0, total_questions=3)

        self.assertEqual(self.ranking()["ranking"], [])

    def test_ranking_grouping_does_not_depend_on_collation(self):
        # A collation padrão do MySQL ignora acento e maiúsculas, então um
        # GROUP BY no banco juntaria estes três nomes num jogador só (no
        # PostgreSQL não). O resultado tem que ser o mesmo nos dois.
        self.finished_session("José", 3, 3)
        self.finished_session("jose", 2, 3)
        self.finished_session("JOSE", 1, 3)

        names = sorted(e["player_name"] for e in self.ranking()["ranking"])
        self.assertEqual(names, sorted(["José", "jose", "JOSE"]))

    def test_unknown_quiz_id(self):
        data = self.ranking(quiz_id=999999)
        self.assertIsNone(data["quiz_title"])
        self.assertEqual(data["ranking"], [])


class DatabaseSettingsTests(TestCase):
    def test_mysql_connection_options(self):
        if connection.vendor != "mysql":
            self.skipTest("só se aplica ao MySQL")

        with connection.cursor() as cursor:
            cursor.execute("SELECT @@SESSION.sql_mode, @@character_set_connection")
            sql_mode, charset = cursor.fetchone()

        self.assertIn("STRICT_TRANS_TABLES", sql_mode)
        self.assertEqual(charset, "utf8mb4")
