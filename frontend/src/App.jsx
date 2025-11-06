import React, { useState } from "react";
import EmpatheticJournal from "./components/EmpatheticJournal";
import Login from "./components/Login";
import Register from "./components/Register";

export default function App() {
  const [user, setUser] = useState(localStorage.getItem("username"));
  const [token, setToken] = useState(localStorage.getItem("token"));

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
      <div className="flex justify-between mb-4">
        <h1 className="text-2xl font-bold text-blue-600">
          Welcome, {user} 🌱
        </h1>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
      <EmpatheticJournal token={token} />
    </div>
  );
}
