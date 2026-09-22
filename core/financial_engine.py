"""
Financial Analytics & Quantitative Risk Calculation Engine for Banking Underwriting.
Calculates key financial health metrics:
- Debt-to-Income (DTI) Ratio (Pre & Post Loan)
- Estimated Monthly Installment (EMI)
- Net Disposable Cash Flow
- Risk Score & Anomaly Flags
"""

import math
from typing import Dict, Any, List
from config.settings import settings


class FinancialEngine:
    @staticmethod
    def calculate_emi(principal: float, annual_interest_rate_pct: float, tenure_months: int) -> float:
        """
        Standard Financial Banking Formula for Equated Monthly Installment (EMI):
        EMI = [P x r x (1+r)^n] / [(1+r)^n - 1]
        where r = monthly interest rate, n = tenure in months.
        """
        if principal <= 0 or tenure_months <= 0:
            return 0.0

        monthly_rate = (annual_interest_rate_pct / 100.0) / 12.0
        if monthly_rate == 0:
            return round(principal / tenure_months, 2)

        numerator = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
        denominator = math.pow(1 + monthly_rate, tenure_months) - 1
        emi = numerator / denominator
        return round(emi, 2)

    @staticmethod
    def evaluate_credit_tier(credit_score: int) -> Dict[str, Any]:
        """
        Determines the credit rating tier and corresponding base interest rate.
        """
        if credit_score >= 750:
            return {"tier": "Prime (Tier 1)", "base_rate": 7.5, "status": "EXCELLENT", "risk_level": "LOW"}
        elif credit_score >= 650:
            return {"tier": "Near-Prime (Tier 2)", "base_rate": 10.0, "status": "GOOD", "risk_level": "MODERATE"}
        else:
            return {"tier": "Subprime (Tier 3)", "base_rate": 14.5, "status": "POOR", "risk_level": "HIGH"}

    def analyze_applicant_finances(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive financial ratio calculation and anomaly detection.
        """
        gross_income = float(data.get("monthly_gross_income", 0.0))
        existing_debt = float(data.get("existing_monthly_debt_obligations", 0.0))
        requested_amount = float(data.get("requested_loan_amount", 0.0))
        tenure_months = int(data.get("loan_tenure_months", 36))
        credit_score = int(data.get("credit_score", 600))
        
        stmt_summary = data.get("bank_statement_summary", {})
        avg_balance = float(stmt_summary.get("average_monthly_balance", 0.0))
        bounces_count = int(stmt_summary.get("unresolved_bounces_count", 0))

        # 1. Credit Tier & Interest Rate
        tier_info = self.evaluate_credit_tier(credit_score)
        interest_rate = tier_info["base_rate"]

        # 2. Loan EMI Calculation
        projected_emi = self.calculate_emi(requested_amount, interest_rate, tenure_months)

        # 3. DTI Ratios
        total_monthly_obligations = existing_debt + projected_emi
        dti_ratio = (total_monthly_obligations / gross_income) if gross_income > 0 else 1.0
        dti_percentage = round(dti_ratio * 100, 2)

        # 4. Disposable Income Buffer
        # Assuming 35% estimated living expense benchmark
        estimated_living_expenses = gross_income * 0.35
        disposable_income = gross_income - (total_monthly_obligations + estimated_living_expenses)

        # 5. Risk Anomaly Flags
        risk_flags: List[str] = []
        is_hard_reject = False

        if dti_ratio > settings.MAX_ALLOWED_DTI:
            risk_flags.append(f"High DTI Ratio: {dti_percentage}% exceeds bank policy cap ({int(settings.MAX_ALLOWED_DTI*100)}%)")
            if dti_ratio > 0.50:
                is_hard_reject = True

        if bounces_count > settings.MAX_UNRESOLVED_BOUNCES:
            risk_flags.append(f"Negative History: {bounces_count} check/debit bounce(s) detected in recent 6 months")
            is_hard_reject = True

        if credit_score < settings.MIN_CREDIT_SCORE:
            risk_flags.append(f"Subprime Credit Score: {credit_score} is below minimum approval threshold ({settings.MIN_CREDIT_SCORE})")
            is_hard_reject = True

        if avg_balance < (gross_income * settings.MIN_AVG_BALANCE_RATIO):
            risk_flags.append(f"Low Liquidity Buffer: Average balance (${avg_balance}) is less than 20% of monthly income")

        # Loan to Income Multiplier Check
        income_multiplier = (requested_amount / gross_income) if gross_income > 0 else 999.0
        if income_multiplier > 5.0:
            risk_flags.append(f"High Leverage: Requested loan is {round(income_multiplier, 1)}x monthly income (Policy max: 5x)")

        return {
            "credit_tier": tier_info["tier"],
            "base_interest_rate_pct": interest_rate,
            "projected_monthly_emi": projected_emi,
            "total_monthly_debt": total_monthly_obligations,
            "dti_ratio": round(dti_ratio, 4),
            "dti_percentage": dti_percentage,
            "net_disposable_income": round(disposable_income, 2),
            "average_monthly_balance": avg_balance,
            "bounces_detected": bounces_count,
            "risk_flags": risk_flags,
            "is_hard_reject_recommended": is_hard_reject,
            "risk_category": "HIGH" if is_hard_reject or len(risk_flags) >= 2 else ("MODERATE" if len(risk_flags) == 1 else "LOW")
        }


financial_engine = FinancialEngine()
