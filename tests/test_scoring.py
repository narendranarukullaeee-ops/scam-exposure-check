from datetime import date

from app.breaches import Breach
from app.scoring import assess, level_for

TODAY = date(2026, 10, 1)


def test_no_breaches_is_low_and_has_no_scenarios():
    r = assess([], TODAY)
    assert (r["score"], r["level"], r["scenarios"]) == (0, "LOW", [])


def test_email_addresses_alone_do_not_count_as_physical_address():
    r = assess([Breach("X", "2015-01-01", ["Email addresses", "IP addresses"])], TODAY)
    assert r["exposures"] == []


def test_dates_of_birth_are_recognised():
    r = assess([Breach("X", "2020-01-01", ["Dates of birth"])], TODAY)
    assert [e["data_type"] for e in r["exposures"]] == ["Dates of birth"]


def test_password_and_phone_raise_account_takeover_and_vishing():
    b = Breach("Shop", "2025-06-01", ["Email addresses", "Passwords", "Phone numbers"])
    r = assess([b], TODAY)
    ids = {s["id"] for s in r["scenarios"]}
    assert {"credential_stuffing", "bank_call", "phishing"} <= ids
    assert r["phone_exposed"] and r["score"] >= 40


def test_score_is_explainable_and_capped():
    b = [Breach(f"B{i}", "2026-01-01", ["Passwords", "Phone numbers", "Physical addresses", "Dates of birth",
                                        "Social security numbers", "Credit cards", "Security questions and answers"], True)
         for i in range(6)]
    r = assess(b, TODAY)
    assert r["score"] == 100 and r["level"] == "CRITICAL"
    assert sum(f["points"] for f in r["factors"]) >= r["score"]


def test_older_breach_scores_lower_than_recent_one():
    old = assess([Breach("A", "2012-01-01", ["Passwords"])], TODAY)["score"]
    new = assess([Breach("A", "2026-03-01", ["Passwords"])], TODAY)["score"]
    assert new > old


def test_level_boundaries():
    assert [level_for(x) for x in (0, 24, 25, 49, 50, 74, 75, 100)] == \
        ["LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH", "HIGH", "CRITICAL", "CRITICAL"]
