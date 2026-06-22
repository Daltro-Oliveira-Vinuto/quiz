import { useEffect, useState } from "react";
import { QuizCard } from "../components/QuizCard";
import { api } from "../services/api";
import type { QuizListItem } from "../types/quiz";
import styles from "./Home.module.css";

interface Props {
  onStart: (quizId: number) => void;
}

export function Home({ onStart }: Props) {
  const [quizzes, setQuizzes] = useState<QuizListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listQuizzes()
      .then(setQuizzes)
      .catch(() => setError("Não foi possível carregar os quizzes."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.logo}>🧠 QuizApp</h1>
        <p className={styles.subtitle}>Escolha um quiz e teste seus conhecimentos</p>
      </header>

      {loading && <p className={styles.state}>Carregando quizzes…</p>}
      {error && <p className={styles.stateError}>{error}</p>}

      {!loading && !error && quizzes.length === 0 && (
        <p className={styles.state}>Nenhum quiz disponível no momento.</p>
      )}

      <div className={styles.grid}>
        {quizzes.map((q) => (
          <QuizCard key={q.id} quiz={q} onStart={onStart} />
        ))}
      </div>
    </div>
  );
}
