from rest_framework import serializers
from .models import Category, Quiz, Question, Choice, QuizSession


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "order"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "text", "image_url", "choices", "order"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class QuizListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "category", "questions_per_session", "question_count"]

    def get_question_count(self, obj):
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "category", "questions_per_session", "questions"]

    def get_questions(self, obj):
        qs = obj.questions.prefetch_related("choices").order_by("?")[: obj.questions_per_session]
        return QuestionSerializer(qs, many=True, context=self.context).data


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


# ---- Ranking ----

class RankingEntrySerializer(serializers.Serializer):
    position = serializers.IntegerField()
    player_name = serializers.CharField()
    best_score = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    percentage = serializers.IntegerField()
    games_played = serializers.IntegerField()


class RankingSerializer(serializers.Serializer):
    quiz_title = serializers.CharField(allow_null=True)
    ranking = RankingEntrySerializer(many=True)
