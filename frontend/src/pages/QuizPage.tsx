import { useEffect, useRef, useState } from "react";
import { ProgressBar } from "../components/ProgressBar";
import { QuestionCard } from "../components/QuestionCard";
import { ResultCard } from "../components/ResultCard";
import { api } from "../services/api";
import type { QuizDetail } from "../types/quiz";
import styles from "./QuizPage.module.css";

interface Props {
  quizId: number;
  onHome: () => void;
  onRanking: () => void;
}

type Phase = "name" | "playing" | "result";

export function QuizPage({ quizId, onHome, onRanking }: Props) {
  const [quiz, setQuiz] = useState<QuizDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [phase, setPhase] = useState<Phase>("name");
  const [playerName, setPlayerName] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [score, setScore] = useState(0);

  const sessionIdRef = useRef<number | null>(null);

  useEffect(() => {
    api
      .getQuiz(quizId)
      .then(setQuiz)
      .catch(() => setError("Não foi possível carregar o quiz."))
      .finally(() => setLoading(false));
  }, [quizId]);

  const handleStart = async () => {
    const name = playerName.trim() || "Anônimo";
    try {
      const session = await api.createSession(quizId, name);
      sessionIdRef.current = session.id;
    } catch {
      // non-blocking
    }
    setPlayerName(name);
    setPhase("playing");
  };

  const handleAnswer = (isCorrect: boolean) => {
    const newScore = isCorrect ? score + 1 : score;
    setScore(newScore);

    if (!quiz) return;
    const nextIndex = currentIndex + 1;

    if (nextIndex >= quiz.questions.length) {
      if (sessionIdRef.current) {
        api.finishSession(sessionIdRef.current, newScore, quiz.questions.length).catch(() => {});
      }
      setPhase("result");
    } else {
      setCurrentIndex(nextIndex);
    }
  };

  const handleRestart = () => {
    setCurrentIndex(0);
    setScore(0);
    setPhase("name");
  };

  if (loading) {
    return (
      <div className={styles.center}>
        <p className={styles.state}>Carregando quiz…</p>
      </div>
    );
  }

  if (error || !quiz) {
    return (
      <div className={styles.center}>
        <p className={styles.stateError}>{error || "Quiz não encontrado."}</p>
        <button className={styles.backBtn} onClick={onHome}>← Voltar</button>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {phase === "name" && (
          <div className={styles.nameCard}>
            <h2 className={styles.quizTitle}>{quiz.title}</h2>
            {quiz.description && <p className={styles.quizDesc}>{quiz.description}</p>}
            <p className={styles.info}>
              {quiz.questions.length} questões · {quiz.category?.name ?? "Geral"}
            </p>
            <label className={styles.label} htmlFor="playerName">
              Seu nome (opcional)
            </label>
            <input
              id="playerName"
              className={styles.input}
              type="text"
              placeholder="Anônimo"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleStart()}
              maxLength={60}
              autoFocus
            />
            <div className={styles.nameActions}>
              <button className={styles.backBtn} onClick={onHome}>← Voltar</button>
              <button className={styles.startBtn} onClick={handleStart}>Começar →</button>
            </div>
          </div>
        )}

        {phase === "playing" && (
          <>
            <div className={styles.topBar}>
              <button className={styles.backLink} onClick={onHome}>← Sair</button>
              <ProgressBar current={currentIndex + 1} total={quiz.questions.length} />
            </div>
            <QuestionCard
              key={quiz.questions[currentIndex].id}
              question={quiz.questions[currentIndex]}
              questionNumber={currentIndex + 1}
              total={quiz.questions.length}
              onAnswer={handleAnswer}
            />
          </>
        )}

        {phase === "result" && (
          <ResultCard
            score={score}
            total={quiz.questions.length}
            playerName={playerName}
            onRestart={handleRestart}
            onHome={onHome}
            onRanking={onRanking}
          />
        )}
      </div>
    </div>
  );
}
