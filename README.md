# SamaSocial AI — Evidence-First Learning Assistant

> A multi-source AI learning assistant that turns PDFs, PPTX files, DOCX documents, web pages, and YouTube videos into an interactive, evidence-grounded learning workspace.

## Overview

SamaSocial AI is an AI-powered learning assistant designed around one core principle:

**The assistant should not only provide an answer — it should show the evidence behind the answer.**

Users can add learning materials from multiple sources and ask questions grounded in those materials. The system processes the sources, preserves their location metadata, retrieves relevant chunks, and generates responses using a local LLM through Ollama.

The application also includes:

- Evidence-first RAG-based question answering
- Multi-source knowledge ingestion
- PDF, PPTX, DOCX, Web and YouTube support
- Fine-grained source citations
- YouTube timestamp citations
- Real-time token streaming using Server-Sent Events
- Multi-turn session memory
- "Explain in simple terms" mode
- Grounded Quiz Me mode
- AI Course Planning Assistant (Task 2 foundation)
- Structured JSON course-plan export
- Local Ollama inference with no external LLM API required

---

# Features

## 1. Multi-Source Knowledge Layer

Users can add different types of learning resources into the same knowledge workspace.

### Supported sources

| Source | Provenance |
|---|---|
| PDF | Page number |
| PPTX | Slide number and slide title |
| DOCX | Heading and paragraph information |
| Web URL | Page title and URL |
| YouTube | Video timestamp |

Each source is parsed independently and converted into searchable chunks while retaining its original location metadata.

This allows the system to provide more precise evidence instead of returning generic source names.

---

## 2. Evidence-First RAG

The application follows a retrieval-augmented generation workflow:

```text
User Source
    ↓
Source Parser
    ↓
Content Extraction
    ↓
Chunking + Metadata
    ↓
Embedding Generation
    ↓
Vector Storage
    ↓
Similarity Retrieval
    ↓
Relevant Context
    ↓
Grounded Prompt
    ↓
LLM
    ↓
Streaming Response + Citations
```

The retrieval layer searches the indexed knowledge base and provides relevant context to the language model before an answer is generated.

The system therefore separates:

- ingestion
- parsing
- chunking
- embeddings
- retrieval
- generation
- citation construction

rather than putting the complete workflow inside a single API route.

---

# Architecture

The backend follows a layered and modular architecture.

```text
                    ┌──────────────────────┐
                    │      Next.js UI      │
                    │   React + Tailwind   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │  DTO validation only │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Services        │
                    ├──────────────────────┤
                    │ Ingestion            │
                    │ Retrieval            │
                    │ LLM                  │
                    │ Embeddings            │
                    │ Citations            │
                    │ Memory               │
                    │ Quiz                 │
                    │ Course Planner       │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
          Repositories     Ollama        Persistence
                │              │              │
                ▼              ▼              ▼
           Vector Search    LLM + Embed     SQLite /
                                          PostgreSQL
```

## Backend structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py
│   │       ├── documents.py
│   │       ├── sessions.py
│   │       └── quiz.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   │
│   └── services/
│       ├── ingestion/
│       ├── parsers/
│       ├── chunking/
│       ├── embeddings/
│       ├── retrieval/
│       ├── llm/
│       ├── citation/
│       ├── memory/
│       ├── quiz/
│       └── planner/
│
├── tests/
├── requirements.txt
├── supabase_schema.sql
└── .env.example
```

The frontend is implemented using Next.js, React, Tailwind CSS and reusable components for chat, sources, citations and quizzes.

---

# AI / LLM Architecture

The application uses a provider-based design for AI services.

For the submitted local configuration:

### LLM

**Ollama**

Used for local language-model inference.

### Embeddings

**Ollama + `nomic-embed-text`**

Used to generate embeddings for indexed source chunks.

The project also contains provider interfaces and alternative clients for cloud providers, allowing the AI layer to be extended without rewriting the application architecture.

---

# Why Ollama?

This implementation uses Ollama for local inference.

This provides:

- Local execution
- No mandatory external LLM API dependency
- No per-request API cost
- Better control over locally processed learning material
- Easy development and testing without requiring a cloud deployment

Because the application is configured around local Ollama inference for this submission, a public deployed link is not provided.

The application is intended to be demonstrated locally with Ollama running on the development machine.

---

# Using the Application

## Task 1 — Learning Assistant

### Step 1: Add learning sources

Use **Add Source** to add:

- PDF
- PPTX
- DOCX
- YouTube URL
- Web URL

### Step 2: Wait for indexing

The backend:

```text
Parse
  ↓
Chunk
  ↓
Generate Embeddings
  ↓
Store
  ↓
Make Available for Retrieval
```

### Step 3: Ask a question

Ask a question related to the uploaded materials.

The system retrieves relevant chunks and passes them to the LLM as grounded context.

### Step 4: Inspect evidence

Generated responses include evidence/source information.

Examples include:

```text
PDF → Page 4
PPTX → Slide 3
DOCX → Section / Heading
YouTube → 03:22
Web → Source URL
```

---

# YouTube Provenance

YouTube sources receive timestamp-level metadata.

For example:

```text
[YouTube: Video Title, 03:22]
```

This allows users to identify the relevant section of the source video instead of receiving only a generic video citation.

---

# Explain in Simple Terms

The interface includes an **Explain in simple terms** interaction.

This changes the response style so that technical concepts can be explained in a more accessible way while still grounding the response in the retrieved context.

---

# Quiz Me Mode

The application includes a grounded quiz-generation workflow.

The quiz system:

```text
Loaded Sources
      ↓
Relevant Knowledge
      ↓
Question Generation
      ↓
Multiple Choice Questions
      ↓
User Submission
      ↓
Instant Grading
      ↓
Explanation
```

Questions are generated from the loaded learning material rather than being completely independent of the user's knowledge base.

---

# Task 2 — AI Course Planning Assistant

The project also includes the foundation for the second assignment task.

The Course Planning Assistant can generate a structured learning curriculum containing:

- Course level
- Duration
- Target audience
- Prerequisites
- Modules
- Learning objectives
- Lessons

The generated course structure can also be exported as structured JSON.

Example workflow:

```text
User Requirements
       ↓
AI Mentor Conversation
       ↓
Course Structure
       ↓
Modules
       ↓
Learning Objectives
       ↓
Lessons
       ↓
Structured JSON Export
```

---

# Architectural Decisions

## 1. Thin API Routes

FastAPI route handlers are intentionally kept lightweight.

Routes are responsible primarily for:

- request validation
- dependency injection
- invoking services
- response serialization

Business logic is implemented in dedicated service modules.

This makes the application easier to test and maintain.

---

## 2. Provider Abstraction

LLM and embedding providers are separated behind interfaces.

This allows the system to support local inference through Ollama while retaining the ability to integrate alternative providers without redesigning the entire application.

---

## 3. Source-Level Provenance

Every extracted chunk carries source-location metadata.

This was a deliberate design decision because a learning assistant should allow users to understand where an answer originated.

---

## 4. Repository Pattern

Database and vector-store operations are separated from application/business logic through repository classes.

This keeps persistence concerns isolated from the rest of the system.

---

## 5. Streaming Responses

The chat API supports Server-Sent Events (SSE) for real-time token streaming.

Instead of waiting for the entire response to be generated, the frontend can receive the response progressively.

---

## 6. Local-First AI

Ollama is used for the submitted configuration so that inference can run locally.

This reduces external dependencies and makes the application easier to run during evaluation.

---

# Testing

The project includes unit and integration tests covering important parts of the application.

Test coverage includes:

- Chunk metadata preservation
- PDF page extraction
- PPTX slide extraction
- DOCX heading extraction
- YouTube video ID extraction
- YouTube timestamp formatting
- Prompt grounding rules
- Prompt context formatting
- FastAPI lifecycle
- Session and database persistence

The implemented test suite was verified successfully during development.

---

# Key Engineering Highlights

### Multi-source ingestion

```text
PDF ───────┐
PPTX ──────┤
DOCX ──────┤
Web ───────┼──→ Parser → Chunker → Embeddings → Retrieval
YouTube ───┘
```

### Grounded generation

```text
Question
   ↓
Similarity Search
   ↓
Relevant Chunks
   ↓
Grounded Prompt
   ↓
Ollama
   ↓
Streaming Answer
   ↓
Evidence / Citations
```

### Learning workflow

```text
Learn
 ↓
Ask Questions
 ↓
Review Evidence
 ↓
Generate Quiz
 ↓
Evaluate Understanding
```

---

# Technology Stack

## Frontend

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide Icons

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Pytest

## AI / RAG

- Ollama
- llama2
- nomic-embed-text
- Retrieval-Augmented Generation
- Cosine similarity search

## Document Processing

- PDF parsing
- PPTX parsing
- DOCX parsing
- Web content extraction
- YouTube transcript processing

# Author

**Jnanasri Kalakota**

SamaSocial AI — AI Backend Developer Assignment