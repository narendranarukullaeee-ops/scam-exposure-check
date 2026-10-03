import hashlib
import hmac
import secrets
import time


class OTPStore:
    """One-time codes held in memory only, keyed by an HMAC of the email.
    The email address itself is never stored; codes expire and are single-use."""

    def __init__(self, settings):
        self.s = settings
        self.items = {}

    def _key(self, email: str) -> str:
        return hmac.new(self.s.app_secret.encode(), email.lower().encode(), hashlib.sha256).hexdigest()

    def _hash(self, key: str, code: str) -> str:
        return hmac.new(self.s.app_secret.encode(), f"{key}:{code}".encode(), hashlib.sha256).hexdigest()

    def _purge(self):
        now = time.time()
        for k in [k for k, v in self.items.items() if v["expires"] < now]:
            del self.items[k]

    def issue(self, email: str):
        """Returns a new 6-digit code, or None if still inside the resend cooldown."""
        self._purge()
        key, now = self._key(email), time.time()
        cur = self.items.get(key)
        if cur and now - cur["sent"] < self.s.otp_cooldown_seconds:
            return None
        code = f"{secrets.randbelow(10**6):06d}"
        self.items[key] = {"hash": self._hash(key, code), "expires": now + self.s.otp_ttl_seconds,
                           "sent": now, "attempts": 0}
        return code

    def verify(self, email: str, code: str) -> str:
        """Returns 'ok', 'invalid', 'expired' (also covers never-issued) or 'locked'."""
        self._purge()
        key = self._key(email)
        cur = self.items.get(key)
        if not cur:
            return "expired"
        if cur["attempts"] >= self.s.otp_max_attempts:
            return "locked"
        cur["attempts"] += 1
        if hmac.compare_digest(cur["hash"], self._hash(key, code)):
            del self.items[key]
            return "ok"
        return "locked" if cur["attempts"] >= self.s.otp_max_attempts else "invalid"
