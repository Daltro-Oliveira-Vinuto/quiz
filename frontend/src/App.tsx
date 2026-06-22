import { useState } from "react";
import { Home } from "./pages/Home";
import { QuizPage } from "./pages/QuizPage";
import { Ranking } from "./pages/Ranking";

type View =
  | { page: "home" }
  | { page: "quiz"; quizId: number }
  | { page: "ranking"; quizId?: number };

export default function App() {
  const [view, setView] = useState<View>({ page: "home" });

  const goHome = () => setView({ page: "home" });
  const goQuiz = (quizId: number) => setView({ page: "quiz", quizId });
  const goRanking = (quizId?: number) => setView({ page: "ranking", quizId });

  if (view.page === "quiz") {
    return (
      <QuizPage
        quizId={view.quizId}
        onHome={goHome}
        onRanking={() => goRanking(view.quizId)}
      />
    );
  }

  if (view.page === "ranking") {
    return <Ranking quizId={view.quizId} onHome={goHome} />;
  }

  return <Home onStart={goQuiz} onRanking={() => goRanking()} />;
}
