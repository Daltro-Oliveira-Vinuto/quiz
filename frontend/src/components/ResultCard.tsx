import styles from "./ResultCard.module.css";

interface Props {
  score: number;
  total: number;
  playerName: string;
  onRestart: () => void;
  onHome: () => void;
}

export function ResultCard({ score, total, playerName, onRestart, onHome }: Props) {
  const pct = Math.round((score / total) * 100);

  const emoji = pct >= 80 ? "🏆" : pct >= 60 ? "👍" : pct >= 40 ? "📚" : "💪";
  const msg =
    pct >= 80
      ? "Excelente! Você mandou muito bem."
      : pct >= 60
      ? "Bom trabalho! Continue praticando."
      : pct >= 40
      ? "Deu pra ver o caminho — bora revisar!"
      : "Não desiste! Tente novamente.";

  return (
    <div className={styles.card}>
      <div className={styles.emoji}>{emoji}</div>
      <h2 className={styles.title}>Resultado de {playerName}</h2>

      <div className={styles.scoreRing}>
        <svg viewBox="0 0 120 120" className={styles.svg}>
          <circle cx="60" cy="60" r="50" className={styles.track} />
          <circle
            cx="60"
            cy="60"
            r="50"
            className={styles.progress}
            strokeDasharray={`${2 * Math.PI * 50}`}
            strokeDashoffset={`${2 * Math.PI * 50 * (1 - pct / 100)}`}
          />
        </svg>
        <div className={styles.scoreText}>
          <span className={styles.pct}>{pct}%</span>
          <span className={styles.fraction}>
            {score}/{total}
          </span>
        </div>
      </div>

      <p className={styles.msg}>{msg}</p>

      <div className={styles.actions}>
        <button className={styles.btnSecondary} onClick={onHome}>
          ← Início
        </button>
        <button className={styles.btnPrimary} onClick={onRestart}>
          Tentar novamente
        </button>
      </div>
    </div>
  );
}
