import React, { useState } from 'react';
import BookSelector from './BookSelector';
import Editor from './Editor';

const JournalPage = () => {
    const [selectedChapterId, setSelectedChapterId] = useState(null);

    return (
        <div className="flex-1 flex overflow-hidden bg-background transition-colors duration-300">
            {/* Sidebar */}
            <BookSelector onSelectChapter={setSelectedChapterId} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                <div className="flex-1 overflow-y-auto p-6 md:p-8">
                    {selectedChapterId ? (
                        <Editor chapterId={selectedChapterId} />
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed border-border rounded-xl m-4">
                            <p>Select a journal chapter to start writing</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default JournalPage;
