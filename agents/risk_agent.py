"""
Agent 2: Credit Risk & Fraud Anomaly Agent.

Responsibilities:
1. Queries the RAG Policy Knowledge Base for exact credit policy clauses.
2. Cross-checks Debt-to-Income (DTI), credit score, and bank statement cash flow.
3. Determines the quantitative risk rating (LOW, MODERATE, HIGH).
"""

from typing import Dict, Any, List
from agents.state import UnderwritingState
from core.rag_policy_engine import policy_rag_engine
from core.financial_engine import financial_engine


class RiskAgent:
    def process(self, state: UnderwritingState) -> Dict[str, Any]:
        data = state.get("raw_applicant_data", {})
        
        # 1. Calculate quantitative financial metrics
        financial_metrics = financial_engine.analyze_applicant_finances(data)

        # 2. Query RAG Policy Knowledge Base
        query = f"Debt-to-Income DTI guidelines credit score {data.get('credit_score')} bounce rules loan limits"
        retrieved_rules = policy_rag_engine.search_policy(query=query, top_k=3)

        # 3. Assess Risk Factors
        risk_findings = list(financial_metrics.get("risk_flags", []))
        risk_category = financial_metrics.get("risk_category", "MODERATE")

        if not risk_findings:
            risk_findings.append("All financial ratios, credit score, and cash flow metrics are within prime bank parameters.")

        trace_entry = {
            "agent": "Credit Risk & Fraud Agent",
            "risk_rating": risk_category,
            "dti_ratio": f"{financial_metrics.get('dti_percentage')}%",
            "findings_count": len(risk_findings)
        }

        return {
            "financial_metrics": financial_metrics,
            "retrieved_policy_rules": retrieved_rules,
            "risk_level": risk_category,
            "risk_findings": risk_findings,
            "current_step": "RISK_ASSESSMENT_COMPLETED",
            "execution_trace": state.get("execution_trace", []) + [trace_entry]
        }


risk_agent = RiskAgent()
