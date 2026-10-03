from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field

from app import mailer
from app.breaches import ProviderError, get_provider
from app.config import Settings
from app.limits import DailyCap, SlidingWindow
from app.otp import OTPStore
from app.scoring import assess
from app.summary import write_summary

STATIC = Path(__file__).resolve().parent.parent / "static"


class OTPRequest(BaseModel):
    email: EmailStr


class CheckRequest(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


def client_ip(request: Request) -> str:
    # Behind a proxy (Render) the first X-Forwarded-For entry is the client.
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() or (request.client.host if request.client else "unknown")


def create_app(settings=None) -> FastAPI:
    s = settings or Settings()
    app = FastAPI(title="Exposure Check", version="1.0.0")
    otp, provider = OTPStore(s), get_provider(s)
    ip_send, ip_check = SlidingWindow(s.ip_hourly_limit, 3600), SlidingWindow(30, 3600)
    email_send = SlidingWindow(s.email_hourly_limit, 3600)
    otp_cap, gemini_cap = DailyCap(s.daily_otp_cap), DailyCap(s.daily_gemini_cap)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/v1/config")
    def config():
        return {"data_source": s.data_source}

    @app.post("/v1/otp/request")
    def request_code(body: OTPRequest, request: Request):
        email = body.email.lower()
        if not ip_send.allow(client_ip(request)) or not email_send.allow(otp._key(email)):
            raise HTTPException(429, "Too many requests. Please try again later.")
        if not otp_cap.take():
            raise HTTPException(503, "The demo has reached its daily limit. Please try again tomorrow.")
        code = otp.issue(email)
        if code is None:
            raise HTTPException(429, "A code was just sent. Wait a minute before requesting another.")
        try:
            mailer.send_otp(s, email, code)
        except mailer.MailError:
            raise HTTPException(502, "Couldn't send the email. Please try again later.")
        return {"sent": True, "expires_in_minutes": s.otp_ttl_seconds // 60}

    @app.post("/v1/check")
    def check(body: CheckRequest, request: Request):
        if not ip_check.allow(client_ip(request)):
            raise HTTPException(429, "Too many attempts. Please try again later.")
        email = body.email.lower()
        status = otp.verify(email, body.code)
        if status == "invalid":
            raise HTTPException(400, "That code is wrong. Check it and try again.")
        if status == "expired":
            raise HTTPException(400, "That code has expired. Request a new one.")
        if status == "locked":
            raise HTTPException(429, "Too many wrong codes. Request a new code later.")
        try:
            breaches = provider.lookup(email)
        except ProviderError:
            raise HTTPException(502, "The breach service is unavailable. Request a new code and try again.")
        result = assess(breaches)
        result["summary"], result["summary_source"] = write_summary(s, gemini_cap, result)
        result["data_source"] = s.data_source
        result["attribution"] = "Breach data: Have I Been Pwned (haveibeenpwned.com)." if s.data_source == "hibp" else "Simulated data for demonstration."
        return result  # nothing is stored; the email is not echoed back

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    return app


app = create_app()
