import type { QuizListItem } from "../types/quiz";
import styles from "./QuizCard.module.css";

interface Props {
  quiz: QuizListItem;
  onStart: (id: number) => void;
}

export function QuizCard({ quiz, onStart }: Props) {
  return (
    <article className={styles.card}>
      <div className={styles.meta}>
        {quiz.category && <span className={styles.tag}>{quiz.category.name}</span>}
        <span className={styles.count}>{quiz.question_count} questões</span>
      </div>
      <h2 className={styles.title}>{quiz.title}</h2>
      {quiz.description && <p className={styles.desc}>{quiz.description}</p>}
      <button className={styles.btn} onClick={() => onStart(quiz.id)}>
        Começar →
      </button>
    </article>
  );
}
