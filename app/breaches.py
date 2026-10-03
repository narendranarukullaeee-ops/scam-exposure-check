import hashlib
from dataclasses import dataclass, field
from urllib.parse import quote

import requests


class ProviderError(Exception):
    pass


@dataclass
class Breach:
    name: str
    date: str  # YYYY-MM-DD
    data_classes: list = field(default_factory=list)
    sensitive: bool = False


class HIBPProvider:
    """Have I Been Pwned v3 breached-account lookup (paid API key required)."""

    def __init__(self, api_key: str):
        self.key = api_key

    def lookup(self, email: str) -> list:
        try:
            r = requests.get(
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote(email, safe='')}",
                params={"truncateResponse": "false"},
                headers={"hibp-api-key": self.key, "user-agent": "exposure-check-demo"}, timeout=10)
        except requests.RequestException as e:
            raise ProviderError("Breach service unreachable") from e
        if r.status_code == 404:
            return []
        if r.status_code != 200:
            raise ProviderError(f"Breach service returned {r.status_code}")
        return [Breach(b.get("Title") or b["Name"], b.get("BreachDate", ""), b.get("DataClasses", []),
                       bool(b.get("IsSensitive"))) for b in r.json()]


_SIM = [
    Breach("ExampleTelecom (simulated)", "2025-03-14", ["Email addresses", "Phone numbers", "Physical addresses", "Dates of birth"]),
    Breach("ExampleShop (simulated)", "2021-11-02", ["Email addresses", "Passwords", "Names"]),
    Breach("ExampleForum (simulated)", "2019-06-20", ["Email addresses", "Usernames", "IP addresses", "Passwords"]),
    Breach("ExampleLender (simulated)", "2024-01-09", ["Email addresses", "Phone numbers", "Social security numbers", "Bank account numbers"], True),
    Breach("ExampleFitness (simulated)", "2020-09-30", ["Email addresses", "Names", "Genders"]),
]


class SimulatedProvider:
    """Deterministic fake data so the demo runs without a paid key. Always labelled as simulated."""

    def lookup(self, email: str) -> list:
        h = hashlib.sha256(email.lower().encode()).digest()
        return [b for i, b in enumerate(_SIM) if h[i] % 2 == 0]


def get_provider(settings):
    return HIBPProvider(settings.hibp_api_key) if settings.hibp_api_key else SimulatedProvider()
