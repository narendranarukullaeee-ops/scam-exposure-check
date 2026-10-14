"""Build the static, no-sign-up demo page (docs/index.html).

Three made-up people are scored by the same rule engine the app uses (app/scoring.py),
on the app's own simulated breach records, so the page always matches the code.

    python scripts/build_demo.py                 # writes docs/index.html
    python scripts/build_demo.py --fragment out  # also writes a body-only copy (for embedding)
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.breaches import _SIM  # noqa: E402
from app.scoring import CATEGORIES, assess  # noqa: E402
from app.summary import _PHRASE, _join, template_summary  # noqa: E402

SCORED_ON = date(2026, 10, 14)
REPO = "https://github.com/narendranarukullaeee-ops/scam-exposure-check"

# Made-up people. Each one is given some of the app's simulated breach records.
PEOPLE = [
    {"id": "margaret", "name": "Margaret", "age": 71, "role": "Retired teacher",
     "story": "Her mobile carrier was breached last year.", "breaches": ["ExampleTelecom"]},
    {"id": "dev", "name": "Dev", "age": 34, "role": "Product manager",
     "story": "Used the same password on a shop and a forum for years.", "breaches": ["ExampleShop", "ExampleForum"]},
    {"id": "sam", "name": "Sam", "age": 24, "role": "Graduate student",
     "story": "Has one old account at a fitness app that was breached.", "breaches": ["ExampleFitness"]},
]


def build_data():
    by_key = {b.name.split(" ")[0]: b for b in _SIM}
    people = []
    for p in PEOPLE:
        breaches = [by_key[k] for k in p["breaches"]]
        result = assess(breaches, today=SCORED_ON)
        result["summary"] = template_summary(result)
        result["attribution"] = "Simulated data for demonstration."
        people.append({**{k: v for k, v in p.items() if k != "breaches"}, "result": result})
    scored_types = _join([_PHRASE.get(label, label.lower()) for (label, _, _, _) in CATEGORIES.values()])
    return {"people": people, "scored_on": SCORED_ON.isoformat(), "scored_types": scored_types, "repo": REPO}


TITLE = "<title>Exposure Check Demo</title>\n"
DESCRIPTION = ('<meta name="description" content="Three made-up people, simulated breach data, '
               'and what the Exposure Check rule engine tells each of them.">\n')
# Only for the body-only copy embedded in a host page that pads for phone safe areas.
EMBED_META = '<meta name="claude:viewport-fit-sides" content="cover">\n'

STYLE = r"""<style>
/* Layout: one reading column like the live app; the three people sit in a row of tabs that stacks on phones,
   and the selected person's input (breach records) sits above the result the app would show them. */
:root{
  --bg:#eef2f5; --surface:#ffffff; --ink:#112230; --muted:#566774; --line:#cbd5dd; --accent:#1e4fd6; --accent-soft:#e3eafc;
  --g-low:#2f7d5b; --g-med:#c98a12; --g-high:#d4682a; --g-crit:#b3261e;
  --t-low:#23674a; --t-med:#8a5c00; --t-high:#ad4716; --t-crit:#a4211a;
  --note-bg:#fff4d6; --note-line:#e3c36a;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#0e1720; --surface:#16222d; --ink:#e3eaf0; --muted:#9aabb8; --line:#2b3b48; --accent:#8aaaff; --accent-soft:#1d2a45;
  --g-low:#3f9b72; --g-med:#d9a032; --g-high:#e57a3e; --g-crit:#d0463d;
  --t-low:#66c99c; --t-med:#e8b54e; --t-high:#f39a62; --t-crit:#f47d73;
  --note-bg:#2c2716; --note-line:#7c6a2e; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0e1720; --surface:#16222d; --ink:#e3eaf0; --muted:#9aabb8; --line:#2b3b48; --accent:#8aaaff; --accent-soft:#1d2a45;
  --g-low:#3f9b72; --g-med:#d9a032; --g-high:#e57a3e; --g-crit:#d0463d;
  --t-low:#66c99c; --t-med:#e8b54e; --t-high:#f39a62; --t-crit:#f47d73;
  --note-bg:#2c2716; --note-line:#7c6a2e; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 var(--sans)}
main{max-width:720px;margin:0 auto;padding-block:40px 72px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3{font-family:var(--serif);font-weight:600;text-wrap:balance;letter-spacing:-.01em}
h1{font-size:clamp(34px,7vw,48px);line-height:1.05;margin:6px 0 14px}
h2{font-size:22px;line-height:1.2;margin:36px 0 10px}
h3{font-size:18px;margin:0 0 8px}
p{margin:0 0 12px;max-width:65ch}
a{color:var(--accent)}
a:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
.lede{font-size:18px;color:var(--ink)}
.muted{color:var(--muted);font-size:14px}
.note{background:var(--note-bg);border:1px solid var(--note-line);border-radius:6px;padding:10px 14px;font-size:14px;margin:18px 0 0}

.people{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:26px 0 0}
.person{all:unset;box-sizing:border-box;display:flex;flex-direction:column;gap:4px;cursor:pointer;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:14px 16px;min-width:0}
.person:hover{border-color:var(--muted)}
.person[aria-selected="true"]{border:2px solid var(--accent);padding:13px 15px;background:var(--accent-soft)}
.person:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.person .who{font:600 20px/1.2 var(--serif)}
.person .role{font-size:14px;color:var(--muted)}
.person .story{font-size:14px;line-height:1.4;margin-top:4px;flex:1}
.chip{align-self:flex-start;margin-top:8px;font-size:13px;font-weight:700;font-variant-numeric:tabular-nums;border:1px solid currentColor;border-radius:999px;padding:1px 10px}

.panel{margin-top:30px}
.input{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
.input ul{list-style:none;margin:0;padding:0}
.input li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 12px;padding:8px 0;border-top:1px solid var(--line)}
.input li:first-child{border-top:0;padding-top:2px}
.input .bname{font-weight:600;min-width:0}
.input .bdate{font-family:var(--mono);font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.input .bdata{grid-column:1 / -1;font-size:14px;color:var(--muted)}

.result{margin-top:28px}
.scoreline{display:flex;align-items:baseline;gap:6px}
.big{font:600 60px/1 var(--serif);font-variant-numeric:tabular-nums}
.level{font-size:14px;font-weight:700;margin-top:4px}
.gauge{position:relative;height:12px;border-radius:6px;margin:20px 0 8px;background:linear-gradient(90deg,var(--g-low) 0 25%,var(--g-med) 25% 50%,var(--g-high) 50% 75%,var(--g-crit) 75% 100%)}
.gauge i{position:absolute;top:-6px;width:4px;height:24px;background:var(--ink);border-radius:2px;transform:translateX(-2px);transition:left .35s ease}
.scale{display:flex;justify-content:space-between;font-size:13px;color:var(--muted)}
.item{border-top:1px solid var(--line);padding:12px 0}
.item b{display:block}
.tag{font-size:13px;font-weight:700;white-space:nowrap}
.LOW{color:var(--t-low)}.MEDIUM{color:var(--t-med)}.HIGH{color:var(--t-high)}.CRITICAL{color:var(--t-crit)}
.factors{width:100%;border-collapse:collapse;font-size:15px}
.factors td{padding:8px 0;border-top:1px solid var(--line);vertical-align:top}
.factors td.pts{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--mono);font-size:14px;padding-left:16px;white-space:nowrap}
.factors tr.total td{border-top:2px solid var(--ink);font-weight:700}
ul.list{padding-left:20px;margin:0 0 12px}
ul.list li{margin:6px 0}
ol.steps{padding-left:22px;margin:0}
ol.steps li{margin:6px 0;padding-left:4px}
footer{margin-top:44px;border-top:1px solid var(--line);padding-top:16px;display:flex;flex-direction:column;gap:8px}
footer p{margin:0}
@media (max-width:640px){.people{grid-template-columns:minmax(0,1fr)}.big{font-size:52px}}
@media (prefers-reduced-motion:reduce){.gauge i{transition:none}}
</style>
"""

MARKUP = r"""
<main>
  <div class="eyebrow">Demo · simulated data · no sign-up</div>
  <h1>Exposure Check</h1>
  <p class="lede">A breach check tells you what leaked. Exposure Check turns that into the scam scripts it makes believable, and what to do first.</p>
  <p class="muted">Pick one of three made-up people to see what the tool would show them. Their breach records are fictional, and every score below comes from the app's own rule engine.</p>

  <div class="people" role="tablist" aria-label="Made-up people" id="people"></div>

  <section class="panel" role="tabpanel" id="panel" aria-live="polite">
    <div class="input">
      <h3 id="in-title">Breach records</h3>
      <ul id="in-list"></ul>
    </div>

    <div class="result">
      <div class="eyebrow">What the tool shows <span id="r-name"></span></div>
      <div class="scoreline"><span class="big" id="r-score"></span><span class="muted">/ 100</span></div>
      <div class="level" id="r-level"></div>
      <div class="gauge" aria-hidden="true"><i id="r-mark"></i></div>
      <div class="scale" aria-hidden="true"><span>Low</span><span>Medium</span><span>High</span><span>Critical</span></div>
      <p id="r-summary" style="margin-top:18px"></p>

      <h2>What was exposed</h2><div id="r-exp"></div>
      <h2>How a scammer could use it</h2><div id="r-scn"></div>
      <h2>Why this score</h2>
      <p class="muted">Every point is listed, so anyone can check the result. No AI model is involved in the score.</p>
      <table class="factors"><tbody id="r-factors"></tbody></table>
      <h2>What to do next</h2><ul class="list" id="r-act"></ul>
      <h2>Protect your phone number</h2><ul class="list" id="r-phone"></ul>
      <p class="note" id="r-note"></p>
    </div>
  </section>

  <h2>How the real app works</h2>
  <ol class="steps">
    <li>You confirm your own email with a one-time code, so nobody can look up someone else. The demo skips this step.</li>
    <li>The app checks that one address against a breach database. The demo uses simulated records instead.</li>
    <li>A fixed rule engine scores the exposure, ranks the scam scripts it makes believable, and lists every point.</li>
    <li>If an API key is set, an AI model rewrites the result in plain English. It never sees the email or changes the score.</li>
    <li>Nothing is stored: not the email, the code or the result.</li>
  </ol>

  <footer class="muted">
    <p>Code, tests and design notes: <a id="repo-link" href="#">GitHub</a>. How a bank could use this signal with customer consent: <a id="bank-link" href="#">design note</a>.</p>
    <p id="scored-on"></p>
    <p>Personal project. Not affiliated with any employer, bank or breach-data provider. Views are my own and not related to my employer.</p>
  </footer>
</main>

<script>
const DATA = __DATA__;
const $ = s => document.getElementById(s);
const mk = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const monthYear = iso => { const [y, m] = iso.split('-'); return MONTHS[+m - 1] + ' ' + y; };
const cap = s => s.charAt(0) + s.slice(1).toLowerCase();

$('repo-link').href = DATA.repo;
$('bank-link').href = DATA.repo + '/blob/main/docs/BANK_USE.md';
const [sy, sm, sd] = DATA.scored_on.split('-');
$('scored-on').textContent = 'Scores computed by app/scoring.py on ' + (+sd) + ' ' + MONTHS[+sm - 1] + ' ' + sy + '. Breach names are fictional and the people are made up.';

const tabs = DATA.people.map((p, i) => {
  const b = mk('button', 'person');
  b.type = 'button'; b.id = 'tab-' + p.id; b.setAttribute('role', 'tab'); b.setAttribute('aria-controls', 'panel');
  b.append(mk('span', 'who', p.name + ', ' + p.age), mk('span', 'role', p.role), mk('span', 'story', p.story));
  b.append(mk('span', 'chip ' + p.result.level, cap(p.result.level) + ' · ' + p.result.score));
  b.addEventListener('click', () => select(i, true));
  b.addEventListener('keydown', e => {
    const k = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
    if (k) { e.preventDefault(); const j = (i + k + DATA.people.length) % DATA.people.length; select(j, true); tabs[j].focus(); }
  });
  $('people').append(b);
  return b;
});

function select(i, fromUser) {
  const p = DATA.people[i], d = p.result;
  tabs.forEach((t, j) => { t.setAttribute('aria-selected', j === i ? 'true' : 'false'); t.tabIndex = j === i ? 0 : -1; });
  $('panel').setAttribute('aria-labelledby', 'tab-' + p.id);

  $('in-title').textContent = 'Breach records for ' + p.name + ' (simulated)';
  const inl = $('in-list'); inl.replaceChildren();
  d.breaches.forEach(b => { const li = mk('li'); li.append(mk('span', 'bname', b.name.replace(' (simulated)', '')), mk('span', 'bdate', monthYear(b.date)), mk('span', 'bdata', b.data.join(', '))); inl.append(li); });

  $('r-name').textContent = p.name;
  $('r-score').textContent = d.score;
  $('r-mark').style.left = Math.min(d.score, 99) + '%';
  const lv = $('r-level'); lv.textContent = cap(d.level) + ' exposure'; lv.className = 'level ' + d.level;
  $('r-summary').textContent = d.summary;

  const exp = $('r-exp'); exp.replaceChildren();
  if (!d.exposures.length) {
    exp.append(mk('p', '', 'No exposed personal data types were found for this address.'));
    exp.append(mk('p', 'muted', 'The tool scores seven kinds of data: ' + DATA.scored_types + '. This breach held none of them.'));
  }
  d.exposures.forEach(x => { const it = mk('div', 'item'); it.append(mk('b', '', x.data_type), mk('span', 'muted', 'Exposed in: ' + x.breaches.map(n => n.replace(' (simulated)', '')).join(', '))); exp.append(it); });

  const scn = $('r-scn'); scn.replaceChildren();
  if (!d.scenarios.length) scn.append(mk('p', '', 'No specific scam scenarios stand out from this data.'));
  d.scenarios.forEach(x => { const it = mk('div', 'item'); const b = mk('b', '', x.title + ' '); b.append(mk('span', 'tag ' + x.likelihood, '(' + x.likelihood.toLowerCase() + ' likelihood)')); it.append(b, mk('span', '', x.description)); scn.append(it); });

  const tb = $('r-factors'); tb.replaceChildren();
  d.factors.forEach(f => { const tr = mk('tr'); tr.append(mk('td', '', f.factor), mk('td', 'pts', '+' + f.points)); tb.append(tr); });
  const raw = d.factors.reduce((s, f) => s + f.points, 0);
  const tr = mk('tr', 'total'); tr.append(mk('td', '', raw > 100 ? 'Score (capped at 100)' : 'Score'), mk('td', 'pts', String(d.score))); tb.append(tr);

  const fill = (id, list) => { const ul = $(id); ul.replaceChildren(); list.forEach(t => ul.append(mk('li', '', t))); };
  fill('r-act', d.actions.length ? d.actions : ['Keep two-factor authentication on for email and banking.']);
  fill('r-phone', d.phone_guidance);
  $('r-note').textContent = d.disclaimer + ' ' + d.attribution;

  if (fromUser) { try { history.replaceState(null, '', '#' + p.id); } catch (_) {} }
}

const start = Math.max(0, DATA.people.findIndex(p => '#' + p.id === location.hash));
select(start, false);
</script>
"""


def render(full: bool) -> str:
    data = json.dumps(build_data(), ensure_ascii=False).replace("</", "<\\/")
    markup = MARKUP.replace("__DATA__", data)
    if not full:
        return TITLE + EMBED_META + DESCRIPTION + STYLE + markup
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            + TITLE + DESCRIPTION + STYLE + "</head>\n<body>" + markup + "</body>\n</html>\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fragment", help="also write a body-only copy to this path")
    args = ap.parse_args()
    out = ROOT / "docs" / "index.html"
    out.write_text(render(full=True), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))
    if args.fragment:
        Path(args.fragment).write_text(render(full=False), encoding="utf-8")
        print("wrote", args.fragment)
