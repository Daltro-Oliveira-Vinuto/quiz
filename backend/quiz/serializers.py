# backend/quiz/serializers.py

from rest_framework import serializers
from .models import Category, Quiz, Question, Choice, QuizSession


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        # Never expose is_correct to the client during a quiz
        fields = ["id", "text", "order"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text", "image_url", "choices", "order"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class QuizListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "category", "questions_per_session", "question_count"]

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    """Returns quiz metadata + shuffled questions for a session."""
    category = CategorySerializer(read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "category", "questions_per_session", "questions"]

    def get_questions(self, obj):
        qs = obj.questions.prefetch_related("choices").order_by("?")[: obj.questions_per_session]
        return QuestionSerializer(qs, many=True).data


# ---- Answer checking ----

class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()

    def validate(self, data):
        try:
            question = Question.objects.get(pk=data["question_id"])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Questão não encontrada.")

        if not question.choices.filter(pk=data["choice_id"]).exists():
            raise serializers.ValidationError("Alternativa não pertence a esta questão.")

        data["question"] = question
        data["choice"] = question.choices.get(pk=data["choice_id"])
        return data


class AnswerResultSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()
    correct_choice_id = serializers.IntegerField()
    explanation = serializers.CharField(allow_blank=True)


# ---- Session ----

class QuizSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSession
        fields = ["id", "quiz", "player_name"]


class QuizSessionResultSerializer(serializers.ModelSerializer):
    percentage = serializers.IntegerField(read_only=True)
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)

    class Meta:
        model = QuizSession
        fields = [
            "id", "quiz_title", "player_name",
            "score", "total_questions", "percentage",
            "completed", "started_at", "finished_at",
        ]


