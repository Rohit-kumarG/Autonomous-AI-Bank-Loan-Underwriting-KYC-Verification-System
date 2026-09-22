"""
Automated Test Suite for the Autonomous Banking Underwriting System.
"""

import pytest
from core.pii_sanitizer import pii_sanitizer
from core.financial_engine import financial_engine
from core.rag_policy_engine import policy_rag_engine
from agents.workflow import underwriting_pipeline


def test_pii_sanitizer_redacts_sensitive_data():
    sample_text = "Customer Tariq CNIC is 35202-9182374-1 and phone is +92-321-9876543, email tariq@example.com."
    sanitized, audit = pii_sanitizer.sanitize_text(sample_text)

    assert "35202-9182374-1" not in sanitized
    assert "tariq@example.com" not in sanitized
    assert audit["total_redactions"] >= 3
    assert audit["status"] == "COMPLIANT_REDACTED"


def test_financial_engine_emi_and_dti():
    # $10,000 at 10% for 12 months
    emi = financial_engine.calculate_emi(principal=10000.0, annual_interest_rate_pct=10.0, tenure_months=12)
    assert 850.0 < emi < 900.0

    applicant = {
        "monthly_gross_income": 4000.0,
        "existing_monthly_debt_obligations": 500.0,
        "requested_loan_amount": 10000.0,
        "loan_tenure_months": 24,
        "credit_score": 750,
        "bank_statement_summary": {
            "average_monthly_balance": 1500.0,
            "unresolved_bounces_count": 0
        }
    }
    analysis = financial_engine.analyze_applicant_finances(applicant)
    assert analysis["credit_tier"] == "Prime (Tier 1)"
    assert analysis["risk_category"] == "LOW"
    assert analysis["is_hard_reject_recommended"] is False


def test_rag_policy_engine_retrieval():
    results = policy_rag_engine.search_policy("Debt-to-income DTI 45 percent maximum", top_k=2)
    assert len(results) > 0
    assert any("DTI" in r["section"] or "Risk" in r["section"] or "Eligibility" in r["section"] for r in results)


def test_pipeline_prime_approval():
    prime_applicant = {
        "applicant_id": "APP-TEST-001",
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
    result = underwriting_pipeline.run(prime_applicant)
    assert result["final_decision"] == "APPROVED"
    assert result["kyc_status"] == "PASSED"
    assert result["approved_amount"] == 15000.0
    assert "CREDIT UNDERWRITING DECISION MEMO" in result["decision_memo_markdown"]


def test_pipeline_high_risk_rejection():
    high_risk_applicant = {
        "applicant_id": "APP-TEST-002",
        "full_name": "Tariq Mahmood",
        "national_id": "35202-9182374-1",
        "email": "tariq.m99@example.com",
        "phone": "+92-321-9876543",
        "date_of_birth": "1998-11-20",
        "employment_type": "Self-Employed",
        "employer_name": "Freelance",
        "years_employed": 0.5,
        "requested_loan_amount": 25000.0,
        "loan_tenure_months": 24,
        "credit_score": 580,
        "monthly_gross_income": 2000.0,
        "existing_monthly_debt_obligations": 1200.0,
        "bank_statement_summary": {
            "account_number": "PK89HABB0009876543210987",
            "average_monthly_balance": 100.0,
            "unresolved_bounces_count": 3
        }
    }
    result = underwriting_pipeline.run(high_risk_applicant)
    assert result["final_decision"] == "REJECTED"
    assert result["risk_level"] == "HIGH"
    assert result["approved_amount"] == 0.0
