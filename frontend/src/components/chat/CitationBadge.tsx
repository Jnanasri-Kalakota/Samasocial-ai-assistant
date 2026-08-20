'use client';

import React, { useState } from 'react';
import { CitationItem } from '@/lib/types';
import { FileText, Presentation, Youtube, Globe, File, ExternalLink, X } from 'lucide-react';

interface CitationBadgeProps {
  citation: CitationItem;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({ citation }) => {
  const [isOpen, setIsOpen] = useState(false);

  const getIcon = () => {
    switch (citation.source_type) {
      case 'pdf':
        return <FileText className="w-3.5 h-3.5 text-rose-400" />;
      case 'pptx':
        return <Presentation className="w-3.5 h-3.5 text-amber-400" />;
      case 'youtube':
        return <Youtube className="w-3.5 h-3.5 text-red-500" />;
      case 'web':
        return <Globe className="w-3.5 h-3.5 text-emerald-400" />;
      case 'docx':
        return <File className="w-3.5 h-3.5 text-blue-400" />;
      default:
        return <FileText className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800/90 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition-all shadow-sm hover:border-slate-500"
      >
        {getIcon()}
        <span className="truncate max-w-[140px]">{citation.source_name}</span>
        <span className="text-blue-400 font-semibold">{citation.location_label}</span>
      </button>

      {isOpen && (
        <div className="absolute z-50 bottom-full left-0 mb-2 w-80 p-3.5 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl text-left animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-start justify-between gap-2 mb-2 pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              {getIcon()}
              <div>
                <h4 className="text-xs font-semibold text-slate-200 truncate max-w-[190px]">
                  {citation.source_name}
                </h4>
                <p className="text-[11px] text-blue-400 font-medium">
                  {citation.location_label}
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-slate-400 hover:text-white p-0.5 rounded"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <p className="text-xs text-slate-300 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/80 italic line-clamp-4">
            "{citation.snippet}"
          </p>

          {citation.source_url && (
            <a
              href={citation.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2.5 inline-flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 font-medium"
            >
              <span>Open original source</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      )}
    </div>
  );
};
