import { useState } from "react";
import type { AnswerResult, Question } from "../types/quiz";
import { api } from "../services/api";
import styles from "./QuestionCard.module.css";

interface Props {
  question: Question;
  questionNumber: number;
  total: number;
  onAnswer: (isCorrect: boolean) => void;
}

type ChoiceState = "idle" | "correct" | "wrong" | "reveal";

export function QuestionCard({ question, questionNumber, total, onAnswer }: Props) {
  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [loading, setLoading] = useState(false);

  const choiceState = (choiceId: number): ChoiceState => {
    if (!result) return "idle";
    if (choiceId === result.correct_choice_id) return "correct";
    if (choiceId === selected) return "wrong";
    return "idle";
  };

  const handleSelect = async (choiceId: number) => {
    if (selected !== null || loading) return;
    setSelected(choiceId);
    setLoading(true);
    try {
      const res = await api.checkAnswer(question.id, choiceId);
      setResult(res);
    } catch {
      // ignore silently — still mark as answered
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    onAnswer(result?.is_correct ?? false);
  };

  return (
    <div className={styles.card}>
      <p className={styles.counter}>
        Questão {questionNumber} de {total}
      </p>

      {question.image_url && (
        <div className={styles.imageWrapper}>
          <img src={question.image_url} alt="Imagem da questão" className={styles.image} />
        </div>
      )}

      <h3 className={styles.questionText}>{question.text}</h3>

      <ul className={styles.choices}>
        {question.choices.map((choice) => {
          const state = choiceState(choice.id);
          return (
            <li key={choice.id}>
              <button
                className={`${styles.choiceBtn} ${styles[state]}`}
                onClick={() => handleSelect(choice.id)}
                disabled={selected !== null}
              >
                {choice.text}
                {state === "correct" && <span className={styles.icon}>✓</span>}
                {state === "wrong" && <span className={styles.icon}>✗</span>}
              </button>
            </li>
          );
        })}
      </ul>

      {result && (
        <div className={`${styles.feedback} ${result.is_correct ? styles.feedbackOk : styles.feedbackErr}`}>
          <strong>{result.is_correct ? "🎉 Correto!" : "❌ Errado!"}</strong>
          {result.explanation && <p className={styles.explanation}>{result.explanation}</p>}
        </div>
      )}

      {result && (
        <button className={styles.nextBtn} onClick={handleNext}>
          {questionNumber === total ? "Ver resultado →" : "Próxima →"}
        </button>
      )}

      {loading && <p className={styles.loading}>Verificando…</p>}
    </div>
  );
}
