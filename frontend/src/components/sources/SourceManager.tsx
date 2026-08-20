'use client';

import React, { useState } from 'react';
import { DocumentItem } from '@/lib/types';
import { SourceCard } from './SourceCard';
import { AddSourceModal } from './AddSourceModal';
import { Plus, Database, Sparkles } from 'lucide-react';
import { deleteDocument } from '@/lib/api';

interface SourceManagerProps {
  sessionId: string;
  documents: DocumentItem[];
  onDocumentsChange: (docs: DocumentItem[]) => void;
  onOpenQuiz: () => void;
}

export const SourceManager: React.FC<SourceManagerProps> = ({
  sessionId,
  documents,
  onDocumentsChange,
  onOpenQuiz,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSourceAdded = (doc: DocumentItem) => {
    onDocumentsChange([doc, ...documents]);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      onDocumentsChange(documents.filter((d) => d.id !== id));
    } catch (e) {
      console.error('Delete failed:', e);
    }
  };

  return (
    <aside className="w-80 h-full flex flex-col bg-slate-950 border-r border-slate-800/80 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-blue-400" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Knowledge Layer ({documents.length})
          </h2>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-sm transition-all"
        >
          <Plus className="w-3.5 h-3.5" />
          Add Source
        </button>
      </div>

      {/* Quiz Me Bonus Action */}
      {documents.length > 0 && (
        <button
          onClick={onOpenQuiz}
          className="mb-3 w-full py-2 px-3 rounded-xl bg-gradient-to-r from-indigo-600/30 to-blue-600/30 hover:from-indigo-600/50 hover:to-blue-600/50 border border-indigo-500/40 text-indigo-200 text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          Generate "Quiz Me" Mode
        </button>
      )}

      {/* Sources List */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {documents.length === 0 ? (
          <div className="h-48 flex flex-col items-center justify-center p-4 text-center rounded-xl border border-dashed border-slate-800 text-slate-500">
            <Database className="w-6 h-6 mb-2 text-slate-600" />
            <p className="text-xs font-medium text-slate-400">No sources added yet</p>
            <p className="text-[11px] text-slate-600 mt-1">
              Add a PDF, PPTX, DOCX, YouTube video, or Web URL to start.
            </p>
          </div>
        ) : (
          documents.map((doc) => (
            <SourceCard key={doc.id} document={doc} onDelete={handleDelete} />
          ))
        )}
      </div>

      <AddSourceModal
        sessionId={sessionId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSourceAdded={handleSourceAdded}
      />
    </aside>
  );
};
