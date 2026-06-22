export interface Choice {
  id: number;
  text: string;
  order: number;
}

export interface Question {
  id: number;
  text: string;
  image_url: string | null;
  choices: Choice[];
  order: number;
}

export interface QuizListItem {
  id: number;
  title: string;
  description: string;
  category: { id: number; name: string; description: string } | null;
  questions_per_session: number;
  question_count: number;
}

export interface QuizDetail extends QuizListItem {
  questions: Question[];
}

export interface AnswerResult {
  is_correct: boolean;
  correct_choice_id: number;
  explanation: string;
}

export interface SessionResult {
  id: number;
  quiz_title: string;
  player_name: string;
  score: number;
  total_questions: number;
  percentage: number;
  completed: boolean;
  started_at: string;
  finished_at: string;
}
