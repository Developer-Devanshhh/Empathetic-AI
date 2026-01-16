import React, { useState } from "react";
import EmpatheticJournal from "./components/EmpatheticJournal";
import Login from "./components/Login";
import Register from "./components/Register";

import PrivacyDashboard from "./components/PrivacyDashboard";
import AgentRoom from "./components/AgentRoom";

export default function App() {
  const [user, setUser] = useState(localStorage.getItem("username"));
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [view, setView] = useState("journal"); // "journal", "room", "privacy"

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
      <div className="flex flex-col gap-6 mt-10 items-center">
        <Register />
        <Login onLogin={handleLogin} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-600">
          Welcome, {user} 🌱
        </h1>
        <div className="flex space-x-2 bg-gray-200 p-1 rounded-lg">
          <button
            onClick={() => setView("journal")}
            className={`px-4 py-1 rounded transition ${view === "journal" ? "bg-white shadow text-indigo-700 font-medium" : "text-gray-600 hover:text-gray-900"}`}
          >
            Journal
          </button>
          <button
            onClick={() => setView("room")}
            className={`px-4 py-1 rounded transition ${view === "room" ? "bg-white shadow text-indigo-700 font-medium" : "text-gray-600 hover:text-gray-900"}`}
          >
            Companion Room
          </button>
          <button
            onClick={() => setView("privacy")}
            className={`px-4 py-1 rounded transition ${view === "privacy" ? "bg-white shadow text-indigo-700 font-medium" : "text-gray-600 hover:text-gray-900"}`}
          >
            Privacy
          </button>
        </div>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 ml-4"
        >
          Logout
        </button>
      </div>

      {view === "journal" && <EmpatheticJournal token={token} />}
      {view === "room" && <AgentRoom token={token} />}
      {view === "privacy" && <PrivacyDashboard token={token} />}
    </div>
  );
}
