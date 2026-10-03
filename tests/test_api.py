import pytest
from fastapi.testclient import TestClient

from app import mailer
from app.config import Settings
from app.main import create_app


@pytest.fixture
def client(monkeypatch):
    sent = {}
    monkeypatch.setattr(mailer, "send_otp", lambda s, to, code: sent.update(to=to, code=code))
    s = Settings(hibp_api_key="", gemini_api_key="", email_provider="console")
    return TestClient(create_app(s)), sent


def test_full_flow_returns_result_without_echoing_email(client):
    c, sent = client
    assert c.post("/v1/otp/request", json={"email": "pat@example.com"}).status_code == 200
    r = c.post("/v1/check", json={"email": "pat@example.com", "code": sent["code"]})
    assert r.status_code == 200
    body = r.json()
    assert body["data_source"] == "simulated" and "score" in body and body["summary"]
    assert body["attribution"] and body["disclaimer"]
    assert "pat@example.com" not in r.text


def test_wrong_code_rejected_and_code_is_single_use(client):
    c, sent = client
    c.post("/v1/otp/request", json={"email": "a@example.com"})
    bad = "000000" if sent["code"] != "000000" else "111111"
    assert c.post("/v1/check", json={"email": "a@example.com", "code": bad}).status_code == 400
    assert c.post("/v1/check", json={"email": "a@example.com", "code": sent["code"]}).status_code == 200
    assert c.post("/v1/check", json={"email": "a@example.com", "code": sent["code"]}).status_code == 400


def test_lockout_after_too_many_wrong_codes(client):
    c, sent = client
    c.post("/v1/otp/request", json={"email": "b@example.com"})
    bad = "000000" if sent["code"] != "000000" else "111111"
    codes = [c.post("/v1/check", json={"email": "b@example.com", "code": bad}).status_code for _ in range(6)]
    assert codes[-1] == 429
    assert c.post("/v1/check", json={"email": "b@example.com", "code": sent["code"]}).status_code == 429


def test_resend_cooldown(client):
    c, _ = client
    assert c.post("/v1/otp/request", json={"email": "c@example.com"}).status_code == 200
    assert c.post("/v1/otp/request", json={"email": "c@example.com"}).status_code == 429


def test_code_for_other_email_does_not_work(client):
    c, sent = client
    c.post("/v1/otp/request", json={"email": "d@example.com"})
    assert c.post("/v1/check", json={"email": "e@example.com", "code": sent["code"]}).status_code == 400
