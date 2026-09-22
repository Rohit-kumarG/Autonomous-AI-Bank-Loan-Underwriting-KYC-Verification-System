"""
Core Banking Compliance Module: PII (Personally Identifiable Information) Sanitizer.

Why this matters in Banking AI:
- Under GDPR, CCPA, and Banking Secrecy Regulations, customer PII (SSN, CNIC, Account Numbers,
  Phone numbers) must NOT be sent to external LLMs in raw form.
- This module redacts sensitive information while preserving financial context.
"""

import re
from typing import Tuple, Dict, Any, List


class PIISanitizer:
    def __init__(self):
        # Patterns for high-risk financial PII
        self.patterns = {
            "CNIC_OR_SSN": r"\b\d{3}-\d{2}-\d{4}\b|\b\d{5}-\d{7}-\d{1}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE": r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4,6}",
            "IBAN_OR_ACCOUNT": r"\b[A-Z]{2}\d{2}[A-Z0-9]{12,30}\b|\b\d{10,16}\b",
            "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        }

    def sanitize_text(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Sanitizes text by replacing sensitive data with semantic token placeholders.
        Returns:
            sanitized_text (str): Safe text for LLM processing.
            audit_log (dict): Metadata of what was redacted for compliance audit.
        """
        sanitized = text
        redaction_counts: Dict[str, int] = {}
        redacted_samples: Dict[str, List[str]] = {}

        for pii_type, pattern in self.patterns.items():
            matches = list(re.finditer(pattern, sanitized, flags=re.IGNORECASE))
            if matches:
                redaction_counts[pii_type] = len(matches)
                redacted_samples[pii_type] = [m.group(0) for m in matches[:3]]
                # Replace with placeholder token e.g., [REDACTED_EMAIL_1]
                counter = 1
                def replacer(match):
                    nonlocal counter
                    token = f"[{pii_type}_{counter}]"
                    counter += 1
                    return token
                sanitized = re.sub(pattern, replacer, sanitized, flags=re.IGNORECASE)

        audit_log = {
            "total_redactions": sum(redaction_counts.values()),
            "details": redaction_counts,
            "status": "COMPLIANT_REDACTED" if redaction_counts else "CLEAN_NO_PII"
        }

        return sanitized, audit_log


# Singleton instance
pii_sanitizer = PIISanitizer()
