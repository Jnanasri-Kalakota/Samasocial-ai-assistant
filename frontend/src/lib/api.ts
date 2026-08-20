import { DocumentItem, SessionItem, ChatMessage, QuizResponse, QuizResult } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function createSession(title: string = 'New Learning Session'): Promise<SessionItem> {
  const res = await fetch(`${API_BASE}/sessions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
}

export async function listSessions(): Promise<SessionItem[]> {
  const res = await fetch(`${API_BASE}/sessions/`);
  if (!res.ok) throw new Error('Failed to list sessions');
  return res.json();
}

export async function getSessionDetail(sessionId: string): Promise<{
  id: string;
  title: string;
  documents: DocumentItem[];
  messages: ChatMessage[];
}> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) throw new Error('Failed to get session');
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' });
}

export async function uploadDocument(sessionId: string, file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function ingestUrl(sessionId: string, url: string): Promise<DocumentItem> {
  const res = await fetch(`${API_BASE}/documents/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Ingestion failed' }));
    throw new Error(err.detail || 'URL Ingestion failed');
  }
  return res.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  await fetch(`${API_BASE}/documents/${documentId}`, { method: 'DELETE' });
}

export async function generateQuiz(sessionId: string, numQuestions: number = 4): Promise<QuizResponse> {
  const res = await fetch(`${API_BASE}/quiz/generate?session_id=${sessionId}&num_questions=${numQuestions}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Quiz generation failed' }));
    throw new Error(err.detail || 'Quiz generation failed');
  }
  return res.json();
}
