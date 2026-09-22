# 🏦 Autonomous AI Bank Loan Underwriting & KYC Verification System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![n8n-Ready](https://img.shields.io/badge/n8n-Orchestration%20Blueprint-EA4B71.svg)](https://n8n.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade autonomous credit underwriting engine built for banking environments. It automates customer document ingestion, PII sanitization (GDPR/Banking compliance), financial risk analytics (DTI, cash flow, bounce detection), policy retrieval via RAG, multi-agent credit committee decisioning, and webhook-driven orchestration with **n8n**.

---

## 🏛️ System Architecture

```
                                  [ CUSTOMER APPLICATION / WEBHOOK ]
                                                  │
                                                  ▼
                                      [ MODULE 1: PII SANITIZER ]
                                   (Masks CNIC/SSN, Phones, Accounts)
                                                  │
                                                  ▼
                 ┌─────────────────────────────────────────────────────────────────┐
                 │          LANGGRAPH MULTI-AGENT UNDERWRITING ROOM               │
                 │                                                                 │
                 │   [ Agent 1: KYC & Compliance ]                                 │
                 │     • Age, Identity & Employment Verification                   │
                 │     • AML / PEP Sanctions Screening Simulation                  │
                 │                            │                                    │
                 │                            ▼                                    │
                 │   [ Agent 2: Credit Risk & Policy RAG ] <---> [ Bank Policy RAG]│
                 │     • DTI, EMI, Liquidity & Bounce Calculation (Vector DB / TF) │
                 │     • Cross-Checks Lending Caps & Rules                         │
                 │                            │                                    │
                 │                            ▼                                    │
                 │   [ Agent 3: Chief Underwriter ]                                │
                 │     • Synthesizes Risk + KYC + Policy Verdict                   │
                 │     • Generates Audit-Ready Credit Decision Memo                │
                 └─────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                                     [ MODULE 4: FASTAPI & n8n ]
                             • REST API Endpoints & Real-Time Dashboard
                             • n8n Webhook / Slack / Email Automation Flow
```

---

## 🚀 Key Features

1. **Banking-Grade PII Sanitization**:
   - Automatically redacts sensitive identifiers (National ID / SSN, Phone, Email, Bank Account / IBAN) prior to LLM processing.
   - Preserves complete data confidentiality adhering to GDPR and financial secrecy laws.

2. **Multi-Agent Decisioning (LangGraph Architecture)**:
   - **KYC & Compliance Agent**: Validates identity authenticity, age criteria (21-65), and sanctions.
   - **Credit Risk Agent**: Computes Debt-to-Income (DTI), cash flow liquidity buffers, and checks for account bounces.
   - **Chief Underwriter Agent**: Formulates the final verdict (`APPROVED`, `CONDITIONALLY_APPROVED`, `REJECTED`) and generates an official Credit Decision Memo.

3. **Retrieval-Augmented Generation (RAG) Policy Engine**:
   - Ingests bank credit manuals and guidelines.
   - Autonomously quotes relevant policy sections directly in the credit memo.

4. **Low-Code Orchestration (n8n Integration)**:
   - Includes a ready-to-import `n8n/banking_loan_workflow.json` blueprint.
   - Triggers automated Slack alerts to the credit committee and emails decision notices to applicants.

5. **Real-time Glassmorphism Dashboard**:
   - Modern, responsive web interface showing live agent execution states, credit metrics HUD, and instant memo generation.

---

## 📁 Repository Structure

```
.
├── config/
│   └── settings.py               # App configuration & risk thresholds
├── data/
│   ├── sample_docs/              # Sample applicant test profiles (Prime vs High Risk)
│   └── policies/                 # Bank Credit Policy manuals (Markdown)
├── core/
│   ├── pii_sanitizer.py          # Data privacy & masking engine
│   ├── document_parser.py        # PDF and text document parser
│   ├── financial_engine.py       # DTI, EMI, and cash flow calculations
│   └── rag_policy_engine.py      # Policy vector retriever
├── agents/
│   ├── state.py                  # LangGraph State schema
│   ├── kyc_agent.py              # Identity & compliance agent
│   ├── risk_agent.py             # Quantitative risk & anomaly agent
│   ├── underwriter_agent.py      # Final decision & credit memo agent
│   └── workflow.py               # Multi-agent graph pipeline
├── api/
│   └── main.py                   # FastAPI application & n8n webhook routes
├── n8n/
│   └── banking_loan_workflow.json # Importable n8n workflow blueprint
├── static/
│   ├── index.html                # Interactive banking dashboard
│   ├── style.css                 # Dark-mode styling
│   └── app.js                    # Live agent visualization logic
├── tests/
│   └── test_pipeline.py          # Pytest verification suite
├── requirements.txt              # Dependencies
└── run.py                        # Server entrypoint
```

---

## ⚡ Quick Start Guide

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/Rohit-kumarG/Autonomous-AI-Bank-Loan-Underwriting-KYC-Verification-System.git
cd Autonomous-AI-Bank-Loan-Underwriting-KYC-Verification-System

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the Application
```bash
python run.py
```
Open your browser at: **`http://127.0.0.1:8000`**

### 3. Run Automated Tests
```bash
pytest tests/test_pipeline.py -v
```

---

## 🔌 API Endpoints

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Web Copilot Dashboard |
| `GET` | `/api/v1/health` | Health check & indexed policy count |
| `POST` | `/api/v1/underwrite` | Main JSON applicant underwriting endpoint |
| `POST` | `/api/v1/upload-document` | Upload document file (PDF/JSON/TXT) for processing |
| `POST` | `/api/v1/n8n-webhook` | Dedicated webhook endpoint for n8n workflow pipelines |

---

## 💡 Banking Interview Talking Points

- **Explainability**: Banking regulators require strict auditability. The engine logs every agent transition and cites the exact credit policy clauses that justified the verdict.
- **Data Privacy (PII)**: By stripping sensitive identifiers before LLM ingestion, the architecture complies with banking compliance and data residency regulations.
- **Hybrid Automation**: High-volume prime applications are auto-decisioned in milliseconds, while edge-case applications receive conditional terms or get escalated to human officers.
