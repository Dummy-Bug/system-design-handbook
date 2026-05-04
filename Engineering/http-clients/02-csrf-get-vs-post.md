#csrf #http #cookies #security #get-vs-post #service-to-service

---

# Why Do Stale Cookies Pass on GET but Fail on POST?

> Prerequisite: [[http-client-as-browser]] — establishes that a shared HTTP client has a cookie jar that accumulates silently.

You have a bug where a shared HTTP client sends stale cookies. You test a GET request — it passes. You assume the cookies are valid. Then a POST to the same host with the same cookies gets a 401. Same client. Same tokens. Different result. Why does one method catch the bad token and the other doesn't?

---

## The Setup

Two calls to the same upstream service, same `SESSION` and `XSRF-TOKEN` cookies:

```python
await client.get("/data", cookies={"SESSION": token, "XSRF-TOKEN": xsrf})    # 200
await client.post("/action", cookies={"SESSION": token, "XSRF-TOKEN": xsrf}) # 401
```

The GET passes. The POST fails. If the tokens were the problem, both would fail.

---

## What CSRF Protection Actually Is

CSRF (Cross-Site Request Forgery) is an attack where a malicious website tricks a logged-in user's browser into making a request to a different site — carrying that site's session cookies automatically.

The attack only works with state-changing operations. A malicious page tricking your browser into a silent `GET /profile` is harmless — GET reads data, it doesn't change anything. But a malicious page tricking your browser into `POST /transfer-money` is dangerous.

So the server defends only where it matters:

- **GET, HEAD, OPTIONS** — safe methods, read-only, no state change. CSRF protection not applied.
- **POST, PUT, DELETE, PATCH** — unsafe methods, state-changing. CSRF protection enforced.

The protection mechanism: the server requires an `X-XSRF-TOKEN` header on every state-changing request, and checks that it matches the `XSRF-TOKEN` cookie. A cross-site attacker cannot read cookies from another domain, so they cannot set this header — the request fails. A legitimate client can read its own cookies and mirrors the value.

> [!important] CSRF protection is not applied uniformly. It is applied specifically to the HTTP methods that can change state. GET is exempt by design.

---

## Why GET Passes Even With Wrong Cookies

When your shared client's jar holds a rotated/stale `SESSION` token and you make a GET:

1. Server receives the request
2. Server validates the `SESSION` cookie — perhaps it checks it, perhaps it ignores it for read endpoints
3. Server does **not** check the `XSRF-TOKEN` at all — GET is exempt from CSRF validation
4. Response: 200

The stale token either passes the session check (some servers don't revalidate on every read) or the endpoint doesn't require authentication at all. Either way, there is no XSRF check to trip over.

---

## Why POST Fails With the Same Cookies

Same stale cookies, POST:

1. Server receives the request
2. Server checks `X-XSRF-TOKEN` header against the `XSRF-TOKEN` cookie value
3. Jar-polluted client sends: `XSRF-TOKEN=<stale_jar>; XSRF-TOKEN=<yours>` in the cookie, `X-XSRF-TOKEN: <yours>` in the header
4. Server reads first cookie match: `XSRF-TOKEN=<stale_jar>`
5. `<stale_jar>` ≠ `<yours>` (header value) → mismatch → **401**

> [!danger] The XSRF check compares header to cookie. Jar pollution puts the wrong cookie value first. The header carries your fresh value. They don't match. The server rejects.

---

## The Diagnostic Pattern

If you see a service where:
- GET calls to the same host succeed
- POST calls fail with 401 or 403
- Tokens are valid (you can verify with a fresh client or Postman)

The first thing to check is whether the shared HTTP client's jar has been polluted by a prior response. CSRF protection on POST is what makes the bug surface there and not on GET.

> [!tip] GET passing and POST failing with the same tokens is not a token validity problem — it is a delivery problem. Something is corrupting what actually reaches the server on the POST. Inspect the on-wire `Cookie` header.

---

## Edge Cases / When This Doesn't Apply

**Servers that don't rotate cookies:** If the upstream never sends `Set-Cookie` in its responses, the jar never accumulates anything and this bug cannot occur — GET and POST will both send exactly what you passed.

**Auth via `Authorization` header:** If the upstream uses `Bearer` tokens in the `Authorization` header instead of cookies, there is no CSRF check and no jar interaction. Header-based auth sidesteps this entire class of problem.

---

## Mental Model To Remember

> [!info] CSRF protection is applied to state-changing methods (POST, PUT, DELETE) and skipped for safe methods (GET). This asymmetry is why jar-polluted cookies pass silently on GET but get caught on POST — the XSRF header-to-cookie check only runs on the methods where forgery actually matters.
