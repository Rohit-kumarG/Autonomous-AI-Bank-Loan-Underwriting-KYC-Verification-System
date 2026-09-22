"""
Agent 3: Chief Underwriter & Decision Memo Agent.

Responsibilities:
1. Synthesizes KYC compliance, quantitative risk ratios, and RAG policy rules.
2. Makes the final credit decision (APPROVED, CONDITIONALLY_APPROVED, REJECTED).
3. Generates a formal, audit-ready Credit Decision Memo.
"""

from typing import Dict, Any
from datetime import datetime
from agents.state import UnderwritingState


class UnderwriterAgent:
    def process(self, state: UnderwritingState) -> Dict[str, Any]:
        data = state.get("raw_applicant_data", {})
        kyc_status = state.get("kyc_status", "REJECTED")
        aml_cleared = state.get("aml_pep_cleared", False)
        metrics = state.get("financial_metrics", {})
        risk_level = state.get("risk_level", "HIGH")
        risk_findings = state.get("risk_findings", [])
        policy_rules = state.get("retrieved_policy_rules", [])

        requested_amount = float(data.get("requested_loan_amount", 0.0))
        requested_tenure = int(data.get("loan_tenure_months", 36))
        base_rate = float(metrics.get("base_interest_rate_pct", 10.0))
        is_hard_reject = metrics.get("is_hard_reject_recommended", False)

        # Decision Logic
        if not aml_cleared or kyc_status == "REJECTED":
            final_decision = "REJECTED"
            approved_amount = 0.0
            approved_rate = 0.0
            approved_tenure = 0
            rationale = "Application rejected due to failed KYC or AML/Sanctions compliance check."
        elif is_hard_reject or risk_level == "HIGH":
            final_decision = "REJECTED"
            approved_amount = 0.0
            approved_rate = 0.0
            approved_tenure = 0
            rationale = f"Application rejected due to high credit risk profile: {'; '.join(risk_findings[:2])}"
        elif risk_level == "MODERATE" or kyc_status == "FLAGGED":
            final_decision = "CONDITIONALLY_APPROVED"
            # 80% loan amount counter-offer, slightly adjusted rate
            approved_amount = round(requested_amount * 0.85, 2)
            approved_rate = round(base_rate + 1.25, 2)
            approved_tenure = requested_tenure
            rationale = "Conditionally approved with adjusted loan amount and rate buffer to mitigate moderate risk flags."
        else:
            final_decision = "APPROVED"
            approved_amount = requested_amount
            approved_rate = base_rate
            approved_tenure = requested_tenure
            rationale = "Fully approved under Prime Tier guidelines with favorable interest rate."

        # Generate Formal Credit Decision Memo
        policy_citations_text = "\n".join([f"- **Section {p.get('section', 'General')}:** {p.get('content', '')[:120]}..." for p in policy_rules[:2]])
        
        memo = f"""# 🏦 CREDIT UNDERWRITING DECISION MEMO

**Application ID:** {state.get('applicant_id', 'N/A')}  
**Date of Review:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Applicant Name (Masked):** {state.get('sanitized_data', {}).get('full_name', data.get('full_name', 'Applicant'))}  
**Credit Bureau Rating Tier:** {metrics.get('credit_tier', 'N/A')} (Score: {data.get('credit_score', 'N/A')})  

---

### 1. Executive Summary & Final Verdict
- **Decision Status:** `{final_decision}`
- **Approved Principal:** ${approved_amount:,.2f} (Requested: ${requested_amount:,.2f})
- **Approved Interest Rate:** {approved_rate}% p.a.
- **Approved Tenure:** {approved_tenure} Months
- **Estimated Monthly Installment (EMI):** ${metrics.get('projected_monthly_emi', 0.0):,.2f}
- **Underwriting Rationale:** {rationale}

---

### 2. KYC & Compliance Verification
- **Identity & Age Verification:** {kyc_status} ({state.get('kyc_summary', '')})
- **AML / PEP / Watchlist Screening:** {'CLEARED' if aml_cleared else 'FAILED'}
- **Data Privacy Audit:** {state.get('pii_audit_log', {}).get('total_redactions', 0)} PII field(s) redacted for compliance.

---

### 3. Quantitative Risk & Financial Ratios
- **Debt-to-Income (DTI):** {metrics.get('dti_percentage', 'N/A')}% (Policy Threshold: <= 45%)
- **Monthly Gross Income:** ${float(data.get('monthly_gross_income', 0)):,.2f}
- **Total Existing Obligations:** ${float(data.get('existing_monthly_debt_obligations', 0)):,.2f}
- **Net Disposable Cash Flow:** ${metrics.get('net_disposable_income', 0):,.2f}
- **Bank Statement Health:** {metrics.get('bounces_detected', 0)} bounce(s) detected.

---

### 4. Regulatory Policy Citations (RAG Knowledge Engine)
{policy_citations_text}

---
*Signed Electronically by Autonomous AI Credit Committee Engine (v1.0)*
"""

        trace_entry = {
            "agent": "Chief Underwriter Agent",
            "decision": final_decision,
            "approved_amount": approved_amount,
            "interest_rate": f"{approved_rate}%"
        }

        return {
            "final_decision": final_decision,
            "approved_amount": approved_amount,
            "approved_interest_rate": approved_rate,
            "approved_tenure_months": approved_tenure,
            "decision_rationale": rationale,
            "decision_memo_markdown": memo,
            "current_step": "UNDERWRITING_COMPLETED",
            "execution_trace": state.get("execution_trace", []) + [trace_entry]
        }


underwriter_agent = UnderwriterAgent()
