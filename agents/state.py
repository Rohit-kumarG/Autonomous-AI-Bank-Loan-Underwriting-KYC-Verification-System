"""
LangGraph State Schema for the Multi-Agent Underwriting System.
Defines the shared memory state passed between agents in the workflow graph.
"""

from typing import TypedDict, Dict, Any, List, Optional


class UnderwritingState(TypedDict):
    # Initial Ingestion Data
    applicant_id: str
    raw_applicant_data: Dict[str, Any]
    
    # Sanitization & Compliance
    sanitized_data: Dict[str, Any]
    pii_audit_log: Dict[str, Any]

    # Core Financial Health Metrics
    financial_metrics: Dict[str, Any]

    # Agent 1 Output: KYC & Identity Status
    kyc_status: str                   # 'PASSED', 'FLAGGED', 'REJECTED'
    kyc_summary: str
    aml_pep_cleared: bool

    # Agent 2 Output: Policy RAG & Risk Assessment
    retrieved_policy_rules: List[Dict[str, Any]]
    risk_level: str                   # 'LOW', 'MODERATE', 'HIGH'
    risk_findings: List[str]

    # Agent 3 Output: Senior Underwriting Decision
    final_decision: str               # 'APPROVED', 'CONDITIONALLY_APPROVED', 'REJECTED'
    approved_amount: float
    approved_interest_rate: float
    approved_tenure_months: int
    decision_rationale: str
    decision_memo_markdown: str

    # Execution Trace & Audit Trail
    current_step: str
    execution_trace: List[Dict[str, Any]]
