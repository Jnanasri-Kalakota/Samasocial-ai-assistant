'use client';

import React from 'react';
import { ChatMessage } from '@/lib/types';
import { CitationBadge } from './CitationBadge';
import { MarkdownRenderer } from './MarkdownRenderer';
import { Sparkles, User } from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center flex-shrink-0 shadow-md">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
      )}

      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3.5 shadow-sm transition-all ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-slate-900/90 border border-slate-800/90 text-slate-100 rounded-bl-none'
        }`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div>
            <MarkdownRenderer content={message.content} />
            
            {message.isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-blue-400 animate-pulse align-middle" />
            )}

            {/* Citations Footer */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-3.5 pt-3 border-t border-slate-800/80">
                <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Evidence Sources ({message.citations.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {message.citations.map((citation, idx) => (
                    <CitationBadge key={`${citation.source_id}-${idx}`} citation={citation} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-slate-300" />
        </div>
      )}
    </div>
  );
};
