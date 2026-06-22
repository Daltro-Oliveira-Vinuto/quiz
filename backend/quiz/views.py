# backend/quiz/views.py

from django.shortcuts import render

# Create your views here.
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
    QuizSessionResultSerializer,
)


class QuizListView(generics.ListAPIView):
    """GET /api/quizzes/ — list all active quizzes."""
    permission_classes = [AllowAny]
    serializer_class = QuizListSerializer
    queryset = Quiz.objects.filter(is_active=True).select_related("category")


class QuizDetailView(generics.RetrieveAPIView):
    """GET /api/quizzes/<id>/ — quiz metadata + shuffled questions (no correct answer)."""
    permission_classes = [AllowAny]
    serializer_class = QuizDetailSerializer
    queryset = Quiz.objects.filter(is_active=True)


@api_view(["POST"])
@permission_classes([AllowAny])
def check_answer(request):
    """
    POST /api/quiz/answer/
    Body: { question_id, choice_id }
    Returns: { is_correct, correct_choice_id, explanation }
    """
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
    """POST /api/quiz/session/ — start a new quiz session."""
    serializer = QuizSessionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save()
    return Response(QuizSessionCreateSerializer(session).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def finish_session(request, pk):
    """
    PATCH /api/quiz/session/<pk>/finish/
    Body: { score, total_questions }
    """
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