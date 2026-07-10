# Why POST (not GET) for a Streaming AI-Agent Endpoint

A common design question: an AI assistant is served by a single endpoint that streams the agent's events back to the client. Should that endpoint be a `GET` or a `POST`? Here is the reasoning, using a generic AI-agent API as the example.

There are two independently sufficient reasons, plus one supporting one. **Either of the first two settles it on its own.**

---

## Background: what GET vs POST actually promises

HTTP verbs carry a *contract* that the whole ecosystem trusts and acts on automatically:

- **GET** is defined as **safe** (does not change state) and **idempotent** (calling it N times = calling it once). Query inputs live in the **URL**, and a GET has **no request body**.
- **POST** is the verb for **"this does something / changes state / carries a payload."** It has a request body.

The word "safe" is load-bearing: browsers prefetch GET URLs, link-preview unfurlers (chat apps expanding a pasted link) fetch them, crawlers hit them, antivirus URL scanners open them, `<link rel=preload>` fires them. **Anything behind a GET can be triggered without a human intending it.**

---

## Reason 1 — Side effects (the semantic clincher)

An agent that can *act* — not just answer — performs **mutating actions on external systems**. For example, an onboarding/offboarding agent runs actions like:

```
ADD_USER            → create an account in an external SaaS system
DELETE_USER         → remove an account
ADD_USER_TO_GROUP   → grant access
REINSTATE_USER      → restore access
```

Each of these changes state in a downstream system.

**Why this forces POST:** a request that runs `ADD_USER` / `DELETE_USER` is not safe and not idempotent, so GET is *semantically wrong*. Worse, if provisioning lived behind a GET, a prefetch / crawler / link-unfurl could trigger real account creation with no human in the loop. **Mutation ⟹ not GET. This ends the argument by itself.**

> Even if the write path is behind a feature flag or partially built, you pick the verb for what the endpoint's **contract** does, not for what a stub currently executes. An endpoint designed to trigger mutations is a POST.

---

## Reason 2 — Polymorphic (document-shaped) request body

A conversational agent endpoint often does not accept one fixed request shape. It accepts a **discriminated union** of shapes, tagged by a `type` field:

```python
class NewMessage(BaseModel):
    type: Literal["message"]           # discriminator
    text: str

class InteractionResponse(BaseModel):
    type: Literal["interaction_response"]   # discriminator
    selected_value: str
    interaction_meta: InteractionMeta   # NESTED object {interaction_id, action}

RequestBody = Annotated[
    Union[NewMessage, InteractionResponse],
    Field(discriminator="type"),        # "one of these two, decided by `type`"
]
```

The user can do two genuinely different things:

- **Send a new message** — the data is text: `{ "type": "message", "text": "how many leaves do I have?" }`
- **Answer a human-in-the-loop (HITL) prompt** — e.g. picking one option from a disambiguation list. The data is *which option they chose* + *which question they're answering*:
  ```json
  { "type": "interaction_response",
    "selected_value": "OPT-4821",
    "interaction_meta": { "interaction_id": "thread9:select:john", "action": "SELECT_OPTION" } }
  ```

**Why this forces POST:** a GET's only data model is the URL query string — **flat `key=value` pairs**. This data is neither flat nor single-shaped:

1. **Nested object.** `interaction_meta` is an object inside the object. Query strings have no native nesting — you'd have to invent `interaction_meta[interaction_id]=…` (non-standard; validation libraries won't parse it cleanly) or URL-encode the whole JSON blob into one param (= "JSON smuggled through a URL", which reintroduces log-leak/length problems).
2. **Discriminated union.** With a body, one validation call reads `type` and selects the correct model. Over query params there is no structured document to validate — you'd hand-branch and lose framework validation.

**Core idea:** nested + tagged/variant data is *document-shaped*, and HTTP's home for a document is the **request body**. POST has a body; GET doesn't. This reason is purely about **representation** — it stands even if the endpoint were read-only and non-sensitive.

---

## Reason 3 — Keep sensitive query text out of URL logs (supporting)

Even short user text can be sensitive ("what's my salary", personal names). A GET puts it in the URL, which lands in **access logs, proxy logs, browser history, and `Referer` headers**. A body keeps it out of all of those. A nice supporting point; not needed to win.

---

## A note on input caps

If your endpoint caps input length (e.g. a max-characters check), **don't lead with that in an interview** — a short cap means a GET query param *would* fit lengthwise, which only hands the interviewer a "why not GET then?" thread. It's an internal validation detail. Answer only if directly asked about input limits, and pivot back to the semantic (side-effect) and structural (document-shaped body) reasons.

---

## How to answer in interview

**The cadence that reads as senior: give ONE decisive reason, then stop. Reveal more only when probed.** A junior lists five reasons (sounds unsure); a senior gives the one that settles it and shows depth on demand.

**Lead with the semantic clincher:**

> "It's a POST because the endpoint triggers state changes — it provisions accounts (create / remove users in external systems) — so GET would be semantically wrong. GET is supposed to be safe and idempotent, and a prefetch or crawler hitting a provisioning GET could create real accounts unintentionally."

**Then stop.** If they push ("is that the only reason?"), deploy the second:

> "Also the request body is a discriminated union — either a normal message or a human-in-the-loop selection-response that carries a nested metadata object. That's document-shaped data, so it wants a body regardless of the side-effect argument. A GET query string can only fake nesting with non-standard hacks."

**Do NOT:** recite all three reasons as a list; volunteer internal input caps; overstate how much of the write path is live.

**One-line summary:** *mutation ⟹ not GET (Reason 1); document-shaped body ⟹ wants a body ⟹ POST (Reason 2). Either alone is enough.*
