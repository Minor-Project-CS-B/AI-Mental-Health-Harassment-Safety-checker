# AIMHHC — AI Mental Health & Harassment Safety Checker

An AI-powered web application that provides mental health support and harassment safety assistance through an intelligent chatbot, structured assessments, and real-time risk classification.

---

## Project Overview

AIMHHC addresses two critical domains often overlooked in traditional support systems:

- **Mental Health** — Depression, anxiety, crisis detection, and emotional support
- **Harassment Safety** — Verbal, physical, online harassment detection and guidance

The system uses a hybrid AI approach combining a large language model (Groq LLaMA 3.3) with a custom rule-based classifier (sentiment analysis + keyword detection + MCQ scoring) to provide empathetic, context-aware support.

---

## Key Features

| Feature | Description |
|---|---|
| AI Chatbot | Real-time empathetic conversations powered by Groq LLaMA 3.3 70B |
| Risk Classifier | Hybrid classifier — sentiment + keyword + MCQ scoring |
| Dual Assessments | Separate tracks for mental health and harassment |
| RAG System | Retrieval-Augmented Generation with curated knowledge base |
| Crisis Detection | Automatic escalation with Indian helpline numbers |
| Hinglish Support | Understands Hindi + English mixed input |
| Evidence Upload | Image/video upload for harassment documentation |
| Dashboard | User history, risk trends, assessment results |

---

## System Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────┐
│           React Frontend (Vite)         │
│   Chat │ Assessment │ Dashboard │ Auth  │
└────────────────┬────────────────────────┘
                 │ REST API
                 ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend (Python)        │
├─────────────┬───────────────────────────┤
│   Routers   │  auth, chat, assessment,  │
│             │  dashboard, response      │
├─────────────┴───────────────────────────┤
│           Engine Layer                  │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │Classifier│ │  RAG     │ │Keywords │ │
│  │(hybrid)  │ │(MiniLM)  │ │Sentiment│ │
│  └──────────┘ └──────────┘ └─────────┘ │
├─────────────────────────────────────────┤
│  Groq LLaMA 3.3 70B  │  MongoDB        │
└─────────────────────────────────────────┘
```

---

## Tech Stack

**Backend**
- Python 3.11+ / FastAPI
- Groq API (LLaMA 3.3 70B Versatile)
- NLTK VADER (sentiment analysis)
- Sentence Transformers — all-MiniLM-L6-v2 (RAG embeddings)
- MongoDB (via Motor async driver)

**Frontend**
- React 18 + Vite
- Tailwind CSS
- React Router v6

---

## Classifier Approach

AIMHHC uses a **hybrid scoring model** instead of a custom-trained ML model. This is intentional — it makes the system transparent, explainable, and maintainable.

### Scoring Formula

```
Final Score = (0.20 × Sentiment Score) + (0.35 × Keyword Score) + (0.45 × MCQ Score)
```

| Component | Weight | Method |
|---|---|---|
| Sentiment | 20% | NLTK VADER compound score |
| Keywords | 35% | Pattern matching (regex, Hinglish) |
| MCQ Answers | 45% | Normalized questionnaire score |

### Risk Levels

| Score Range | Risk Level | Action |
|---|---|---|
| ≥ 0.50 | HIGH | Crisis protocol + helplines |
| 0.20 – 0.49 | MEDIUM | Empathetic support + resources |
| < 0.20 | LOW | General supportive chat |

### Crisis Override

Any message containing crisis keywords (suicidal ideation, self-harm) automatically overrides the score to ≥ 0.85 (HIGH), regardless of other signals.

---

## Classifier Performance

Results from 30-case test suite across both domains:

| Test Category | Cases | Accuracy |
|---|---|---|
| Mental health — chat | 13 | ~85% |
| Harassment — chat | 11 | ~82% |
| Assessment (MCQ) | 6 | ~100% |
| **Overall** | **30** | **~87%** |

*Note: Run `python test_classifier.py` from project root for live results.*

---

## Dataset

`dataset_sample.csv` contains 45 curated examples across both domains:
- 25 mental health samples (crisis, depression, anxiety, neutral)
- 20 harassment samples (verbal, physical, cyber, neutral)
- Includes Hinglish examples for regional relevance
- Labels: `text`, `label`, `track`, `risk_level`, `source`

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)
- Groq API key (free at [groq.com](https://console.groq.com))

### Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd vite-project
npm install
npm run dev
```


## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | Login + JWT token |
| POST | `/chat/message` | Send chat message |
| GET | `/chat/history` | Fetch chat history |
| GET | `/assessment/questions` | Get assessment questions |
| POST | `/assessment/submit` | Submit assessment answers |
| GET | `/dashboard/summary` | User dashboard data |

---

## Indian Support Resources (Built-in)

The system automatically provides these resources in crisis situations:

- **iCall (TISS)** — 9152987821
- **Vandrevala Foundation** — 1860-2662-345
- **NIMHANS** — 080-46110007
- **Emergency** — 112
- **NCW Helpline** — 7827170170
- **Cyber Crime** — cybercrime.gov.in / 1930
- **UGC Anti-Ragging** — 1800-180-5522

---

## Project Structure

```
AIMHHC/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt
│   ├── engine/
│   │   ├── classifier.py       # Hybrid risk classifier
│   │   ├── sentiment.py        # VADER sentiment analysis
│   │   ├── keywords.py         # Keyword pattern matching
│   │   ├── rag.py              # RAG retrieval system
│   │   └── response_generator.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── assessment.py
│   │   └── dashboard.py
│   ├── services/
│   │   ├── chat_service.py     # Groq LLM integration
│   │   └── assessment_service.py
│   ├── models/schemas.py
│   └── utils/questions.py      # Assessment question bank
├── vite-project/               # React frontend
├── dataset_sample.csv          # Sample dataset (45 examples)
├── test_classifier.py          # Test suite (30 test cases)
└── README.md
```

---

## Limitations & Future Scope

- Custom-trained ML model can replace rule-based classifier for higher accuracy
- Multi-language support (regional Indian languages)
- Mobile app version
- Integration with licensed therapist network
- Anonymous peer support community

---

## Team / Author
Sarvesh Parmar (Leader)
Swati Tiwari
Naman Pal
Shivani khati
Palak Sitole
Sarang Jain

Minor Project — Computer Science and Engineering , Samrat Ashok Technological Institute Vidisha  
Academic Year: 2025-2026
