"""
LangGraph Multi-Agent Orchestration Workflow.
Defines the state graph transitions between KYC Agent, Risk Agent, and Underwriter Agent.
"""

from typing import Dict, Any
from agents.state import UnderwritingState
from agents.kyc_agent import kyc_agent
from agents.risk_agent import risk_agent
from agents.underwriter_agent import underwriter_agent
from core.pii_sanitizer import pii_sanitizer
import json


class UnderwritingPipeline:
    """
    State Graph Pipeline that orchestrates the execution across agents.
    """
    def __init__(self):
        pass

    def run(self, applicant_data: Dict[str, Any]) -> UnderwritingState:
        # Step 0: Initialize State & Sanitize PII
        applicant_id = applicant_data.get("applicant_id", "APP-UNKNOWN")
        raw_json_str = json.dumps(applicant_data)
        sanitized_json_str, pii_audit = pii_sanitizer.sanitize_text(raw_json_str)
        
        try:
            sanitized_data = json.loads(sanitized_json_str)
        except Exception:
            sanitized_data = applicant_data

        initial_state: UnderwritingState = {
            "applicant_id": applicant_id,
            "raw_applicant_data": applicant_data,
            "sanitized_data": sanitized_data,
            "pii_audit_log": pii_audit,
            "financial_metrics": {},
            "kyc_status": "PENDING",
            "kyc_summary": "",
            "aml_pep_cleared": False,
            "retrieved_policy_rules": [],
            "risk_level": "PENDING",
            "risk_findings": [],
            "final_decision": "PENDING",
            "approved_amount": 0.0,
            "approved_interest_rate": 0.0,
            "approved_tenure_months": 0,
            "decision_rationale": "",
            "decision_memo_markdown": "",
            "current_step": "PII_SANITIZED",
            "execution_trace": [
                {
                    "step": "PII & Data Ingestion",
                    "status": "COMPLETED",
                    "redacted_fields": pii_audit.get("total_redactions", 0)
                }
            ]
        }

        # Step 1: Execute KYC Agent Node
        kyc_update = kyc_agent.process(initial_state)
        state = {**initial_state, **kyc_update}

        # Step 2: Execute Risk & Policy RAG Agent Node
        risk_update = risk_agent.process(state)
        state = {**state, **risk_update}

        # Step 3: Execute Senior Underwriter Decision Agent Node
        underwriter_update = underwriter_agent.process(state)
        state = {**state, **underwriter_update}

        return state


underwriting_pipeline = UnderwritingPipeline()
