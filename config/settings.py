"""
Configuration and Environment Settings for the Banking Underwriting System.
"""
from pydantic_settings import BaseSettings
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
POLICIES_DIR = DATA_DIR / "policies"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"
UPLOADS_DIR = BASE_DIR / "uploads"

# Ensure directories exist
for directory in [POLICIES_DIR, SAMPLE_DOCS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    APP_NAME: str = "Autonomous Bank Loan Underwriting & KYC System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Risk & Lending Default Thresholds (Bank Policy Defaults)
    MAX_ALLOWED_DTI: float = 0.45          # Maximum Debt-to-Income ratio allowed (45%)
    MIN_MONTHLY_INCOME: float = 2500.0     # Minimum income in USD / Standard Currency
    MIN_CREDIT_SCORE: int = 650            # Minimum credit score for auto-approval
    MAX_UNRESOLVED_BOUNCES: int = 1        # Max allowed check/debit bounces in last 6 months
    MIN_AVG_BALANCE_RATIO: float = 0.20    # Average balance must be >= 20% of monthly income

    # Simulated / Configurable LLM Provider
    LLM_PROVIDER: str = "mock"             # 'mock', 'openai', 'gemini', 'ollama'
    API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
