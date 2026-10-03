# LinkedIn launch post (draft)

By the time someone is at a bank counter withdrawing cash for a scammer, the offender has usually coached them on what to say. What makes that coaching believable? Often it's personal data that leaked years ago: a phone number, a birth date, an address.

I built a small prototype to explore that. You verify your own email with a one-time code, and the tool translates a breach check into what matters for scams: which scripts a caller could use, how likely they are, and what to do first.

A few choices I made on purpose:
- Verify first, so nobody can look up someone else
- A transparent rule-based score; the AI is optional and only writes the plain-English summary
- Nothing is stored
- No phone lookup, because text-message verification is costly and easy to abuse

To be clear about what it is: the public demo uses simulated breach data. The design is built to run on a real breach-data API (such as Have I Been Pwned), but I haven't put real people's data through it. The part I wanted to explore is the one most tools skip: turning "you were breached" into "here is how it gets used against you."

Code and design notes (including how a bank could use this signal with customer consent): https://github.com/narendranarukullaeee-ops/scam-exposure-check

Personal project. My views are my own and not related to my employer. I'd value feedback from anyone working on scam prevention.

#scams #fraudprevention #cybersecurity
