import { Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import Landing from "./pages/Landing.jsx";
import Analyze from "./pages/Analyze.jsx";
import Quiz from "./pages/Quiz.jsx";
import Result from "./pages/Result.jsx";
import History from "./pages/History.jsx";
import Achievements from "./pages/Achievements.jsx";
import NotFound from "./pages/NotFound.jsx";
import { AppProvider } from "./context/AppContext.jsx";
import { useKonami } from "./hooks/useKonami.js";
import toast from "react-hot-toast";

function KonamiListener() {
  useKonami(() => {
    toast("🎮 Konami code accepted. You are 0% cooked.", { icon: "🥚", duration: 5000 });
  });
  return null;
}

export default function App() {
  return (
    <AppProvider>
      <KonamiListener />
      <div className="flex min-h-full flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/quiz" element={<Quiz />} />
            <Route path="/result/:id" element={<Result />} />
            <Route path="/history" element={<History />} />
            <Route path="/achievements" element={<Achievements />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
      </div>

      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: "#17171c",
            color: "#f5f5f7",
            border: "1px solid rgba(255,255,255,0.08)",
          },
        }}
      />
    </AppProvider>
  );
}