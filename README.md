# 🚀 ColdGenius AI - Intelligent Cold Email Automation Platform

**Transform Your Cold Outreach with AI-Powered Personalization & Blockchain Verification**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

---

## 🎯 Overview

**ColdGenius AI** is a next-generation cold email automation platform that combines **artificial intelligence**, **blockchain verification**, and **smart deliverability** to help sales teams achieve unprecedented response rates.

Unlike traditional email tools, ColdGenius AI:
- ✨ **Generates hyper-personalized emails** using multi-LLM intelligence (Gemini, Groq, OpenRouter)
- 🔗 **Verifies email authenticity** with blockchain timestamps (Polygon)
- 🛡️ **Prevents spam flags** with intelligent email validation & anti-spam logic
- 📊 **Tracks real-time analytics** with webhook-based open/reply tracking

---

## 🌟 Key Features

### 🤖 AI-Powered Email Generation
- **Multi-LLM Auto-Swap**: Seamlessly switches between Gemini 3.6 Flash, Groq, and OpenRouter models.
- **Smart Personalization**: Analyzes prospect data for unique, highly relevant messaging.
- **Response Time**: < 3 seconds per email generation.

### 📧 Real Email Delivery & Validation
- **Provider**: Resend API integration for reliable delivery.
- **Anti-Spam Logic**: Random delay (30-120s) between sends to protect domain reputation.
- **Email Validation**: Blocks disposable domains and flags risky free email providers.

### ⛓️ Web3 Blockchain Timestamp
- **Immutable Proof**: Generates Keccak256 hash of email content.
- **Audit Trail**: Stores proof of send time on Polygon blockchain (mock/testnet ready).

### 🔐 Enterprise-Grade Security
- **Authentication**: JWT tokens with secure expiration.
- **Password Hashing**: Bcrypt with salt rounds (NIST compliant).
- **Data Isolation**: Row-level security ensures users only access their own data.
a.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.13), SQLAlchemy, Pydantic
- **Database**: PostgreSQL (Neon.tech Serverless)
- **AI/LLM**: Google Gemini 3.6 Flash, Groq (Llama 3.3), OpenRouter
- **Email**: Resend API
- **Frontend**: Alpine.js, Tailwind CSS
- **DevOps**: Docker, GitHub Actions CI/CD

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL database (local or cloud like Neon.tech)
- API keys for Resend, Gemini/Groq

### 1. Clone & Setup
```bash
git clone https://github.com/whoissaf/coldgenius-ai.git
cd coldgenius-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
2. Configure
Copy .env.example to .env and add your API keys.
3. Run App uvicorn app.main:app --reload --port 8000
API Docs: http://localhost:8000/docs

