# 🧠 AI RAG Chatbot Backend

**Enterprise AI • Memory • RAG • JWT Auth • PostgreSQL • ChromaDB**

------------------------------------------------------------------------

# 📌 Project Overview

This project implements a **Production-Ready Enterprise AI RAG Backend**
built using:

-   🔐 JWT Authentication (Role-Based)
-   🧠 Conversational Memory
-   📄 Retrieval-Augmented Generation (RAG) from PDFs
-   🗄️ PostgreSQL Database Persistence
-   📊 Token Usage Analytics
-   🔎 Swagger API Documentation
-   📦 Persistent ChromaDB Vector Store

This is **not a demo chatbot** --- it is a scalable backend architecture
suitable for enterprise AI systems.

------------------------------------------------------------------------

# 🏗️ Architecture

Client → FastAPI → JWT Auth → LangChain (Memory + RAG)\
↓\
PostgreSQL (Users + Chat + Analytics)\
↓\
ChromaDB (Persistent Vector Store)\
↓\
PDF Knowledge Base

------------------------------------------------------------------------

# 🧰 Tech Stack

## Backend

-   FastAPI\
-   LangChain\
-   OpenAI\
-   ChromaDB (Persistent)\
-   PyPDF\
-   PostgreSQL\
-   SQLAlchemy\
-   JWT (python-jose)\
-   Passlib (bcrypt)\
-   Uvicorn

------------------------------------------------------------------------

# 📁 Actual Project Structure
```text
ai_rag_chatbot_backend/
│
├── app.py                  # Main FastAPI application
├── config.py               # Environment & configuration settings
├── database.py             # PostgreSQL connection setup
├── models.py               # SQLAlchemy models (Users, ChatHistory, TokenAnalytics)
├── create_tables.py        # DB table creation script
├── .env                    # Environment variables
├── README.md
│
├── auth/                   # 🔐 Authentication & JWT
│   ├── auth_router.py
│   ├── dependencies.py
│   ├── jwt.py
│   ├── security.py
│
├── analytics/              # 📊 Token & Admin Analytics
│   ├── analytics_router.py
│   ├── analytics_service.py
│
├── memory/                 # 🧠 Conversation Memory
│   ├── memory_manager.py
│
├── rag/                    # 📄 Retrieval-Augmented Generation
│   ├── __init__.pySSSS
│   ├── ingest.py
│   ├── qa_chain.py
│   ├── vectorstore.py
│
├── tools/                  # 🛠 AI Tools (Extensible)
│   ├── calculator.py
│   ├── weather_tool.py
│   ├── web_search.py
│
├── streaming/              # ⚡ Streaming Support
│
├── utils/                  # 🔧 LLM Utilities
│   ├── llm.py
│
├── data/                   # 📚 Source Documents (PDFs)
│   ├── company_docs.pdf
│   ├── SD0109_Chatbots.pdf
│
├── vectorstore/            # 🗂 ChromaDB Persistent Storage
│   └── chroma/
│       └── chroma.sqlite3  # Persistent vector database
│
├── logs/                   # 📝 Application Logs
│   └── app.log
│
├── venv/                   # Python virtual environment
└── __pycache__/
```

------------------------------------------------------------------------

# 🔐 Role-Based Authentication & Authorization

## 👤 User Registration

POST `/auth/register`

``` json
{
  "email": "user@email.com",
  "password": "securepassword",
  "role": "USER"
}
```

## 🔑 User Login

POST `/auth/login`

``` json
{
  "email": "user@email.com",
  "password": "securepassword"
}
```

Response:

``` json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

Send JWT in headers:

    Authorization: Bearer <token>

------------------------------------------------------------------------

# 🤖 Chat Endpoint

POST `/chat`

``` json
{
  "message": "What is RAG?",
  "session_id": "test-1",
  "memory_type": "buffer"
}
```

Response:

``` json
{
  "user": "user@email.com",
  "session_id": "test-1",
  "reply": "RAG stands for Retrieval-Augmented Generation...",
  "tokens": {
    "prompt": 1052,
    "completion": 9,
    "total": 1061,
    "cost": 0.001596
  },
  "sources": []
}
```

------------------------------------------------------------------------

# 📊 Analytics Endpoints

GET `/analytics/summary`\
GET `/analytics/admin` (Admin Only)

------------------------------------------------------------------------

# 🧪 How to Test APIs

1️⃣ Register user via `/auth/register`\
2️⃣ Login via `/auth/login`\
3️⃣ Click **Authorize** in Swagger and paste:

    Bearer your_token_here

4️⃣ Test `/chat` endpoint

------------------------------------------------------------------------

# 🔐 Environment Variables

Create `.env`:

    OPENAI_API_KEY=your_openai_api_key_here
    CHROMA_PERSIST_DIR=vectorstore
    DATABASE_URL=your_postgresql_connection_string
    SECRET_KEY=your_jwt_secret_key

------------------------------------------------------------------------

# ▶️ Backend Setup

``` bash
python -m venv venv

venv\Scripts\activate

pip install fastapi uvicorn pydantic python-dotenv langchain langchain-classic langchain-openai langchain-community chromadb pypdf psycopg2 "python-jose[cryptography]" "passlib[bcrypt]" "pydantic[email]" sqlalchemy loguru bcrypt==4.3.0 python-multipart slowapi

 

Create 'chatbot_db' database in Postgres DB (PGAdmin)

python create_tables.py

python -m rag.ingest

uvicorn app:app --reload
```

Open in Browser:

http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# 🚀 Enterprise Capabilities

-   JWT Authentication\
-   Role-Based Access Control\
-   PostgreSQL Conversation Storage\
-   Persistent Chroma Vector DB\
-   Token-Level Cost Tracking\
-   Admin Analytics\
-   Multi-session Conversations

------------------------------------------------------------------------

# 🎯 Production-Ready AI Backend

This backend demonstrates:

-   Secure API design\
-   Enterprise RBAC\
-   Database persistence\
-   Cost-aware AI usage\
-   Modular RAG pipeline\
-   Scalable architecture

------------------------------------------------------------------------
