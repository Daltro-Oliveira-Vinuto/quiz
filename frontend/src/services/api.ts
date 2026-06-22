import type { AnswerResult, QuizDetail, QuizListItem, RankingResponse, SessionResult } from "../types/quiz";

const BASE = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api").replace(/\/$/, "");

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listQuizzes: () => request<QuizListItem[]>("/quizzes/"),

  getQuiz: (id: number) => request<QuizDetail>(`/quizzes/${id}/`),

  checkAnswer: (question_id: number, choice_id: number) =>
    request<AnswerResult>("/quiz/answer/", {
      method: "POST",
      body: JSON.stringify({ question_id, choice_id }),
    }),

  createSession: (quiz: number, player_name: string) =>
    request<{ id: number }>("/quiz/session/", {
      method: "POST",
      body: JSON.stringify({ quiz, player_name }),
    }),

  finishSession: (sessionId: number, score: number, total_questions: number) =>
    request<SessionResult>(`/quiz/session/${sessionId}/finish/`, {
      method: "PATCH",
      body: JSON.stringify({ score, total_questions }),
    }),

  getRanking: (quizId?: number) => {
    const qs = quizId ? `?quiz_id=${quizId}` : "";
    return request<RankingResponse>(`/ranking/${qs}`);
  },
};
