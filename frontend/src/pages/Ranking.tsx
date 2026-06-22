import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { RankingEntry } from "../types/quiz";
import styles from "./Ranking.module.css";

interface Props {
  quizId?: number;
  onHome: () => void;
}

const medals: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

export function Ranking({ quizId, onHome }: Props) {
  const [entries, setEntries] = useState<RankingEntry[]>([]);
  const [quizTitle, setQuizTitle] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getRanking(quizId)
      .then((data) => {
        setEntries(data.ranking);
        setQuizTitle(data.quiz_title);
      })
      .catch(() => setError("Não foi possível carregar o ranking."))
      .finally(() => setLoading(false));
  }, [quizId]);

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <button className={styles.backBtn} onClick={onHome}>← Voltar</button>
          <div>
            <h1 className={styles.title}>🏆 Ranking</h1>
            {quizTitle && <p className={styles.subtitle}>{quizTitle}</p>}
          </div>
        </div>

        {loading && <p className={styles.state}>Carregando ranking…</p>}
        {error && <p className={styles.stateError}>{error}</p>}

        {!loading && !error && entries.length === 0 && (
          <p className={styles.state}>Nenhuma partida finalizada ainda. Seja o primeiro!</p>
        )}

        {entries.length > 0 && (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Jogador</th>
                  <th>Melhor score</th>
                  <th>%</th>
                  <th>Partidas</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e) => (
                  <tr key={e.player_name} className={e.position <= 3 ? styles.top3 : ""}>
                  <td className={styles.pos}>
                    {e.position}º {medals[e.position] ?? ""}
                  </td>
                    <td className={styles.name}>{e.player_name}</td>
                    <td className={styles.score}>
                      {e.best_score}/{e.total_questions}
                    </td>
                    <td>
                      <span
                        className={styles.badge}
                        style={{
                          background:
                            e.percentage >= 80
                              ? "#f0fdf4"
                              : e.percentage >= 50
                              ? "#fffbeb"
                              : "#fef2f2",
                          color:
                            e.percentage >= 80
                              ? "#15803d"
                              : e.percentage >= 50
                              ? "#92400e"
                              : "#b91c1c",
                        }}
                      >
                        {e.percentage}%
                      </span>
                    </td>
                    <td className={styles.games}>{e.games_played}x</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
