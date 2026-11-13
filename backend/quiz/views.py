from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Quiz, QuizSession
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    AnswerSubmitSerializer,
    AnswerResultSerializer,
    QuizSessionCreateSerializer,
    QuizSessionFinishSerializer,
    QuizSessionResultSerializer,
    RankingSerializer,
)


class QuizListView(generics.ListAPIView):
    """GET /api/quizzes/ — list all active quizzes."""
    permission_classes = [AllowAny]
    serializer_class = QuizListSerializer
    queryset = Quiz.objects.filter(is_active=True).select_related("category")
    pagination_class = None


class QuizDetailView(generics.RetrieveAPIView):
    """GET /api/quizzes/<id>/ — quiz metadata + shuffled questions (no correct answer)."""
    permission_classes = [AllowAny]
    serializer_class = QuizDetailSerializer
    queryset = Quiz.objects.filter(is_active=True)


@api_view(["POST"])
@permission_classes([AllowAny])
def check_answer(request):
    serializer = AnswerSubmitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    question = serializer.validated_data["question"]
    choice = serializer.validated_data["choice"]
    correct = question.correct_choice

    result = {
        "is_correct": choice.is_correct,
        "correct_choice_id": correct.id if correct else None,
        "explanation": question.explanation,
    }
    return Response(AnswerResultSerializer(result).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_session(request):
    serializer = QuizSessionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save()
    return Response(QuizSessionCreateSerializer(session).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def finish_session(request, pk):
    try:
        session = QuizSession.objects.get(pk=pk)
    except QuizSession.DoesNotExist:
        return Response({"detail": "Sessão não encontrada."}, status=404)

    # Valida antes de gravar: sem isso, um valor negativo ou não numérico
    # vira erro 500 no banco (modo estrito do MySQL / CHECK do PostgreSQL).
    serializer = QuizSessionFinishSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    session.score = serializer.validated_data["score"]
    session.total_questions = serializer.validated_data["total_questions"]
    session.completed = True
    session.finished_at = timezone.now()
    session.save()

    return Response(QuizSessionResultSerializer(session).data)


# Nomes tratados como "sem nome" e fora do ranking (comparação em Python,
# independente da collation configurada no banco).
ANONYMOUS_NAMES = {"", "anônimo", "anonimo"}


@api_view(["GET"])
@permission_classes([AllowAny])
def ranking(request):
    """
    GET /api/ranking/?quiz_id=<id>
    Returns best score per player_name, ordered by percentage desc.
    Excludes 'Anônimo' and incomplete sessions.
    Optional filter by quiz_id.

    O agrupamento por jogador é feito em Python, e não com GROUP BY no
    banco, porque no MySQL o GROUP BY em texto segue a collation
    (utf8mb4_0900_ai_ci), que ignora acentos e maiúsculas: "José", "jose"
    e "JOSE" virariam um jogador só, e no PostgreSQL não. Assim o ranking
    é igual nos dois bancos.
    """
    quiz_id = request.query_params.get("quiz_id")

    qs = QuizSession.objects.filter(completed=True, total_questions__gt=0)

    if quiz_id:
        qs = qs.filter(quiz_id=quiz_id)

    stats = {}
    for player_name, score, total in qs.values_list(
        "player_name", "score", "total_questions"
    ).iterator():
        if player_name.strip().casefold() in ANONYMOUS_NAMES:
            continue
        entry = stats.setdefault(
            player_name,
            {"player_name": player_name, "best_score": 0, "best_total": 0, "games_played": 0},
        )
        entry["best_score"] = max(entry["best_score"], score)
        entry["best_total"] = max(entry["best_total"], total)
        entry["games_played"] += 1

    best_per_player = list(stats.values())

    def sort_key(x):
        total = x["best_total"] or 1
        pct = x["best_score"] / total
        # desempate final pelo nome, para a ordem ser sempre a mesma
        return (-pct, -x["games_played"], x["player_name"])

    best_per_player.sort(key=sort_key)
    best_per_player = best_per_player[:50]

    # Attach quiz title if filtered
    quiz_title = None
    if quiz_id:
        quiz_title = Quiz.objects.filter(pk=quiz_id).values_list("title", flat=True).first()

    results = []
    for i, entry in enumerate(best_per_player, start=1):
        total = entry["best_total"] or 1
        results.append({
            "position": i,
            "player_name": entry["player_name"],
            "best_score": entry["best_score"],
            "total_questions": total,
            "percentage": round((entry["best_score"] / total) * 100),
            "games_played": entry["games_played"],
        })

    return Response({
        "quiz_title": quiz_title,
        "ranking": results,
    })
