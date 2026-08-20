'use client';

import React from 'react';
import { DocumentItem } from '@/lib/types';
import { FileText, Presentation, Youtube, Globe, File, Trash2, Layers } from 'lucide-react';

interface SourceCardProps {
  document: DocumentItem;
  onDelete: (id: string) => void;
}

export const SourceCard: React.FC<SourceCardProps> = ({ document, onDelete }) => {
  const getIcon = () => {
    switch (document.source_type) {
      case 'pdf':
        return <FileText className="w-4 h-4 text-rose-400" />;
      case 'pptx':
        return <Presentation className="w-4 h-4 text-amber-400" />;
      case 'youtube':
        return <Youtube className="w-4 h-4 text-red-500" />;
      case 'web':
        return <Globe className="w-4 h-4 text-emerald-400" />;
      case 'docx':
        return <File className="w-4 h-4 text-blue-400" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="group relative p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-all shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="p-1.5 rounded-lg bg-slate-800/80 flex-shrink-0">
            {getIcon()}
          </div>
          <div className="overflow-hidden">
            <h4 className="text-xs font-semibold text-slate-200 truncate" title={document.source_name}>
              {document.source_name}
            </h4>
            <div className="flex items-center gap-2 mt-0.5 text-[11px] text-slate-400">
              <span className="uppercase font-medium text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                {document.source_type}
              </span>
              <span className="flex items-center gap-1">
                <Layers className="w-3 h-3 text-slate-500" />
                {document.chunk_count} chunks
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={() => onDelete(document.id)}
          className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-1 rounded transition-opacity"
          title="Remove source"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {document.summary && (
        <div className="mt-2.5 pt-2 border-t border-slate-800/60">
          <p className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed">
            {document.summary}
          </p>
        </div>
      )}
    </div>
  );
};
