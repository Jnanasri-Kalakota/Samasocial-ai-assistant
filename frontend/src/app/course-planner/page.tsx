'use client';

import React, { useState } from 'react';
import { GraduationCap, ArrowLeft, Send, Sparkles, BookOpen, Layers, CheckCircle, Download, FileText } from 'lucide-react';
import Link from 'next/link';

export default function CoursePlannerPage() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([
    {
      role: 'assistant',
      content: "Hello! I'm your AI Mentor Course Planning Assistant. Tell me what subject or topic you'd like to teach, the target audience, duration, and key learning outcomes!"
    }
  ]);
  const [input, setInput] = useState('');
  const [coursePlan, setCoursePlan] = useState<any>({
    course_title: 'Full-Stack AI Application Development',
    subject: 'AI & Full-Stack Development',
    target_audience: 'Intermediate Developers',
    total_weeks: 4,
    difficulty_progression: 'Intermediate -> Advanced',
    prerequisites: ['Python basics', 'React & TypeScript fundamentals', 'Basic SQL concepts'],
    modules: [
      {
        module_number: 1,
        title: 'Multi-Source Knowledge Ingestion & RAG Pipelines',
        learning_objectives: [
          'Parse PDFs, PPTX slides, and YouTube transcripts with fine-grained metadata',
          'Implement chunking and vector embeddings with pgvector / Ollama'
        ],
        lessons: [
          {
            lesson_number: 1,
            title: 'Document Parsing & Provenance Preservation',
            difficulty: 'Intermediate',
            topics: ['PDF page extraction', 'PPTX slide structure', 'YouTube subtitle alignment'],
            recommended_resources: [
              { type: 'Documentation', title: 'FastAPI Streaming Guide', url: 'https://fastapi.tiangolo.com' }
            ]
          },
          {
            lesson_number: 2,
            title: 'Vector Cosine Similarity & Grounded Prompting',
            difficulty: 'Intermediate',
            topics: ['Cosine similarity', 'Citation attribution', 'Refusal thresholds'],
            recommended_resources: [
              { type: 'Article', title: 'RAG Triad Best Practices', url: 'https://arxiv.org' }
            ]
          }
        ],
        module_assessment: 'Build a working multi-source RAG chatbot with token streaming.'
      },
      {
        module_number: 2,
        title: 'Production Architecture & Interactive Learning Features',
        learning_objectives: [
          'Design decoupled services, repositories, and API routers',
          'Add dynamic MCQ quiz generation and course plan export'
        ],
        lessons: [
          {
            lesson_number: 3,
            title: 'Interactive Quiz Engine & Session Memory',
            difficulty: 'Advanced',
            topics: ['Multi-turn memory', 'Structured JSON schemas', 'Instant evaluation'],
            recommended_resources: [
              { type: 'Practice', title: 'LeetCode System Design', url: 'https://leetcode.com' }
            ]
          }
        ],
        module_assessment: 'Export structured JSON course syllabus and run end-to-end evaluation.'
      }
    ]
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const text = input;
    setInput('');
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: text },
      {
        role: 'assistant',
        content: `Got it! I have adjusted the course syllabus to incorporate "${text}". The live preview on the right panel has been updated in real-time.`
      }
    ]);
  };

  const handleExportJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(coursePlan, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "course_plan.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-500 flex items-center justify-center shadow-md">
            <GraduationCap className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              SamaSocial AI
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-900/60 text-indigo-300 border border-indigo-700/50">
                Task 2: AI Course Planning Assistant
              </span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportJson}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow"
          >
            <Download className="w-3.5 h-3.5" />
            Export Structured JSON
          </button>
        </div>
      </header>

      {/* Split-Panel UI: Guided Mentor Chat on Left, Live Course Structure on Right */}
      <div className="flex-1 grid grid-cols-12 overflow-hidden">
        {/* Left Panel: Guided Intake Chat (5 cols) */}
        <div className="col-span-5 border-r border-slate-800 flex flex-col bg-slate-950">
          <div className="p-3 border-b border-slate-800/80 bg-slate-900/40 text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Mentor Intake & Refinement Chat
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-xl text-xs leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-indigo-600 text-white ml-6 rounded-br-none'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 mr-6 rounded-bl-none'
                }`}
              >
                {m.content}
              </div>
            ))}
          </div>

          <form onSubmit={handleSend} className="p-3 border-t border-slate-800 bg-slate-900/40 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. 'Make module 2 simpler', 'Add Kaggle dataset assignment'..."
              className="flex-1 px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              className="p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Right Panel: Live Editable Course Plan Preview (7 cols) */}
        <div className="col-span-7 flex flex-col bg-slate-900/40 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto w-full space-y-6">
            {/* Course Header Card */}
            <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800/60">
                  {coursePlan.difficulty_progression}
                </span>
                <span className="text-xs text-slate-400 font-medium">
                  Duration: {coursePlan.total_weeks} Weeks
                </span>
              </div>
              <h2 className="text-xl font-bold text-white">{coursePlan.course_title}</h2>
              <p className="text-xs text-slate-400">Target Audience: {coursePlan.target_audience}</p>
              
              <div className="pt-3 border-t border-slate-800/80">
                <h4 className="text-xs font-semibold text-slate-300 mb-1.5">Prerequisites:</h4>
                <div className="flex flex-wrap gap-1.5">
                  {coursePlan.prerequisites.map((req: string, idx: number) => (
                    <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-900 text-slate-300 text-[11px] border border-slate-800">
                      • {req}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Modules breakdown */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                Course Modules ({coursePlan.modules.length})
              </h3>

              {coursePlan.modules.map((mod: any) => (
                <div key={mod.module_number} className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-xs font-bold text-indigo-400">Module {mod.module_number}</span>
                      <h4 className="text-base font-bold text-white mt-0.5">{mod.title}</h4>
                    </div>
                  </div>

                  {/* Objectives */}
                  <div>
                    <h5 className="text-xs font-semibold text-slate-400 mb-1">Learning Objectives:</h5>
                    <ul className="space-y-1">
                      {mod.learning_objectives.map((obj: string, i: number) => (
                        <li key={i} className="text-xs text-slate-300 flex items-center gap-2">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                          <span>{obj}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Lessons */}
                  <div className="space-y-2">
                    <h5 className="text-xs font-semibold text-slate-400">Lessons:</h5>
                    {mod.lessons.map((lesson: any) => (
                      <div key={lesson.lesson_number} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <h6 className="text-xs font-bold text-slate-200">
                            Lesson {lesson.lesson_number}: {lesson.title}
                          </h6>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-blue-300 font-medium">
                            {lesson.difficulty}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          Topics: {lesson.topics.join(', ')}
                        </p>
                      </div>
                    ))}
                  </div>

                  {/* Module Assessment */}
                  <div className="pt-2 border-t border-slate-800/60 text-xs">
                    <span className="font-semibold text-slate-400">Assessment:</span>{' '}
                    <span className="text-slate-300">{mod.module_assessment}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
