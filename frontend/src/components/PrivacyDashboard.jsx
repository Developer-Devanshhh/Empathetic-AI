import React, { useState, useEffect } from 'react';
import { Trash2, AlertTriangle, Database } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function PrivacyDashboard({ token }) {
    const [memories, setMemories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [retention, setRetention] = useState(30); // Default 30 days visualization

    useEffect(() => {
        fetchMemories();
    }, [token]);

    const fetchMemories = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/memories`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                setMemories(await res.json());
            }
        } catch (err) {
            console.error(err);
        }
        setLoading(false);
    };

    const deleteMemory = async (id) => {
        if (!confirm("Are you sure you want to delete this memory?")) return;
        try {
            await fetch(`${API_BASE}/memories/${id}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` }
            });
            setMemories(memories.filter(m => m.id !== id));
        } catch (err) {
            console.error(err);
        }
    };

    const clearAll = async () => {
        if (!confirm("WARNING: This will delete ALL your journal history. This cannot be undone.")) return;
        if (!confirm("Are you absolutely sure?")) return;

        try {
            await fetch(`${API_BASE}/memories`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` }
            });
            setMemories([]);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto mt-10 p-6 bg-white/80 rounded-2xl shadow-lg border border-red-50">
            <div className="flex items-center space-x-3 mb-6">
                <Database className="text-indigo-600" size={28} />
                <h2 className="text-2xl font-bold text-gray-800">Privacy & Memory Control</h2>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                    <h3 className="font-semibold text-blue-900 mb-2">Encryption at Rest</h3>
                    <p className="text-sm text-blue-700">
                        Your journal entries are encrypted using AES-256 before being stored.
                        Only you can see the decrypted text.
                    </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-xl border border-purple-100">
                    <h3 className="font-semibold text-purple-900 mb-2">Retention Policy (Simulated)</h3>
                    <p className="text-sm text-purple-700 mb-3">
                        Current setting: Keep memories for <strong>{retention} days</strong>.
                    </p>
                    <input
                        type="range"
                        min="1" max="365"
                        value={retention}
                        onChange={(e) => setRetention(e.target.value)}
                        className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer"
                    />
                </div>
            </div>

            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-gray-700">Stored Memories ({memories.length})</h3>
                <button
                    onClick={clearAll}
                    className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition"
                >
                    <AlertTriangle size={18} />
                    <span>Forget Everything</span>
                </button>
            </div>

            {loading ? (
                <p className="text-gray-500">Loading encrypted memories...</p>
            ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                    {memories.map((mem) => (
                        <div key={mem.id} className="p-4 bg-white border rounded-xl flex justify-between items-start hover:shadow-sm transition">
                            <div>
                                <p className="font-medium text-gray-800">{mem.text}</p>
                                <div className="flex space-x-3 mt-2 text-xs text-gray-500">
                                    <span>{new Date(mem.metadata.timestamp).toLocaleString()}</span>
                                    <span className="capitalize px-2 py-0.5 bg-gray-100 rounded text-gray-600">{mem.metadata.emotion}</span>
                                    {mem.metadata.safety_flag && <span className="text-red-500 font-bold">Unsafe Flag</span>}
                                </div>
                            </div>
                            <button
                                onClick={() => deleteMemory(mem.id)}
                                className="text-gray-400 hover:text-red-500 p-2"
                                title="Delete this memory"
                            >
                                <Trash2 size={20} />
                            </button>
                        </div>
                    ))}
                    {memories.length === 0 && <p className="text-gray-400 italic">No memories stored securely yet.</p>}
                </div>
            )}
        </div>
    );
}
