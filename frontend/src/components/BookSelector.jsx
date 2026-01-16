import React, { useState, useEffect } from 'react';
import { journalApi } from '../utils/journal';
import { ChevronDown, Plus, Book } from 'lucide-react';

const BookSelector = ({ onSelectChapter }) => {
    const [books, setBooks] = useState([]);
    const [selectedBookId, setSelectedBookId] = useState(null);
    const [selectedChapterId, setSelectedChapterId] = useState(null);

    useEffect(() => {
        loadBooks();
    }, []);

    const loadBooks = async () => {
        try {
            const data = await journalApi.getBooks();
            setBooks(data);
            // Auto-select first book if nothing selected
            if (data.length > 0 && !selectedBookId) {
                setSelectedBookId(data[0].book_id);
                if (data[0].chapters && data[0].chapters.length > 0) {
                    const firstChapter = data[0].chapters[0];
                    setSelectedChapterId(firstChapter.chapter_id);
                    onSelectChapter(firstChapter.chapter_id);
                }
            }
        } catch (err) {
            console.error("Failed to load books", err);
        }
    };

    const handleCreateBook = async () => {
        const title = window.prompt("New Journal Title:");
        if (!title) return;
        try {
            const newBook = await journalApi.createBook(title, "");
            const updatedBooks = [...books, newBook];
            setBooks(updatedBooks);
            setSelectedBookId(newBook.book_id);
        } catch (err) {
            console.error(err);
            alert("Failed to create book");
        }
    };

    const handleCreateChapter = async (bookId) => {
        const title = window.prompt("New Chapter Title (e.g., 'March 2026'):");
        if (!title) return;
        try {
            const newChapter = await journalApi.createChapter(bookId, title, new Date().toISOString());

            // Update local state immediately
            const updatedBooks = books.map(b => {
                if (b.book_id === bookId) {
                    return { ...b, chapters: [...(b.chapters || []), newChapter] };
                }
                return b;
            });
            setBooks(updatedBooks);

            // Auto-select the new chapter
            setSelectedChapterId(newChapter.chapter_id);
            onSelectChapter(newChapter.chapter_id);
        } catch (err) {
            console.error(err);
            alert("Failed to create chapter");
        }
    };

    const handleSelectChapter = (chapterId) => {
        setSelectedChapterId(chapterId);
        onSelectChapter(chapterId);
    };

    const activeBook = books.find(b => b.book_id === selectedBookId);

    return (
        <div className="w-64 h-full bg-card border-r border-border flex flex-col transition-colors duration-300">
            {/* Header */}
            <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between mb-2">
                    <h2 className="font-semibold text-foreground tracking-tight">Journals</h2>
                    <button
                        onClick={handleCreateBook}
                        className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-primary transition-colors"
                        title="Create New Journal"
                    >
                        <Plus className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Books List (Accordion style) */}
            <div className="flex-1 overflow-y-auto p-2 space-y-2">
                {books.map(book => (
                    <div key={book.book_id} className="rounded-lg overflow-hidden">
                        {/* Book Header */}
                        <button
                            onClick={() => setSelectedBookId(book.book_id === selectedBookId ? null : book.book_id)}
                            className={`w-full flex items-center justify-between p-2.5 text-sm font-medium transition-colors rounded-md ${book.book_id === selectedBookId
                                    ? "bg-accent text-accent-foreground"
                                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                                }`}
                        >
                            <div className="flex items-center">
                                <Book className="w-4 h-4 mr-2 opacity-70" />
                                <span className="truncate">{book.title}</span>
                            </div>
                            <ChevronDown
                                className={`w-3 h-3 transition-transform duration-200 ${book.book_id === selectedBookId ? "transform rotate-180" : ""
                                    }`}
                            />
                        </button>

                        {/* Chapters List (Expanded) */}
                        {book.book_id === selectedBookId && (
                            <div className="bg-muted/30 mt-1 rounded-md overflow-hidden">
                                {book.chapters?.length > 0 ? (
                                    book.chapters.map(chapter => (
                                        <button
                                            key={chapter.chapter_id}
                                            onClick={() => handleSelectChapter(chapter.chapter_id)}
                                            className={`w-full text-left flex items-center pl-9 pr-3 py-2 text-xs transition-colors border-l-2 ${selectedChapterId === chapter.chapter_id
                                                    ? "border-primary text-primary bg-primary/5 font-medium"
                                                    : "border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/50"
                                                }`}
                                        >
                                            <span className="truncate">{chapter.title}</span>
                                        </button>
                                    ))
                                ) : (
                                    <div className="pl-9 pr-3 py-2 text-xs text-muted-foreground italic">
                                        No chapters yet
                                    </div>
                                )}
                                <button
                                    onClick={() => handleCreateChapter(book.book_id)}
                                    className="w-full text-left pl-9 pr-3 py-2 text-xs text-muted-foreground hover:text-primary transition-colors flex items-center"
                                >
                                    <Plus className="w-3 h-3 mr-1" /> Add Chapter
                                </button>
                            </div>
                        )}
                    </div>
                ))}

                {books.length === 0 && (
                    <div className="text-center p-4">
                        <p className="text-xs text-muted-foreground">No journals yet.</p>
                        <button
                            onClick={handleCreateBook}
                            className="text-xs text-primary hover:underline mt-1"
                        >
                            Create your first one
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default BookSelector;
