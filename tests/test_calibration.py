"""Small labelled calibration set: hand-written profiles with the level and top scenario an
analyst would expect. If you change a weight, these show what moved."""
from datetime import date

import pytest

from app.breaches import Breach
from app.scoring import assess

T = date(2026, 10, 1)
B = Breach
CASES = [
    ("clean", [], "LOW", None),
    ("old forum only", [B("F", "2014-01-01", ["Email addresses", "Usernames"])], "LOW", "phishing"),
    ("old password leak (reuse risk persists)", [B("S", "2012-05-01", ["Email addresses", "Passwords"])], "MEDIUM", "credential_stuffing"),
    ("recent password leak", [B("S", "2026-02-01", ["Email addresses", "Passwords"])], "MEDIUM", "credential_stuffing"),
    ("recent phone + dob + address", [B("T", "2026-01-01", ["Phone numbers", "Dates of birth", "Physical addresses"])], "HIGH", "bank_call"),
    ("lender with SSN and bank data", [B("L", "2025-08-01", ["Phone numbers", "Social security numbers", "Bank account numbers"], True)], "HIGH", "bank_call"),
    ("everything, several breaches", [B(f"X{i}", "2026-01-01", ["Passwords", "Phone numbers", "Physical addresses", "Dates of birth", "Social security numbers", "Credit cards"], True) for i in range(3)], "CRITICAL", "bank_call"),
]


@pytest.mark.parametrize("name,breaches,level,top", CASES)
def test_expected_level_and_top_scenario(name, breaches, level, top):
    r = assess(breaches, T)
    assert r["level"] == level, name
    if top:
        assert top in [s["id"] for s in r["scenarios"][:3]], name
