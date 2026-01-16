import React, { useState } from 'react';
import { motion } from 'framer-motion';

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Smile, Frown, Meh } from 'lucide-react';

// Temporary fix — using plain HTML equivalents until shadcn/ui is set up
const Card = ({ children, className }) => (
  <div className={`rounded-2xl shadow p-4 bg-white ${className || ""}`}>{children}</div>
);
const CardContent = ({ children, className }) => (
  <div className={className || ""}>{children}</div>
);
const Button = ({ children, ...props }) => (
  <button
    {...props}
    className="px-4 py-2 bg-indigo-500 text-white rounded-xl hover:bg-indigo-600 transition"
  >
    {children}
  </button>
);
const Textarea = ({ ...props }) => (
  <textarea
    {...props}
    className="w-full p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
  />
);


import { generateEmbedding } from '../utils/embeddings';

// NEW (after authentication)
export default function EmpatheticJournal({ token }) {
  const [entry, setEntry] = useState('');
  const [emotion, setEmotion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // Use your backend API URL
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Fallback mock analyzer (if backend not reachable)

  const mockAnalyze = (text) => {
    const lower = text.toLowerCase();
    if (lower.includes('happy') || lower.includes('joy'))
      return { emotion: 'joy', confidence: 0.9, message: 'You sound happy today!' };
    if (lower.includes('sad') || lower.includes('lonely'))
      return { emotion: 'sadness', confidence: 0.85, message: 'It seems you are feeling low.' };
    return { emotion: 'neutral', confidence: 0.7, message: 'I sense a calm tone in your entry.' };
  };

  const handleAnalyze = async () => {
    if (!entry.trim()) return;
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/analyze_emotion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: entry }),
      });

      if (!response.ok) throw new Error('Backend not reachable');

      const data = await response.json();
      setEmotion(data);
      setHistory((prev) => [...prev, { ...data, text: entry, date: new Date().toLocaleString() }]);
    } catch (error) {
      console.warn('Falling back to local mock:', error);
      const data = mockAnalyze(entry);
      setEmotion(data);
      setHistory((prev) => [...prev, { ...data, text: entry, date: new Date().toLocaleString() }]);
    }

    setLoading(false);
  };
  // Submit journal entry to backend
  const handleSubmitJournal = async () => {
    if (!entry.trim()) return;
    setLoading(true);
    try {
      // Generate embedding on client
      let embedding = null;
      try {
        embedding = await generateEmbedding(entry);
        console.log("Generated client-side embedding:", embedding.length);
      } catch (err) {
        console.error("Embedding generation failed, falling back to server:", err);
      }

      const response = await fetch(`${API_BASE}/journal`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: localStorage.getItem("username"),
          text: entry,
          embedding: embedding // Send vector if generated
        }),
      });



      if (!response.ok) throw new Error("Failed to submit journal");
      const data = await response.json();
      setHistory((prev) => [
        ...prev,
        {
          text: entry,
          emotion: data.emotion,
          confidence: 1,
          reply: data.reply,
          date: new Date().toLocaleString(),
        },
      ]);
      setEmotion({
        emotion: data.emotion,
        confidence: 1,
        message: data.reply,
      });
    } catch (error) {
      console.error("Error submitting journal:", error);
    } finally {
      setLoading(false);
    }
  };



  const emotionIcon = (emo) => {
    switch (emo) {
      case 'joy':
        return <Smile className="text-yellow-500" />;
      case 'sadness':
        return <Frown className="text-blue-500" />;
      default:
        return <Meh className="text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 p-6 flex flex-col items-center">
      <motion.h1
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-bold mb-8 text-gray-800"
      >
        Empathetic AI Journal
      </motion.h1>

      <Card className="w-full max-w-3xl shadow-lg bg-white/70 backdrop-blur-md">
        <CardContent className="p-6">
          <Textarea
            placeholder="How are you feeling today? Write your thoughts here..."
            value={entry}
            onChange={(e) => setEntry(e.target.value)}
            className="w-full min-h-[150px] text-lg p-4 rounded-2xl border-gray-300 focus:ring-2 focus:ring-indigo-400"
          />
          <div className="mt-4 flex justify-end">
            <Button onClick={handleAnalyze} disabled={loading || !entry.trim()}>
              {loading ? 'Analyzing...' : 'Analyze Emotion'}
            </Button>
            <Button
              onClick={handleSubmitJournal}
              disabled={loading || !entry.trim()}
              className="ml-2 bg-green-500 hover:bg-green-600 "
            >
              {loading ? "Saving..." : "Save & Reflect"}
            </Button>

          </div>
        </CardContent>
      </Card>

      {emotion && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-8 w-full max-w-3xl p-6 bg-white/60 rounded-2xl shadow-md flex items-center space-x-4"
        >
          {emotionIcon(emotion.emotion)}
          <div>
            <h2 className="text-xl font-semibold capitalize">{emotion.emotion}</h2>
            <p className="text-gray-700">{emotion.message}</p>
            <p className="text-xs text-gray-500 mt-1">
              Confidence: {emotion.confidence ? emotion.confidence.toFixed(2) : '—'}
            </p>
          </div>
        </motion.div>
      )}

      {history.length > 0 && (
        <div className="mt-10 w-full max-w-4xl">
          <h3 className="text-2xl font-semibold mb-4 text-gray-800">Mood Trends</h3>
          <Card className="bg-white/70 shadow-lg p-4">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={history.map((h, i) => ({
                  index: i + 1,
                  confidence: h.confidence,
                }))}
              >
                <XAxis dataKey="index" label={{ value: 'Entry', position: 'insideBottom', offset: -5 }} />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Line type="monotone" dataKey="confidence" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>
      )}
    </div>
  );
}
