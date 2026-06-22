# backend/quiz/models.py

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="quizzes"
    )
    questions_per_session = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    image = models.ImageField(upload_to="questions/", blank=True, null=True)
    explanation = models.TextField(blank=True, help_text="Explicação exibida após resposta")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"[{self.quiz.title}] {self.text[:60]}"

    @property
    def correct_choice(self):
        return self.choices.filter(is_correct=True).first()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"
        ordering = ["order"]

    def __str__(self):
        marker = "✓" if self.is_correct else "✗"
        return f"{marker} {self.text[:60]}"


class QuizSession(models.Model):
    """Tracks a user's quiz attempt (anonymous or named)."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="sessions")
    player_name = models.CharField(max_length=100, blank=True, default="Anônimo")
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Sessão de Quiz"
        verbose_name_plural = "Sessões de Quiz"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.player_name} — {self.quiz.title} ({self.score}/{self.total_questions})"

    @property
    def percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)