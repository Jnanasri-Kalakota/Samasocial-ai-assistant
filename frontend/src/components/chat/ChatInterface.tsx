'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, CitationItem } from '@/lib/types';
import { MessageBubble } from './MessageBubble';
import { Send, Sparkles, Layers, Bot } from 'lucide-react';

interface ChatInterfaceProps {
  sessionId: string;
  messages: ChatMessage[];
  documentCount: number;
  onSendMessage: (text: string, simpleTerms: boolean) => Promise<void>;
  isStreaming: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionId,
  messages,
  documentCount,
  onSendMessage,
  isStreaming,
}) => {
  const [inputPrompt, setInputPrompt] = useState('');
  const [simpleTerms, setSimpleTerms] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isStreaming) return;
    const text = inputPrompt;
    setInputPrompt('');
    await onSendMessage(text, simpleTerms);
  };

  return (
    <main className="flex-1 flex flex-col h-full bg-slate-950 overflow-hidden">
      {/* Messages Timeline */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 max-w-lg mx-auto">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center mb-4 shadow-lg shadow-blue-600/30">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-base font-bold text-slate-100 mb-1.5">
              Evidence-First Learning Assistant
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Ask questions, explore concepts, or resolve doubts. Every answer is strictly grounded in your uploaded documents and videos with precise citations.
            </p>
            {documentCount === 0 ? (
              <div className="p-3 rounded-xl bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs">
                💡 Upload a PDF, PPTX, DOCX, or YouTube link on the left sidebar to begin grounded learning!
              </div>
            ) : (
              <div className="flex flex-wrap gap-2 justify-center">
                {['Summarize the key takeaways', 'Explain this in simple terms', 'What are the main concepts covered?'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => {
                      setInputPrompt(suggestion);
                    }}
                    className="px-3 py-1.5 rounded-full text-xs bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box Controls */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto space-y-2.5">
          {/* Controls toolbar */}
          <div className="flex items-center justify-between text-xs px-1">
            <button
              onClick={() => setSimpleTerms(!simpleTerms)}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border transition-all ${
                simpleTerms
                  ? 'bg-blue-600/20 border-blue-500/50 text-blue-300 font-semibold'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              <span>Explain in simple terms</span>
              {simpleTerms ? (
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
              ) : null}
            </button>

            <span className="text-[11px] text-slate-500 flex items-center gap-1">
              <Layers className="w-3 h-3" />
              {documentCount} source{documentCount !== 1 ? 's' : ''} in context
            </span>
          </div>

          {/* Form Input */}
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              type="text"
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              placeholder={
                documentCount > 0
                  ? "Ask anything grounded in your loaded sources..."
                  : "Upload a document/video first, or ask a question..."
              }
              className="w-full pl-4 pr-12 py-3 rounded-xl bg-slate-900 border border-slate-800 focus:border-blue-500 text-xs text-slate-100 outline-none shadow-inner placeholder:text-slate-500"
            />
            <button
              type="submit"
              disabled={!inputPrompt.trim() || isStreaming}
              className="absolute right-2 p-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white transition-all shadow-md"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      </div>
    </main>
  );
};
