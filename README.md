# 📄 ResumeFit - API

**An AI-powered API that analyzes how well your resume matches a job description — and helps you prepare to close the gap.**

Upload a resume, paste in a job description, and get back a match score, a skills-gap breakdown, concrete improvement suggestions, and likely interview questions tailored to what's missing. Built as a full backend engineering project: real auth, real file handling, real AI integration, real infrastructure.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🔗 Live Demo
[![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)](https://youtu.be/UtttppB8hqA)
*<- short demo.*
- **API base:** `https://resumefit-api.onrender.com`
- **Interactive docs (Swagger UI):** `https://resumefit-api.onrender.com/docs`

> ⚠️ Hosted on Render's free tier — the service spins down after periods of inactivity, so the **first request may take 30–60 seconds** to wake it back up. Subsequent requests are fast.

---

## ✨ Features

- 🔐 **JWT authentication** — secure registration and login, with Argon2 password hashing
- 📤 **Resume upload & parsing** — accepts PDF resumes, validated by extension, MIME type, *and* magic bytes (so a renamed non-PDF can't slip through), then parsed entirely in memory — nothing touches disk
- 🤖 **AI-powered matching** — Google Gemini compares your resume against a job description and returns structured, schema-validated JSON: match score, found/missing skills, suggestions, and likely interview questions
- ⚡ **Redis caching** — identical resume + job description pairs are cached by content hash, so repeat requests return in milliseconds instead of re-calling the AI
- 🚦 **Rate limiting** — a custom Redis-backed limiter (10 requests/hour per user) protects the AI endpoints from abuse and runaway API costs
- ✅ **Automated tests** — Pytest suite covering auth, upload validation, AI matching (mocked), caching behavior, and authorization boundaries
- 🔄 **CI/CD** — every push runs the full test suite against real ephemeral Postgres and Redis containers via GitHub Actions
- 🐳 **Dockerized** — multi-stage Docker build for a lean, reproducible production image
- ☁️ **Deployed on real infrastructure** — Neon (serverless Postgres), Upstash (serverless Redis), and Render (container hosting)

---

## 🏗️ Architecture

```
[ Client / Swagger UI ]
          │
          ▼
[ FastAPI App ] ──── (JWT Auth Middleware & Input Validation)
          │
          ├──► [ PDF Parser ] ── extracts text safely, in memory
          │
          ├──► [ Redis Cache ] ── checks hash of (resume + job description)
          │            │
          │      (cache miss)
          │            ▼
          └──► [ Gemini API ] ── returns structured, schema-validated JSON
                       │
                       ▼
              [ PostgreSQL (Neon) ]
```

---

## 🛠️ Tech Stack

| Layer | Choice |
|---|---|
| **Language / Framework** | Python 3.11, FastAPI |
| **Database** | PostgreSQL (via SQLAlchemy + Alembic migrations) |
| **Cache / Rate Limiting** | Redis |
| **Auth** | JWT (python-jose), Argon2 password hashing (passlib) |
| **PDF Parsing** | pdfplumber |
| **AI** | Google Gemini API (structured JSON output) |
| **Testing** | Pytest, with mocked AI calls and a transactional test database |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker (multi-stage build) |
| **Hosting** | Render (API), Neon (Postgres), Upstash (Redis) |

---

## 📚 API Overview

Full interactive documentation is available at `/docs` (Swagger UI) on any running instance.

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Create a new account | No |
| `POST` | `/api/v1/auth/login` | Log in, receive a JWT access token | No |
| `POST` | `/api/v1/resumes/upload` | Upload a PDF resume for parsing | Yes |
| `POST` | `/api/v1/match-reports` | Generate an AI match report for a resume + job description | Yes |
| `GET` | `/health` | Health check | No |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- Docker Desktop (for local Postgres & Redis)

### Setup

```bash
# Clone the repo
git clone https://github.com/Kevizyke/resumefit-backend.git
cd resumefit-backend 

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Postgres & Redis
docker compose up -d

# Copy env template and fill in your own values
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to try it out.

### Running Tests

```bash
pytest -v
```

### Building the Docker Image

```bash
docker build -t resumefit-api .
docker run -p 8000:8000 --env-file .env resumefit-api
```

---

## 🔒 Security Notes

- Passwords are hashed with **Argon2**, never stored in plaintext.
- Uploaded files are validated by extension, declared MIME type, **and** file magic bytes — a spoofed `.pdf` extension alone won't pass.
- Files are parsed entirely **in memory** and never written to disk.
- Resume ownership is checked on every lookup — one user cannot access or generate reports against another user's resume, even by guessing an ID.
- AI-generated output is validated against a strict Pydantic schema before being trusted or stored, with an automatic retry on malformed responses.

---

## 🙏 Attributions

This project was built with the help of the following tools, libraries, and services:

**Development assistance**
- [Claude](https://claude.com) (Anthropic) — used for Dockerfile, GitHub workflow, and debugging.

**Core frameworks & libraries**
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [passlib](https://passlib.readthedocs.io/) (Argon2 hashing)
- [python-jose](https://github.com/mpdavis/python-jose) (JWT)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [redis-py](https://github.com/redis/redis-py)
- [pytest](https://docs.pytest.org/) & [reportlab](https://www.reportlab.com/) (test fixtures)

**AI & infrastructure**
- [Google Gemini API](https://ai.google.dev/) — resume/job matching intelligence
- [Neon](https://neon.tech/) — serverless PostgreSQL hosting
- [Upstash](https://upstash.com/) — serverless Redis hosting
- [Render](https://render.com/) — application hosting
- [GitHub Actions](https://github.com/features/actions) — CI/CD

---

## 📄 License

This project is licensed under the MIT License — feel free to use it as a reference for your own learning.
