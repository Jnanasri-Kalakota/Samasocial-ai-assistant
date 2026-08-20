'use client';

import React, { useState, useEffect } from 'react';
import { SourceManager } from '@/components/sources/SourceManager';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { QuizModal } from '@/components/quiz/QuizModal';
import { DocumentItem, ChatMessage, SessionItem, CitationItem } from '@/lib/types';
import { createSession, listSessions, getSessionDetail } from '@/lib/api';
import { Sparkles, GraduationCap, Plus, BookOpen, Layers, Cpu } from 'lucide-react';
import Link from 'next/link';

export default function LearningAssistantPage() {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isQuizOpen, setIsQuizOpen] = useState(false);

  useEffect(() => {
    initApp();
  }, []);

  const initApp = async () => {
    try {
      const sessionList = await listSessions();
      if (sessionList.length > 0) {
        setSessions(sessionList);
        await selectSession(sessionList[0].id);
      } else {
        const newSess = await createSession('SamaSocial Learning Session');
        setSessions([newSess]);
        await selectSession(newSess.id);
      }
    } catch (err) {
      console.error('Initialization error:', err);
    }
  };

  const selectSession = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    try {
      const detail = await getSessionDetail(sessionId);
      setDocuments(detail.documents || []);
      setMessages(detail.messages || []);
    } catch (e) {
      console.error('Failed to load session details:', e);
    }
  };

  const handleCreateNewSession = async () => {
    try {
      const title = prompt('Enter Session Title:', 'New Learning Session') || 'New Learning Session';
      const newSess = await createSession(title);
      setSessions([newSess, ...sessions]);
      await selectSession(newSess.id);
    } catch (e) {
      console.error('Create session error:', e);
    }
  };

  const handleSendMessage = async (text: string, simpleTerms: boolean) => {
    if (!activeSessionId) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    const assistantMsgId = `assistant-${Date.now()}`;
    const initialAssistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      citations: [],
      isStreaming: true,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg, initialAssistantMsg]);
    setIsStreaming(true);

    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeSessionId,
          message: text,
          simple_terms: simpleTerms,
        }),
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';
      let receivedCitations: CitationItem[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const rawChunk = decoder.decode(value, { stream: true });
        const lines = rawChunk.split('\n');

        let currentEvent = 'token';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.replace('event: ', '').trim();
          } else if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            try {
              const parsed = JSON.parse(dataStr);
              if (currentEvent === 'citations') {
                receivedCitations = parsed;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId ? { ...m, citations: receivedCitations } : m
                  )
                );
              } else if (currentEvent === 'token') {
                accumulatedText += parsed.token || '';
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId
                      ? { ...m, content: accumulatedText, citations: receivedCitations }
                      : m
                  )
                );
              } else if (currentEvent === 'done') {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId
                      ? {
                          ...m,
                          content: parsed.full_text || accumulatedText,
                          citations: parsed.citations || receivedCitations,
                          isStreaming: false,
                        }
                      : m
                  )
                );
              }
            } catch (err) {
              // ignore partial parse errors
            }
          }
        }
      }
    } catch (e: any) {
      console.error('Streaming error:', e);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsgId
            ? { ...m, content: `Error: ${e.message || 'Stream disconnected'}`, isStreaming: false }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-md">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              SamaSocial AI
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-900/60 text-blue-300 border border-blue-700/50">
                Task 1: Learning Assistant
              </span>
            </h1>
          </div>
        </div>

        {/* Center: Session Switcher */}
        <div className="flex items-center gap-2">
          <select
            value={activeSessionId || ''}
            onChange={(e) => selectSession(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 outline-none focus:border-blue-500 font-medium"
          >
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </select>
          <button
            onClick={handleCreateNewSession}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            title="Create New Session"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Right: Task 2 Navigation Toggle */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 text-[11px] font-medium">
            <Cpu className="w-3 h-3 text-emerald-400" />
            <span>Ollama Ready</span>
          </div>

          <Link
            href="/course-planner"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
          >
            <GraduationCap className="w-3.5 h-3.5 text-indigo-400" />
            <span>Switch to Mentor Mode (Task 2)</span>
          </Link>
        </div>
      </header>

      {/* Main App Body: Sidebar + Chat Interface */}
      <div className="flex-1 flex overflow-hidden">
        {activeSessionId && (
          <SourceManager
            sessionId={activeSessionId}
            documents={documents}
            onDocumentsChange={setDocuments}
            onOpenQuiz={() => setIsQuizOpen(true)}
          />
        )}

        {activeSessionId && (
          <ChatInterface
            sessionId={activeSessionId}
            messages={messages}
            documentCount={documents.length}
            onSendMessage={handleSendMessage}
            isStreaming={isStreaming}
          />
        )}
      </div>

      {activeSessionId && (
        <QuizModal
          sessionId={activeSessionId}
          isOpen={isQuizOpen}
          onClose={() => setIsQuizOpen(false)}
        />
      )}
    </div>
  );
}
