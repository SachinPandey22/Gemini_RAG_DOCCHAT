🚀 Gemini RAG DocChat

A full end-to-end Retrieval-Augmented Generation (RAG) chatbot using FastAPI, Qdrant, Gemini API, and React.

Live now: https://gemini-rag-docchat.vercel.app/

⸻

📌 Overview

Gemini RAG DocChat is a document-aware AI assistant.
Users can upload PDFs or text files, the system extracts & chunks text, stores semantic embeddings in Qdrant, and answers questions grounded in the uploaded content using Google Gemini models.

This project was built end-to-end from scratch to learn how modern RAG systems work under the hood — covering ingestion, chunking, embeddings, vector search, retrieval fusion, and grounded LLM generation.

✨ Live App: (Frontend on Vercel, Backend on Render, Qdrant Cloud)
📦 Frontend: React + Vite
🧠 Backend: FastAPI
📊 Vector DB: Qdrant Cloud
🤖 LLM: Gemini 1.5 Flash + text-embedding-004

⸻

🎯 Features

🔼 Upload & Index
	•	Upload multiple files (.pdf, .txt, .md)
	•	Stored by namespace (per user/session grouping)
	•	Automatic text extraction + cleanup
	•	Document chunking (600 words with 80 overlap)
	•	Embeddings from Gemini text-embedding-004
	•	Stored in Qdrant with metadata: filename, page, namespace

🔎 Hybrid Retrieval
	•	Dense semantic search (vector similarity)
	•	BM25 keyword retrieval
	•	Fused scoring: score = α*dense + (1-α)*bm25
	•	Configurable top_k and alpha

🤖 Grounded Chat
	•	Detects small talk vs document questions
	•	Includes contextual snippets in prompt
	•	Strict grounded prompt: “Use only the provided snippets”
	•	Returns answer + clean citation list

🌐 Deployment
	•	Frontend: Vercel
	•	Backend: Render (FastAPI + Uvicorn)
	•	Vector DB: Qdrant Cloud
	•	Fully CORS-safe and cross-domain JSON API

⸻

🏗️ Architecture

┌───────────────────────────────┐
│        React Frontend         │
│  (Upload UI + Chat Interface) │
└───────────────┬───────────────┘
                │ REST API
┌───────────────▼───────────────┐
│        FastAPI Backend         │
│ /upload  /index  /ask  /search │
│                                │
│ 1. Extract & Chunk             │
│ 2. Generate Embeddings         │
│ 3. Hybrid Retrieval (dense+bm25)│
│ 4. Grounded Gemini Answers     │
└───────────────┬───────────────┘
                │
      ┌─────────▼─────────┐
      │    Qdrant Cloud    │
      │ (Vector + Payload) │
      └────────────────────┘


⸻

🧪 Evaluation

A small evaluation of 20–30 questions showed:

Metric	Result
Answer Accuracy	~80%
Faithfulness	~90%
Citation Quality	~75%
Hybrid Retrieval Benefit	+15% recall
Small Talk Quality	100%


⸻

📂 Project Structure

gemini-rag-docchat/
│
├── backend/
│   ├── app/
│   │   ├── routes/          # upload, index, ask, search
│   │   ├── services/        # ingest, chunking, indexing
│   │   ├── ai/              # embeddings, prompts, generator
│   │   ├── db/              # qdrant client setup
│   │   ├── retriever/       # dense + bm25 fusion
│   │   ├── state/           # short chat memory
│   │   ├── models/          # chunk metadata
│   │   └── main.py          # FastAPI bootstrap
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api.js           # backend calls
│   │   ├── views/           # Upload + Chat pages
│   │   ├── components/      # UI components
│   └── vite config
│
└── README.md


⸻

🛠️ Local Development

1. Clone the repo

git clone https://github.com/<yourname>/gemini-rag-docchat
cd gemini-rag-docchat


⸻

2. Backend setup

cd backend
pip install -r requirements.txt

Create .env inside backend/:

GOOGLE_API_KEY=<your_gemini_key>
QDRANT_URL=https://<cluster>.<region>.cloud.qdrant.io:6333
QDRANT_API_KEY=<your_qdrant_key>
COLLECTION_NAME=docs
EMBED_DIM=768
CORS_ORIGINS=http://localhost:5173

Run:

uvicorn app.main:app --reload


⸻

3. Frontend setup

cd ../frontend
npm install
npm run dev

The app runs on:
	•	Backend → http://127.0.0.1:8000
	•	Frontend → http://127.0.0.1:5173

⸻

☁️ Deployment

▶️ Backend – Render
	•	Connect repo to Render Web Service
	•	Root Directory → backend/
	•	Build: pip install -r requirements.txt
	•	Start: uvicorn app.main:app --host 0.0.0.0 --port 8000
	•	Add environment variables:

GOOGLE_API_KEY
QDRANT_URL
QDRANT_API_KEY
COLLECTION_NAME=docs
EMBED_DIM=768
CORS_ORIGINS=https://<your-vercel-app>.vercel.app



▶️ Vector DB – Qdrant Cloud
	•	Create HTTPS cluster
	•	Add collection docs (size 768, cosine)
	•	Use API key above

▶️ Frontend – Vercel
	•	Root Directory: frontend/
	•	Build Command: npm run build
	•	Output Directory: dist
	•	Update frontend/src/api.js:

export const BASE = "https://<your-backend>.onrender.com";


⸻

🧠 What I Learned (key takeaways)
	•	How chunking affects retrieval quality
	•	Why hybrid semantic + keyword search boosts accuracy
	•	How to structure vector payloads for citations
	•	Practical grounding techniques to eliminate hallucination
	•	Deploying multi-service fullstack apps (Render + Vercel + Qdrant Cloud)

⸻

📝 Future Improvements
	•	Heading-aware chunking
	•	Reranker model for higher precision
	•	Real-time progress for indexing
	•	Unified domain + reverse proxy
	•	Better UI and file history per namespace

⸻

⭐ Acknowledgements
	•	Google Gemini API
	•	Qdrant Vector Database
	•	FastAPI
	•	BM25Okapi (rank-bm25)
	•	React + Vite
