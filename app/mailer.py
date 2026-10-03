import logging

import requests

log = logging.getLogger("mailer")


class MailError(Exception):
    pass


def send_otp(settings, to: str, code: str) -> None:
    subject = "Your Exposure Check code"
    text = f"Your one-time code is {code}. It expires in 10 minutes. If you didn't ask for it, ignore this email."
    p = settings.email_provider
    if p == "console":  # development only: never use in production
        log.warning("DEV OTP for %s: %s", to, code)
        return
    try:
        if p == "brevo":
            r = requests.post("https://api.brevo.com/v3/smtp/email", timeout=10,
                              headers={"api-key": settings.mail_api_key},
                              json={"sender": {"name": settings.mail_from_name, "email": settings.mail_from},
                                    "to": [{"email": to}], "subject": subject, "textContent": text})
        elif p == "resend":
            r = requests.post("https://api.resend.com/emails", timeout=10,
                              headers={"Authorization": f"Bearer {settings.mail_api_key}"},
                              json={"from": f"{settings.mail_from_name} <{settings.mail_from}>",
                                    "to": [to], "subject": subject, "text": text})
        else:
            raise MailError(f"Unknown EMAIL_PROVIDER '{p}'")
        if r.status_code >= 300:
            raise MailError(f"Mail provider returned {r.status_code}")
    except requests.RequestException as e:
        raise MailError("Mail provider unreachable") from e
