from django.urls import path
from . import views

urlpatterns = [
    path("quizzes/", views.QuizListView.as_view(), name="quiz-list"),
    path("quizzes/<int:pk>/", views.QuizDetailView.as_view(), name="quiz-detail"),
    path("quiz/answer/", views.check_answer, name="quiz-answer"),
    path("quiz/session/", views.create_session, name="quiz-session-create"),
    path("quiz/session/<int:pk>/finish/", views.finish_session, name="quiz-session-finish"),
    path("ranking/", views.ranking, name="ranking"),
]
