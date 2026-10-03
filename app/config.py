import os
import secrets


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


class Settings:
    """All configuration comes from environment variables. kwargs override (used in tests)."""

    def __init__(self, **overrides):
        self.app_secret = os.getenv("APP_SECRET") or secrets.token_hex(32)
        self.email_provider = os.getenv("EMAIL_PROVIDER", "console")
        self.mail_api_key = os.getenv("MAIL_API_KEY", "")
        self.mail_from = os.getenv("MAIL_FROM", "")
        self.mail_from_name = os.getenv("MAIL_FROM_NAME", "Exposure Check")
        self.hibp_api_key = os.getenv("HIBP_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        self.otp_ttl_seconds = 600
        self.otp_max_attempts = 5
        self.otp_cooldown_seconds = 60
        self.daily_otp_cap = _int("DAILY_OTP_CAP", 200)
        self.daily_gemini_cap = _int("DAILY_GEMINI_CAP", 300)
        self.ip_hourly_limit = _int("IP_HOURLY_LIMIT", 6)
        self.email_hourly_limit = _int("EMAIL_HOURLY_LIMIT", 3)
        for k, v in overrides.items():
            setattr(self, k, v)

    @property
    def data_source(self) -> str:
        return "hibp" if self.hibp_api_key else "simulated"
