import { useState } from "react";
import { Home } from "./pages/Home";
import { QuizPage } from "./pages/QuizPage";

type View = { page: "home" } | { page: "quiz"; quizId: number };

export default function App() {
  const [view, setView] = useState<View>({ page: "home" });

  const goHome = () => setView({ page: "home" });
  const goQuiz = (quizId: number) => setView({ page: "quiz", quizId });

  if (view.page === "quiz") {
    return <QuizPage quizId={view.quizId} onHome={goHome} />;
  }

  return <Home onStart={goQuiz} />;
}
