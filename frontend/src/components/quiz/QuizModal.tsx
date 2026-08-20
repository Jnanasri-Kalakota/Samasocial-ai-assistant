'use client';

import React, { useState, useEffect } from 'react';
import { QuizResponse, QuizQuestion, QuizResult } from '@/lib/types';
import { generateQuiz } from '@/lib/api';
import { Sparkles, X, CheckCircle2, XCircle, Award, Loader2, RotateCcw } from 'lucide-react';
import confetti from 'canvas-confetti';

interface QuizModalProps {
  sessionId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const QuizModal: React.FC<QuizModalProps> = ({ sessionId, isOpen, onClose }) => {
  const [quiz, setQuiz] = useState<QuizResponse | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadQuiz();
    } else {
      setQuiz(null);
      setSelectedAnswers({});
      setIsSubmitted(false);
      setError(null);
    }
  }, [isOpen, sessionId]);

  const loadQuiz = async () => {
    setIsLoading(true);
    setError(null);
    setIsSubmitted(false);
    setSelectedAnswers({});
    try {
      const data = await generateQuiz(sessionId, 4);
      setQuiz(data);
    } catch (e: any) {
      setError(e.message || 'Could not generate quiz from current sources.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (questionId: number, optionId: string) => {
    if (isSubmitted) return;
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: optionId }));
  };

  const handleSubmit = () => {
    setIsSubmitted(true);
    if (!quiz) return;
    
    let score = 0;
    quiz.questions.forEach((q) => {
      if (selectedAnswers[q.id]?.toUpperCase() === q.correct_option_id.toUpperCase()) {
        score += 1;
      }
    });

    const pct = (score / quiz.questions.length) * 100;
    if (pct >= 75) {
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
    }
  };

  if (!isOpen) return null;

  const calculateScore = () => {
    if (!quiz) return { score: 0, total: 0, pct: 0 };
    let score = 0;
    quiz.questions.forEach((q) => {
      if (selectedAnswers[q.id]?.toUpperCase() === q.correct_option_id.toUpperCase()) {
        score += 1;
      }
    });
    return {
      score,
      total: quiz.questions.length,
      pct: Math.round((score / quiz.questions.length) * 100),
    };
  };

  const scoreInfo = isSubmitted ? calculateScore() : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-indigo-600/30 border border-indigo-500/40">
              <Sparkles className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100">Knowledge Mastery Quiz</h3>
              <p className="text-[11px] text-slate-400">Auto-generated from your loaded session documents</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {isLoading && (
            <div className="h-64 flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              <p className="text-xs text-slate-400">Synthesizing questions from your multi-source context...</p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800 text-rose-300 text-xs">
              {error}
            </div>
          )}

          {quiz && !isLoading && (
            <>
              {scoreInfo && (
                <div className="p-4 rounded-xl bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-700/60 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Award className="w-8 h-8 text-amber-400" />
                    <div>
                      <h4 className="text-sm font-bold text-white">
                        Your Score: {scoreInfo.score} / {scoreInfo.total} ({scoreInfo.pct}%)
                      </h4>
                      <p className="text-xs text-blue-200">
                        {scoreInfo.pct >= 75 ? 'Outstanding mastery of the material!' : 'Keep reviewing the source references!'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={loadQuiz}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    New Questions
                  </button>
                </div>
              )}

              <div className="space-y-6">
                {quiz.questions.map((q, qIdx) => (
                  <div key={q.id} className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
                    <p className="text-xs font-bold text-blue-400 mb-1">Question {qIdx + 1}</p>
                    <h4 className="text-sm font-semibold text-slate-100 mb-3">{q.question}</h4>

                    <div className="space-y-2">
                      {q.options.map((opt) => {
                        const isSelected = selectedAnswers[q.id] === opt.id;
                        const isCorrect = q.correct_option_id.toUpperCase() === opt.id.toUpperCase();
                        
                        let optionStyle = 'border-slate-800 hover:border-slate-700 bg-slate-900/60 text-slate-300';
                        if (isSelected && !isSubmitted) {
                          optionStyle = 'border-blue-500 bg-blue-600/20 text-blue-200 font-medium';
                        }
                        if (isSubmitted) {
                          if (isCorrect) {
                            optionStyle = 'border-emerald-600 bg-emerald-950/50 text-emerald-200 font-medium';
                          } else if (isSelected && !isCorrect) {
                            optionStyle = 'border-rose-600 bg-rose-950/50 text-rose-200';
                          }
                        }

                        return (
                          <button
                            key={opt.id}
                            onClick={() => handleSelect(q.id, opt.id)}
                            disabled={isSubmitted}
                            className={`w-full p-3 rounded-xl border text-left text-xs flex items-center justify-between transition-all ${optionStyle}`}
                          >
                            <div className="flex items-center gap-2.5">
                              <span className="w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold bg-slate-800 text-slate-300">
                                {opt.id}
                              </span>
                              <span>{opt.text}</span>
                            </div>

                            {isSubmitted && isCorrect && (
                              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                            )}
                            {isSubmitted && isSelected && !isCorrect && (
                              <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                            )}
                          </button>
                        );
                      })}
                    </div>

                    {isSubmitted && (
                      <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-1 text-xs">
                        <p className="text-slate-300">
                          <span className="font-semibold text-slate-200">Explanation:</span> {q.explanation}
                        </p>
                        <p className="text-[11px] text-blue-400 font-medium">
                          Source Reference: {q.source_reference}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        {quiz && !isLoading && !isSubmitted && (
          <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={Object.keys(selectedAnswers).length === 0}
              className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-xs font-semibold text-white shadow-lg shadow-blue-600/20 transition-all"
            >
              Submit & Check Answers
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
