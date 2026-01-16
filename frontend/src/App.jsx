import React, { useState, useEffect } from "react";
import JournalPage from "./components/JournalPage";
import Login from "./components/Login";
import Register from "./components/Register";
import PrivacyDashboard from "./components/PrivacyDashboard";
import AgentRoom from "./components/AgentRoom";
import { Moon, Sun, LogOut } from "lucide-react";

export default function App() {
  const [user, setUser] = useState(localStorage.getItem("username"));
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [view, setView] = useState("journal"); // "journal", "room", "privacy"
  const [darkMode, setDarkMode] = useState(localStorage.getItem("theme") === "dark");

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  const handleLogin = (username, token) => {
    localStorage.setItem("username", username);
    localStorage.setItem("token", token);
    setUser(username);
    setToken(token);
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setToken(null);
  };

  if (!user || !token) {
    return (
      <div className="flex flex-col gap-6 mt-10 items-center justify-center min-h-screen bg-background text-foreground transition-colors duration-300">
        <div className="w-full max-w-md">
          <h1 className="text-3xl font-bold text-center mb-8 bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">NeuroLog</h1>
          <Login onLogin={handleLogin} />
          <div className="mt-8 pt-8 border-t border-border">
            <p className="text-center text-muted-foreground mb-4">New here?</p>
            <Register />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300 flex flex-col">
      {/* Top Navigation Bar */}
      <nav className="bg-card border-b border-border px-6 py-3 flex justify-between items-center sticky top-0 z-40 transition-colors duration-300">
        <div className="flex items-center space-x-2">
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
            NeuroLog
          </span>
        </div>

        <div className="flex bg-muted p-1 rounded-lg">
          {["journal", "room", "privacy"].map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all capitalize ${view === v
                  ? "bg-background shadow-sm text-primary"
                  : "text-muted-foreground hover:text-foreground"
                }`}
            >
              {v}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <span className="text-sm text-muted-foreground hidden md:block">Hi, {user}</span>
          <button
            onClick={handleLogout}
            className="text-sm text-destructive hover:text-destructive/80 font-medium flex items-center"
          >
            <LogOut size={16} className="ml-1" />
          </button>
        </div>
      </nav>

      <div className="flex-1">
        {view === "journal" && <JournalPage />}
        {view === "room" && <AgentRoom token={token} />}
        {view === "privacy" && <PrivacyDashboard token={token} />}
      </div>
    </div>
  );
}
