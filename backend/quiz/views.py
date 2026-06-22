from django.utils import timezone
from django.db.models import Max, Count, Avg
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

    session.score = request.data.get("score", 0)
    session.total_questions = request.data.get("total_questions", 0)
    session.completed = True
    session.finished_at = timezone.now()
    session.save()

    return Response(QuizSessionResultSerializer(session).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def ranking(request):
    """
    GET /api/ranking/?quiz_id=<id>
    Returns best score per player_name, ordered by percentage desc.
    Excludes 'Anônimo' and incomplete sessions.
    Optional filter by quiz_id.
    """
    quiz_id = request.query_params.get("quiz_id")

    qs = QuizSession.objects.filter(
        completed=True,
        total_questions__gt=0,
    ).exclude(player_name__iexact="anônimo").exclude(player_name="")

    if quiz_id:
        qs = qs.filter(quiz_id=quiz_id)

    # Best session per player (by score then most recent)
    # Group by player_name: pick max score, count games, avg percentage
    from django.db.models import FloatField, ExpressionWrapper, F

    best_per_player = list(
        qs.values("player_name")
        .annotate(
            best_score=Max("score"),
            games_played=Count("id"),
            best_total=Max("total_questions"),
        )
        # sem [:50] aqui
    )

    def sort_key(x):
        total = x["best_total"] or 1
        pct = x["best_score"] / total
        return (-pct, -x["games_played"])

    best_per_player.sort(key=sort_key)
    best_per_player = best_per_player[:50]

    # Attach quiz title if filtered
    quiz_title = None
    if quiz_id:
        try:
            from .models import Quiz
            quiz_title = Quiz.objects.get(pk=quiz_id).title
        except Quiz.DoesNotExist:
            pass

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
