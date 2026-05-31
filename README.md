# CounselAI - Multi-Agent Admission Counsellor

AI-powered MHT-CET admission counselling system built with:
- **AI Service**: Python FastAPI + Groq LLM + LangGraph multi-agent pipeline
- **Backend**: Java Spring Boot + PostgreSQL (692 colleges, 157k+ cutoff records)
- **Frontend**: React + Vite + TailwindCSS (dark theme chat UI)

## Quick Start

```bash
# 1. Start PostgreSQL (counselai_db)
# 2. Start Java Backend
cd backend && mvn spring-boot:run

# 3. Start AI Service
cd ai-service && uvicorn main:app --port 8001

# 4. Start Frontend
cd frontend && npm run dev
```

## Architecture

```
User → React Chat UI (5173)
         → FastAPI AI Service (8001)
              → Profile Agent (Groq LLM)
              → Eligibility Agent → Spring Boot API (8080) → PostgreSQL
              → Strategy Agent (Groq LLM)
              → Document Agent → Spring Boot API (8080) → PostgreSQL
              → Response Agent (Groq LLM)
         ← Structured response with colleges, strategy, documents
```
