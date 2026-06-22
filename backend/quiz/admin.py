# backend/quiz/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Quiz, Question, Choice, QuizSession


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ("text", "is_correct", "order")
    ordering = ("order",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "quiz", "image_preview", "order", "created_at")
    list_filter = ("quiz",)
    search_fields = ("text", "quiz__title")
    ordering = ("quiz", "order")
    inlines = [ChoiceInline]
    readonly_fields = ("image_preview",)

    @admin.display(description="Questão")
    def short_text(self, obj):
        return obj.text[:80]

    @admin.display(description="Imagem")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = ("text", "image", "explanation", "order")
    ordering = ("order",)
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "questions_per_session", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("title",)
    list_editable = ("is_active",)
    inlines = [QuestionInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct", "order")
    list_filter = ("is_correct", "question__quiz")
    search_fields = ("text", "question__text")
    list_editable = ("is_correct", "order")


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ("player_name", "quiz", "score", "total_questions", "percentage_display", "completed", "started_at")
    list_filter = ("completed", "quiz")
    search_fields = ("player_name", "quiz__title")
    readonly_fields = ("started_at", "finished_at", "percentage_display")
    ordering = ("-started_at",)

    @admin.display(description="Acerto %")
    def percentage_display(self, obj):
        pct = obj.percentage
        color = "#22c55e" if pct >= 70 else "#ef4444"
        return format_html('<strong style="color:{}">{} %</strong>', color, pct)