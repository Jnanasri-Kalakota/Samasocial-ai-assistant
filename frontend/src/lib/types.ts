export type SourceType = 'pdf' | 'pptx' | 'docx' | 'web' | 'youtube';

export interface SourceLocationMeta {
  page_number?: number;
  total_pages?: number;
  slide_number?: number;
  slide_title?: string;
  heading?: string;
  paragraph_idx?: number;
  start_time_seconds?: number;
  formatted_time?: string;
  url?: string;
  section_heading?: string;
  title?: string;
  domain?: string;
}

export interface CitationItem {
  source_id: string;
  source_name: string;
  source_type: SourceType;
  source_url?: string;
  location_label: string;
  location_meta: SourceLocationMeta;
  snippet: string;
}

export interface DocumentItem {
  id: string;
  session_id: string;
  source_type: SourceType;
  source_name: string;
  source_url?: string;
  summary?: string;
  chunk_count: number;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: CitationItem[];
  created_at?: string;
  isStreaming?: boolean;
}

export interface SessionItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  document_count: number;
}

export interface QuizOption {
  id: string;
  text: string;
}

export interface QuizQuestion {
  id: number;
  question: string;
  options: QuizOption[];
  correct_option_id: string;
  explanation: string;
  source_reference: string;
}

export interface QuizResponse {
  session_id: string;
  topic: string;
  questions: QuizQuestion[];
}

export interface QuizQuestionEvaluation {
  question_id: number;
  is_correct: boolean;
  selected_option_id: string;
  correct_option_id: string;
  explanation: string;
}

export interface QuizResult {
  score: number;
  total: number;
  percentage: number;
  evaluations: QuizQuestionEvaluation[];
}
