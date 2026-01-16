import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, Shield, Users } from "lucide-react";

const MessageBubble = ({ sender, text, color, isUser }) => (
    <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex w-full mb-4 ${isUser ? "justify-end" : "justify-start"}`}
    >
        <div
            className={`max-w-[70%] p-4 rounded-2xl shadow-sm transition-colors duration-300 ${isUser
                    ? "bg-primary text-primary-foreground rounded-br-none"
                    : `bg-card border-l-4 border-${color}-500 text-card-foreground rounded-bl-none`
                }`}
        >
            {!isUser && (
                <p className={`text-xs font-bold text-${color}-600 dark:text-${color}-400 mb-1 uppercase`}>
                    {sender}
                </p>
            )}
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{text}</p>
        </div>
    </motion.div>
);

export default function AgentRoom({ token }) {
    const [personas, setPersonas] = useState([]);
    const [selectedAgents, setSelectedAgents] = useState([]);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [roomId] = useState("default-room"); // Simple single room for MVP

    const API_BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000") + "/api";

    // Load Personas on Mount
    useEffect(() => {
        fetch(`${API_BASE}/personas`)
            .then((res) => {
                if (!res.ok) throw new Error("Failed to load personas");
                return res.json();
            })
            .then((data) => {
                if (Array.isArray(data)) {
                    setPersonas(data);
                    // Default select all
                    setSelectedAgents(data.map(p => p.id));
                } else {
                    console.error("Invalid format for personas", data);
                    setPersonas([]);
                }
            })
            .catch((err) => {
                console.error("Failed to load personas", err);
                setPersonas([]);
            });
    }, []);

    const toggleAgent = (id) => {
        setSelectedAgents(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        // 1. Add User Message
        const userMsg = { sender: "You", text: input, isUser: true };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE}/rooms/${roomId}/message`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    text: userMsg.text
                })
            });

            const data = await res.json();

            if (!data.is_safe) {
                // Crisis Mode
                setMessages(prev => [...prev, {
                    sender: "Safety System",
                    text: data.crisis_message,
                    color: "red",
                    isUser: false
                }]);
            } else {
                // Add Agent Responses
                const newMsgs = data.responses.map(r => ({
                    sender: r.name,
                    text: r.response,
                    color: r.color,
                    isUser: false
                }));
                setMessages(prev => [...prev, ...newMsgs]);
            }

        } catch (err) {
            console.error("Error sending message:", err);
            setError("Failed to get responses. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col md:flex-row h-[85vh] bg-background rounded-2xl overflow-hidden border border-border shadow-xl transition-colors duration-300">

            {/* 🎭 SIDEBAR: PERSONA TOGGLES */}
            <div className="w-full md:w-64 bg-card p-6 border-r border-border flex flex-col transition-colors duration-300">
                <div className="flex items-center space-x-2 mb-6 text-foreground">
                    <Users size={20} />
                    <h3 className="font-bold">Active Companions</h3>
                </div>

                <div className="space-y-3 flex-1 overflow-y-auto">
                    {personas.map(p => (
                        <div
                            key={p.id}
                            onClick={() => toggleAgent(p.id)}
                            className={`p-3 rounded-xl cursor-pointer transition border-2 ${selectedAgents.includes(p.id)
                                ? `border-${p.color}-400 bg-${p.color}-50 dark:bg-${p.color}-900/20`
                                : "border-transparent hover:bg-muted"
                                }`}
                        >
                            <div className="flex items-center justify-between">
                                <span className={`font-semibold text-${p.color}-700 dark:text-${p.color}-400`}>{p.name}</span>
                                {selectedAgents.includes(p.id) && <span className="text-green-500 text-xs">●</span>}
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">{p.role}</p>
                        </div>
                    ))}
                </div>

                <div className="pt-4 border-t border-border mt-4 text-xs text-muted-foreground">
                    <p className="flex items-center"><Shield size={12} className="mr-1" /> Privately Secured</p>
                </div>
            </div>

            {/* 💬 MAIN CHAT AREA */}
            <div className="flex-1 flex flex-col bg-background transition-colors duration-300">
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    <AnimatePresence>
                        {messages.length === 0 && (
                            <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50">
                                <Users size={48} className="mb-4" />
                                <p>Select companions and start a safe space discussion.</p>
                            </div>
                        )}
                        {messages.map((m, i) => (
                            <MessageBubble
                                key={i}
                                sender={m.sender}
                                text={m.text}
                                color={m.color}
                                isUser={m.isUser}
                            />
                        ))}
                        {loading && (
                            <div className="flex space-x-2 p-4">
                                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-100" />
                                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-200" />
                            </div>
                        )}
                    </AnimatePresence>
                </div>

                {/* ⌨️ INPUT AREA */}
                <div className="p-4 bg-card border-t border-border transition-colors duration-300">
                    <div className="max-w-4xl mx-auto flex space-x-4">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSend()}
                            placeholder="Share your thoughts..."
                            className="flex-1 p-3 rounded-xl border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-colors duration-300"
                            disabled={loading}
                        />
                        <button
                            onClick={handleSend}
                            disabled={loading || !input.trim() || selectedAgents.length === 0}
                            className="px-6 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground transition font-medium"
                        >
                            Send
                        </button>
                    </div>
                    {error && <p className="text-center text-destructive text-sm mt-2">{error}</p>}
                </div>
            </div>
        </div>
    );
}
