"""Plain-language summary. The model only explains a result that scoring.py already computed,
and it never sees the email address."""
import logging

log = logging.getLogger("summary")

# How each data type reads in the middle of a sentence.
_PHRASE = {
    "Passwords": "passwords",
    "Government ID / SSN": "government ID or Social Security numbers",
    "Payment card / bank account data": "payment card or bank account details",
    "Phone numbers": "phone numbers",
    "Security questions and answers": "security questions and answers",
    "Physical addresses": "physical addresses",
    "Dates of birth": "dates of birth",
}


def _join(items):
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def template_summary(a: dict) -> str:
    if not a["breach_count"]:
        return "This address wasn't found in any known data breach. That is good news, but it doesn't mean your data is private everywhere. Keep two-factor authentication on and stay cautious with unexpected calls and messages."
    n = a["breach_count"]
    top = _join([_PHRASE.get(e["data_type"], e["data_type"].lower()) for e in a["exposures"][:3]]) or "contact details"
    return (f"This address appears in {n} known {'breach' if n == 1 else 'breaches'}, which exposed {top} for affected accounts. "
            f"Your exposure level is {a['level'].lower()}. The steps below are the quickest ways to make that data less useful to a scammer.")


def write_summary(settings, cap, a: dict):
    """Returns (text, source). Falls back to the template on any problem."""
    if not settings.gemini_api_key or not a["breach_count"] or not cap.take():
        return template_summary(a), "template"
    prompt = (
        "Write a calm, plain-English summary (3 to 4 sentences) for a person about their data-breach exposure. "
        "Use only the facts below. Do not invent breaches, numbers, or advice, and do not be alarmist. "
        "Say the breaches exposed data for affected accounts; never claim a specific item was definitely the person's own.\n"
        f"Exposure level: {a['level']}\nBreaches: {', '.join(b['name'] for b in a['breaches'])}\n"
        f"Data exposed: {', '.join(e['data_type'] for e in a['exposures']) or 'basic contact details'}\n"
        f"Main scam risks: {', '.join(s['title'] for s in a['scenarios'][:3])}")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.gemini_api_key)
        r = client.models.generate_content(model=settings.gemini_model, contents=prompt,
                                           config=types.GenerateContentConfig(temperature=0.3))
        text = (r.text or "").strip()
        if text:
            return text, "gemini"
    except Exception as e:  # never fail the request because the explainer failed
        log.warning("Gemini summary failed: %s", type(e).__name__)
    return template_summary(a), "template"
