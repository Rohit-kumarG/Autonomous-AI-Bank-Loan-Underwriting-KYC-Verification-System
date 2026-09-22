"""
Agent 1: Know Your Customer (KYC) & Regulatory Compliance Agent.

Responsibilities:
1. Validates National Identity / Passport format.
2. Checks age requirement (21 - 65 years).
3. Verifies employment stability.
4. Executes simulated Anti-Money Laundering (AML) / Politically Exposed Person (PEP) screening.
"""

from typing import Dict, Any
from datetime import datetime
from agents.state import UnderwritingState


class KYCAgent:
    def process(self, state: UnderwritingState) -> Dict[str, Any]:
        data = state.get("raw_applicant_data", {})
        full_name = data.get("full_name", "Unknown Applicant")
        dob_str = data.get("date_of_birth", "1990-01-01")
        years_employed = float(data.get("years_employed", 0.0))
        national_id = str(data.get("national_id", ""))

        findings = []
        is_passed = True

        # 1. Age Calculation
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.now() - dob).days // 365
            if age < 21:
                findings.append(f"Underage Applicant: Age is {age} years (Policy minimum: 21).")
                is_passed = False
            elif age > 65:
                findings.append(f"Overage Applicant: Age is {age} years (Policy maximum: 65).")
                is_passed = False
            else:
                findings.append(f"Age Verified: {age} years old (Eligible).")
        except Exception:
            findings.append("Invalid or missing Date of Birth format.")
            is_passed = False

        # 2. National ID validation
        if not national_id or len(national_id) < 5:
            findings.append("National Identity Document missing or invalid.")
            is_passed = False
        else:
            findings.append(f"Identity Document validated: {national_id[:3]}***")

        # 3. Employment stability
        if years_employed < 1.0:
            findings.append(f"Employment tenure warning: {years_employed} years with current employer (Preferred: >= 1.0 year).")
        else:
            findings.append(f"Employment tenure verified: {years_employed} years with {data.get('employer_name', 'Employer')}.")

        # 4. AML / PEP Screening simulation
        # In production, this calls World-Check or OFAC sanction API
        pep_sanctions_hit = False
        if "SANCTION" in full_name.upper():
            pep_sanctions_hit = True
            is_passed = False
            findings.append("CRITICAL: AML/PEP Sanctions match detected on watchlist!")
        else:
            findings.append("AML & Global Sanctions Screening: CLEARED (No adverse records).")

        status = "PASSED" if is_passed else ("FLAGGED" if years_employed < 1.0 else "REJECTED")
        summary = " | ".join(findings)

        trace_entry = {
            "agent": "KYC & Compliance Agent",
            "status": status,
            "summary": summary
        }

        return {
            "kyc_status": status,
            "kyc_summary": summary,
            "aml_pep_cleared": not pep_sanctions_hit,
            "current_step": "KYC_COMPLETED",
            "execution_trace": state.get("execution_trace", []) + [trace_entry]
        }


kyc_agent = KYCAgent()
