# backend/quiz/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Quiz listing & detail
    path("quizzes/", views.QuizListView.as_view(), name="quiz-list"),
    path("quizzes/<int:pk>/", views.QuizDetailView.as_view(), name="quiz-detail"),

    # Answer checking (stateless)
    path("quiz/answer/", views.check_answer, name="quiz-answer"),

    # Session lifecycle
    path("quiz/session/", views.create_session, name="quiz-session-create"),
    path("quiz/session/<int:pk>/finish/", views.finish_session, name="quiz-session-finish"),
]