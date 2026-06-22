import { useEffect, useState } from "react";
import { QuizCard } from "../components/QuizCard";
import { api } from "../services/api";
import type { QuizListItem } from "../types/quiz";
import styles from "./Home.module.css";

interface Props {
  onStart: (id: number) => void;
  onRanking: () => void;
}

export function Home({ onStart, onRanking }: Props) {
  const [quizzes, setQuizzes] = useState<QuizListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
    .listQuizzes()
    .then((data) => {
      console.log("data:", data);
      setQuizzes(data);
    })
    .catch(() => setError("Não foi possível carregar os quizzes."))
    .finally(() => setLoading(false));
  }, []);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerTop}>

          <div className={styles.logoContainer}>
          <img
            src={import.meta.env.VITE_LOGO_URL}
            alt="Museu Virtual da FEB"
            className={styles.logoImage}
          />

          <h1 className={styles.logo}>
            Quiz do Museu Virtual da FEB
          </h1>
          
        </div>
          
          <button className={styles.rankingBtn} onClick={onRanking}>
            🏆 Ranking geral
          </button>
        </div>
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