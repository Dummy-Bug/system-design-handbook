
A D2C (direct-to-consumer) brand — the kind of company selling straight to customers online, t-shirts and the like — wants their checkout form to **auto-fill city and state from a PIN code**. Type in a 6-digit PIN code, the rest of the address fills itself in. A familiar pattern from real checkout forms, now being built from the backend side.

The actual value being delivered: **less friction, fewer typos** in an address form — a customer typing 6 digits correctly is a much smaller ask than typing a city and state name correctly by hand.

As before, the boundary matters: this project builds the **server**, not the checkout form itself. The frontend calling it is out of scope.

---

## The flow

```mermaid
flowchart TD
    IN["PIN code comes in"] --> V{"Valid shape?<br/><i>6 digits</i>"}
    V -- "No" --> E1["400 or 422<br/><i>depends which route</i>"]
    V -- "Yes" --> L{"Found in<br/>PIN code data?"}
    L -- "No" --> E2["404 — not found"]
    L -- "Yes" --> OK["200 — city + state"]
```

Two separate failure modes, worth keeping distinct:

- **Malformed input** (not 6 digits, contains letters, wrong length) → rejected before any lookup happens at all. The data doesn't even need to be checked against anything to know it's invalid.
- **Well-formed but unsupported** (a real-looking 6-digit code that just isn't in the dataset) → `404`. This one **is** a lookup failure — the shape was fine, the value just isn't covered.

> [!important] The malformed case does **not** produce one single status code across this project, and the reason is worth understanding now rather than being surprised by it later. It depends entirely on **who catches the bad shape**:
>
> | Route | Who validates | Status |
> |---|---|---|
> | `GET /pincode/{code}` | a hand-written `if` inside the route, raising this project's own `InvalidPinCodeError` | `400` |
> | `POST /pincode/bulk` | Pydantic, against a model, before the route body runs | `422` |
>
> `422` is what **Pydantic** produces automatically whenever incoming data fails to match a model. A plain path parameter never goes through a model, so nothing produces a `422` there — the check has to be written by hand, and this project's hand-written version chooses `400`. Both are correct; they just come from two different mechanisms.

Same distinction as `/menu/{item_id}` in the previous project (a badly-typed id vs. a well-typed id that doesn't exist) — just applied to a different kind of input.

Like project 1, **database** here means a file, not an actual database — same constraint, same reasoning as before.

---

## What's actually new this time

The previous project's list — path params, query params, a Pydantic response model, raising `HTTPException` — is done. This project's four new pieces, in the order they'll show up:

1. **Pydantic `field_validator`** — custom validation logic beyond a plain type annotation. A type hint alone can say **this must be a string**; a field validator is what enforces something more specific, like **and it must be exactly 6 digits.**
2. **Custom exception classes and exception handlers** — moving past `raise HTTPException(...)` inline, toward defining an app's own exception types and a handler that controls how they get turned into a response. Flagged explicitly as something that looks like overkill in a small project but is genuinely how production FastAPI applications are structured.
3. **`POST` with a JSON body** — everything so far has been `GET`, reading data via path or query parameters. This is the first route accepting **structured data sent in the request body** rather than in the URL.
4. **Clean error response patterns** — a consistent shape for what an error response actually contains, applied deliberately rather than improvised per-route.

> [!note] The reasoning given for #4 is worth keeping: writing (or reviewing) code with an explicit sense of **this is the pattern I want** matters even more once AI tools are doing a lot of the typing — an AI generates whatever it's asked for, not necessarily the pattern that's actually wanted, unless that pattern is specified.
