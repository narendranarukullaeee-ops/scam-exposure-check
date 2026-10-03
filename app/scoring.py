"""Deterministic, explainable exposure scoring. No model is involved in the score or the level."""
from datetime import date, datetime

# category -> (label, points, severity, keywords matched against breach data-class names)
CATEGORIES = {
    "password": ("Passwords", 20, "CRITICAL", ("password",)),
    "identity": ("Government ID / SSN", 15, "CRITICAL", ("social security", "government", "passport")),
    "financial": ("Payment card / bank account data", 12, "HIGH", ("credit card", "bank account", "payment card")),
    "phone": ("Phone numbers", 10, "HIGH", ("phone",)),
    "secq": ("Security questions and answers", 8, "HIGH", ("security question",)),
    "address": ("Physical addresses", 10, "MEDIUM", ("physical address", "home address")),
    "dob": ("Dates of birth", 8, "MEDIUM", ("dates of birth", "date of birth", "birth date")),
}

# id, title, needs (any one set must be present; [] = any breach), boost categories, explanation, actions
SCENARIOS = [
    ("bank_call", "Fake bank or fraud-department call", [{"phone"}], {"address", "dob", "identity"},
     "A caller who already has your number and personal details sounds legitimate, which makes 'your account is compromised, move your money' scripts believable.",
     ["Hang up on unexpected calls about your accounts and call the number on your card or the bank's official site.",
      "Agree with family on a rule: nobody legitimate asks you to withdraw cash or move money in secret."]),
    ("sim_swap", "SIM swap or number takeover", [{"phone"}], {"dob", "identity"},
     "Phone number plus birth date or ID details is what an attacker needs to convince a carrier to move your number, then intercept text-message codes.",
     ["Set a PIN or port-out lock on your mobile account.", "Move two-factor codes from text messages to an authenticator app."]),
    ("credential_stuffing", "Account takeover with leaked passwords", [{"password"}], {"secq"},
     "Leaked passwords get tried automatically on email, shopping, and banking sites, especially if you reuse them.",
     ["Change any password that matches one used in these breaches, and never reuse it.",
      "Use a password manager and turn on two-factor authentication for email and banking."]),
    ("identity_theft", "New-account identity theft", [{"identity"}, {"dob", "address"}], set(),
     "Name, birth date, address, or ID numbers together can be used to open accounts or credit in your name.",
     ["Freeze your credit at all three bureaus (free).", "Monitor your accounts and request your free credit reports."]),
    ("card_scam", "Payment-card and refund scams", [{"financial"}], set(),
     "Exposed card or bank details let scammers sound credible on 'suspicious charge' and refund calls.",
     ["Ask your bank to replace exposed cards and turn on transaction alerts."]),
    ("phishing", "Targeted phishing and fake-alert texts", [], set(),
     "Knowing which companies leaked your data lets scammers write convincing 'your account at X needs attention' messages.",
     ["Don't click links in unexpected messages; open the company's app or site yourself."]),
]

PHONE_GUIDANCE = [
    "Set a carrier account PIN and a port-out lock so your number can't be moved without you.",
    "Use an authenticator app or passkey instead of text-message codes where you can.",
    "Treat any call or text about 'fraud on your account' as unverified until you call back on a number you looked up yourself.",
    "Never read out one-time codes, even to someone who says they are from your bank.",
]
DISCLAIMER = ("Each breach record lists what that breach contained overall, so not every item may apply to you personally. "
              "Some sensitive breaches are not searchable publicly, so a clean result is not a guarantee.")
GENERAL_ACTIONS = ["Opt out of people-search and data-broker sites that list your address and relatives."]
_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def _years_ago(d: str, today: date):
    try:
        return (today - datetime.strptime(d, "%Y-%m-%d").date()).days / 365.25
    except ValueError:
        return None


def level_for(score: int) -> str:
    return "LOW" if score < 25 else "MEDIUM" if score < 50 else "HIGH" if score < 75 else "CRITICAL"


def assess(breaches, today=None) -> dict:
    today = today or date.today()
    found = {}
    for b in breaches:
        for dc in b.data_classes:
            for cat, (_, _, _, kws) in CATEGORIES.items():
                if any(k in dc.lower() for k in kws) and b.name not in found.setdefault(cat, []):
                    found[cat].append(b.name)
    present = set(found)
    ages = [a for a in (_years_ago(b.date, today) for b in breaches) if a is not None]
    recent = bool(ages) and min(ages) <= 2

    factors = []
    if breaches:
        factors.append({"factor": f"{len(breaches)} known breach(es)", "points": min(25, 5 * len(breaches))})
    cat_points = min(60, sum(CATEGORIES[c][1] for c in present))
    if cat_points:
        factors.append({"factor": "Types of data exposed", "points": cat_points})
    if ages and min(ages) <= 5:
        factors.append({"factor": "Breach within the last 2 years" if recent else "Breach within the last 5 years",
                        "points": 10 if recent else 5})
    if any(b.sensitive for b in breaches):
        factors.append({"factor": "Sensitive breach", "points": 5})
    if {"password", "phone"} <= present:
        factors.append({"factor": "Password and phone exposed together", "points": 5})
    if {"phone", "address", "dob"} <= present:
        factors.append({"factor": "Phone, address and birth date exposed together", "points": 10})
    score = min(100, sum(f["points"] for f in factors))

    scenarios, actions = [], []
    for sid, title, needs, boost, text, acts in SCENARIOS:
        if sid == "phishing":
            if not breaches:
                continue
            lk = "HIGH" if recent else "MEDIUM" if len(breaches) >= 2 else "LOW"
        else:
            if not any(n <= present for n in needs):
                continue
            lk = "HIGH" if (boost & present) or recent else "MEDIUM"
        scenarios.append({"id": sid, "title": title, "likelihood": lk, "description": text})
        actions += [a for a in acts if a not in actions]
    scenarios.sort(key=lambda s: -_RANK[s["likelihood"]])
    if breaches:
        actions += GENERAL_ACTIONS

    return {
        "score": score, "level": level_for(score), "factors": factors,
        "breach_count": len(breaches),
        "breaches": [{"name": b.name, "date": b.date, "data": b.data_classes} for b in breaches],
        "exposures": [{"data_type": CATEGORIES[c][0], "severity": CATEGORIES[c][2], "breaches": n}
                      for c, n in sorted(found.items(), key=lambda kv: -CATEGORIES[kv[0]][1])],
        "scenarios": scenarios, "actions": actions,
        "phone_exposed": "phone" in present, "phone_guidance": PHONE_GUIDANCE,
        "disclaimer": DISCLAIMER,
    }
