# Design note: using exposure signals in a bank, with consent

**Status:** concept. Not implemented, not tested with any institution, and based only on public information.

## Problem
In authorized scams the customer makes the payment themselves, having been coached by the offender. Detection that looks at the transaction alone arrives late. What the offender relies on is *credibility*, and credibility is built from leaked personal data: a phone number, a birth date, an address, the name of a company that was breached.

## Idea
With the customer's explicit opt-in, a bank could check *their own* contact email against breach data (exactly as this demo does) and receive a coarse, explainable exposure level, not the raw breach list.

## Possible uses
| Use | How the signal helps |
|---|---|
| Step-up authentication | Higher exposure on phone and birth date means stronger verification before changing contact details or porting a number |
| Customer education | Tailored warnings ("callers may already know your address; here is how to verify a call") instead of generic banners |
| Counter or call-centre conversations | A prepared, non-accusatory prompt for staff when a customer is making an unusual cash withdrawal |

## Guardrails
- **Opt-in only.** No lookup without the customer verifying their own email.
- **Minimum data.** Pass an exposure *level* and category flags, not breach names or raw data.
- **Never a reason to deny service.** It informs friction and messaging only, and is not a credit or eligibility signal.
- **Explainable.** Rule-based scoring so a customer or reviewer can see why.
- **Retention.** Do not store breach results beyond the session unless the customer asks.

## Open questions
- Does exposure level actually predict scam victimization? This needs labelled outcome data and is **not** established here.
- Does tailored messaging change behaviour more than generic messaging? Needs a controlled test.
- Legal review (consumer-reporting and privacy rules) before any production use.

---
*Personal design note. Views are my own and not related to my employer.*
