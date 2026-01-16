import React, { useState, useEffect, useCallback } from 'react';
import { journalApi } from '../utils/journal';
import { Save, Lock, Cloud, Check } from 'lucide-react';

const Editor = ({ chapterId }) => {
    const [text, setText] = useState("");
    const [saving, setSaving] = useState(false);
    const [lastSaved, setLastSaved] = useState(null);
    const [clientOnly, setClientOnly] = useState(false);
    const [loading, setLoading] = useState(false);

    // Load existing entries when chapter changes
    useEffect(() => {
        if (!chapterId) return;

        const loadEntries = async () => {
            setLoading(true);
            try {
                const entries = await journalApi.getEntries(chapterId);
                // Combine all entries (most recent first, so we reverse for chronological order)
                const combinedText = entries
                    .reverse()
                    .map(e => e.text)
                    .join("\n\n---\n\n");
                setText(combinedText);
            } catch (err) {
                console.error("Failed to load entries", err);
                setText(""); // Start fresh if load fails
            } finally {
                setLoading(false);
            }
        };

        loadEntries();
    }, [chapterId]);

    // Debounce save logic
    useEffect(() => {
        if (!chapterId || !text || loading) return;

        const timer = setTimeout(() => {
            handleSave();
        }, 3000); // Autosave every 3s of inactivity

        return () => clearTimeout(timer);
    }, [text, chapterId, clientOnly, loading]);

    const handleSave = async () => {
        if (!chapterId || !text) return;
        setSaving(true);
        try {
            await journalApi.createEntry(chapterId, text, clientOnly);
            setLastSaved(new Date());
        } catch (err) {
            console.error("Autosave failed", err);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full text-muted-foreground">
                <Cloud className="w-6 h-6 animate-pulse mr-2" />
                Loading your journal...
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-card rounded-3xl shadow-sm border border-border overflow-hidden transition-colors duration-300">
            {/* Toolbar */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card/50 backdrop-blur-sm">
                <div className="text-sm text-muted-foreground">
                    {saving ? (
                        <span className="flex items-center"><Cloud className="w-4 h-4 mr-2 animate-pulse" /> Saving...</span>
                    ) : lastSaved ? (
                        <span className="flex items-center text-green-600 dark:text-green-400"><Check className="w-4 h-4 mr-2" /> Saved {lastSaved.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    ) : (
                        "Start writing..."
                    )}
                </div>

                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => setClientOnly(!clientOnly)}
                        className={`flex items-center px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${clientOnly ? 'bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-300' : 'bg-muted text-muted-foreground hover:bg-muted/80'}`}
                        title="Client-only mode: No AI processing, encrypted locally."
                    >
                        <Lock className="w-3 h-3 mr-1.5" />
                        {clientOnly ? "Private Mode (Client Only)" : "Standard Mode"}
                    </button>

                    <button
                        onClick={handleSave}
                        className="p-2 text-primary hover:bg-primary/10 rounded-full transition-colors"
                        title="Manual Save"
                    >
                        <Save className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Editor Area */}
            <div className="flex-1 p-6 md:p-10 overflow-auto cursor-text" onClick={() => document.getElementById('main-editor').focus()}>
                <textarea
                    id="main-editor"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Write freely. No filters, no judgment..."
                    className="w-full h-full resize-none outline-none text-lg md:text-xl leading-relaxed text-foreground placeholder:text-muted-foreground/50 font-serif bg-transparent"
                    spellCheck="false"
                />
            </div>

            {/* Bottom Status / Stats (Optional) */}
            <div className="px-6 py-3 border-t border-border text-xs text-muted-foreground flex justify-end">
                {text.length} chars
            </div>
        </div>
    );
};

export default Editor;
