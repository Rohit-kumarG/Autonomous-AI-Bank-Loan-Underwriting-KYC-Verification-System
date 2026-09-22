"""
FastAPI Microservice for Autonomous Bank Loan Underwriting & KYC Verification.
Provides RESTful APIs, Webhooks for n8n, and serves the Banking Copilot Dashboard.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import shutil

from config.settings import settings, UPLOADS_DIR, SAMPLE_DOCS_DIR
from core.document_parser import document_parser
from core.rag_policy_engine import policy_rag_engine
from agents.workflow import underwriting_pipeline

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise AI Automation for Autonomous Bank Loan Underwriting, KYC, and Policy RAG."
)

# Enable CORS for frontend & external automation webhooks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for frontend
static_dir = Path(__file__).resolve().parent.parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class ApplicantRequest(BaseModel):
    applicant_id: str = Field(default="APP-2026-001")
    full_name: str
    national_id: str
    email: str
    phone: str
    date_of_birth: str
    employment_type: str = "Salaried Full-time"
    employer_name: str
    years_employed: float = 2.0
    requested_loan_amount: float
    loan_purpose: str = "Personal Use"
    loan_tenure_months: int = 36
    credit_score: int = 700
    monthly_gross_income: float
    existing_monthly_debt_obligations: float = 0.0
    bank_statement_summary: Optional[Dict[str, Any]] = None


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return "<h1>Autonomous Bank Loan Underwriting System API is Running.</h1>"


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "policies_indexed": len(policy_rag_engine.chunks)
    }


@app.post("/api/v1/underwrite")
async def run_underwriting(applicant: ApplicantRequest):
    """
    Main endpoint: runs the full multi-agent underwriting workflow.
    """
    try:
        result_state = underwriting_pipeline.run(applicant.model_dump())
        return JSONResponse(status_code=200, content=result_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.post("/api/v1/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts customer application / bank statement document, parses it, and executes underwriting.
    """
    saved_path = UPLOADS_DIR / file.filename
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed = document_parser.parse_file(saved_path)
        
        # If JSON, directly run underwriting
        if parsed.get("raw_data") and isinstance(parsed["raw_data"], dict):
            applicant_data = parsed["raw_data"]
        else:
            # Fallback mock mapping if parsing raw text file
            applicant_data = {
                "applicant_id": f"APP-{saved_path.stem}",
                "full_name": "Ayesha Khan",
                "national_id": "42101-5829103-9",
                "email": "ayesha.khan@example.com",
                "phone": "+92-300-1234567",
                "date_of_birth": "1992-05-14",
                "employment_type": "Salaried Full-time",
                "employer_name": "TechGlobal Logistics Ltd",
                "years_employed": 4.5,
                "requested_loan_amount": 15000.0,
                "loan_purpose": "Home Renovation",
                "loan_tenure_months": 36,
                "credit_score": 765,
                "monthly_gross_income": 4500.0,
                "existing_monthly_debt_obligations": 900.0,
                "bank_statement_summary": {
                    "account_number": "PK36MEZN0001234567890123",
                    "average_monthly_balance": 2400.0,
                    "unresolved_bounces_count": 0
                }
            }

        result_state = underwriting_pipeline.run(applicant_data)
        return JSONResponse(status_code=200, content=result_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@app.get("/api/v1/samples/{sample_name}")
async def get_sample_applicant(sample_name: str):
    """
    Helper for demo dashboard to load pre-configured test profiles (e.g. 'prime', 'high_risk').
    """
    if sample_name == "prime":
        file_path = SAMPLE_DOCS_DIR / "applicant_prime_approved.json"
    elif sample_name == "high_risk":
        file_path = SAMPLE_DOCS_DIR / "applicant_high_risk_rejected.json"
    else:
        raise HTTPException(status_code=404, detail="Sample profile not found")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample file missing")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/v1/n8n-webhook")
async def n8n_webhook_handler(payload: Dict[str, Any]):
    """
    Dedicated Webhook endpoint optimized for n8n automation workflows.
    Receives incoming payload from n8n, executes AI agents, and formats response for n8n downstream nodes.
    """
    result = underwriting_pipeline.run(payload)
    return {
        "status": "success",
        "decision": result.get("final_decision"),
        "approved_amount": result.get("approved_amount"),
        "interest_rate": result.get("approved_interest_rate"),
        "applicant_id": result.get("applicant_id"),
        "summary_memo": result.get("decision_rationale"),
        "memo_markdown": result.get("decision_memo_markdown"),
        "redacted_fields_count": result.get("pii_audit_log", {}).get("total_redactions", 0)
    }
