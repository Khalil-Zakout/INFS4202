# AI usage log

One entry per meaningful use. We used AI assistants to accelerate understanding,
test-data and boundary enumeration, scaffolding and documentation. Every kept
artefact was checked against the Requirements and the running system, and **every
reported defect was reproduced by hand** before it was filed. No API key was ever
committed; the AI-eval runner reads it from an environment variable.

Replace `[Member]` / `[dd/MM]` with the real author and date for each row.

| Date | Member | Tool & model | Purpose | Prompt summary | Kept | Modified (how) | Rejected (why) |
|------|--------|--------------|---------|----------------|------|----------------|----------------|
| [dd/MM] | Monir | Claude (Opus) | Understand the system | "Summarise the architecture and the Portal↔Engine calls from these sources" | Component/flow model used in report Q1 | Re-checked each call against the code | — |
| [dd/MM] | Monir | ChatGPT | Enumerate Engine boundaries | "List boundary values for GPA, credits, 2/5 MB, 180-day transcript, 15–120 min, 08:00–18:00, allowance months/caps/penalty weeks" | The boundary list behind `tests/api` | Added the exact byte boundaries (2,097,152 / 5,242,880) from the OpenAPI | Dropped suggestions not in the contract |
| [dd/MM] | Monir | Claude | Scaffold the Engine contract suite | "Write zero-dependency Python unittest cases asserting the openapi.yaml behaviour" | `tests/api/test_engine_contract.py` structure | Rewrote oracles to the spec, not to observed output; split DEFECT cases | — |
| [dd/MM] | Khalil | ChatGPT | Draft the seat-race concurrency test | "Two threads accepting the last seat via HTTP with a barrier" | `tests/system` seat-race idea | Tuned to our CSRF/session client; added a 6-attempt loop | First draft used requests (not installed); switched to stdlib |
| [dd/MM] | Khalil | Claude | Reason about OFF-03/OFF-05 | "Given these service methods, what does accept() fail to do when the posting fills?" | The OFF-03 hypothesis (remaining apps not rejected) | Verified on the running system before filing | — |
| [dd/MM] | Abdulaziz | Claude | Security test ideas | "Which access-control and secret-handling checks apply to USR-05 / SEC-01..07?" | IDOR, CSRF, session, secrets, XSS checklist | Reproduced each by hand; discarded ones the code already blocks | Rejected a "SQL injection on search" idea — queries are parameterised (no defect) |
| [dd/MM] | Abdulaziz | ChatGPT | Explain BCrypt vs plaintext | "Is a BCrypt hash enough for SEC-01?" | Confirmed SEC-01 holds (hash is salted) | — | Did not file a SEC-01 issue (no defect) |
| [dd/MM] | Abdulaziz | Claude | Design AI property tests | "Properties that must hold for letter feedback regardless of model (AI-01/04/06/09)" | `tests/ai-eval` property set and runner | Added PII-echo and injection-leak checks against the ai-eval `checks` | — |
| [dd/MM] | Abdulaziz | Claude | Draft improved prompt v2 | "Rewrite the feedback prompt to drop PII, the internal threshold and the bad example, keep the JSON contract" | `prompts.py` v2 | Kept the band-comparable format; stated the criterion before runs | Rejected a version that added a rubric table (would leak thresholds again) |
| [dd/MM] | Abdulaziz | ChatGPT | Generate extra fictional letters | "Five more fictional internship letters, clearly marked, no real data" | (optional) added under our own IDs | Marked as ours; reported separately from the original 20 | — |
| [dd/MM] | All | Claude | Draft report & docs wording | "Tighten these sections; keep every number matching the repo" | Report/strategy prose | Numbers re-checked against issues and CI | Rejected any claim we had not reproduced |

## Reflection

**Where AI helped.** Fast, broad **boundary enumeration** (the Engine suite's edge
cases came from an AI list we then pinned to the OpenAPI), **scaffolding** of the
zero-dependency test harnesses, and **reading unfamiliar code** quickly to form
hypotheses (e.g. "accept() sets FILLED but never rejects the rest"). It was also
useful as a second pair of eyes on the AI prompt itself — the privacy and
threshold leaks are the kind of thing a reviewer skims past.

**Where AI was wrong or risky.** It occasionally proposed "defects" that the code
already prevents (parameterised queries, BCrypt hashing) — filing those would have
cost us −1 each, so **every hypothesis was reproduced on the running system before
filing**. It also suggested libraries not available offline (we kept the suites to
the standard library). And when asked to improve the AI prompt it first reintroduced
an internal rubric with thresholds — exactly the AI-10 problem we were fixing — which
we rejected.

**How we checked it.** Oracle = Requirements + `openapi.yaml`, never the model's or
the system's own output. Each kept test states the requirement it checks; each
reported defect has steps that reproduce it on a fresh `--reset`.
