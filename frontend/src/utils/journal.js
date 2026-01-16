const API_BASE = "http://localhost:8000/api";

const getHeaders = () => {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
};

export const journalApi = {
    getBooks: async () => {
        const res = await fetch(`${API_BASE}/books`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to fetch books");
        return res.json();
    },

    createBook: async (title, description) => {
        const res = await fetch(`${API_BASE}/books`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ title, description })
        });
        if (!res.ok) throw new Error("Failed to create book");
        return res.json();
    },

    createChapter: async (bookId, title, startDate) => {
        const res = await fetch(`${API_BASE}/books/${bookId}/chapters`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ title, start_date: startDate })
        });
        if (!res.ok) throw new Error("Failed to create chapter");
        return res.json();
    },

    createEntry: async (chapterId, text, clientOnly = false, date = null) => {
        const res = await fetch(`${API_BASE}/chapters/${chapterId}/entries`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({
                text,
                client_only: clientOnly,
                date: date
            })
        });
        if (!res.ok) throw new Error("Failed to save entry");
        return res.json();
    },

    getEntries: async (chapterId) => {
        const res = await fetch(`${API_BASE}/chapters/${chapterId}/entries`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Failed to fetch entries");
        return res.json();
    }
};
