#httpx #http-client #cookies #shared-state #python #debugging

---

# Why Does a Shared httpx Client Send Stale Cookies Even When You Pass Fresh Ones?

> Prerequisite: [[http-client-as-browser]], [[csrf-get-vs-post]] — establish that the shared client has a cookie jar and why GET passes while POST fails.

Your shared `httpx.AsyncClient` is passing explicit cookies on every request. The GET succeeds. The POST gets a 401. You verify the tokens work in Postman. You update the tokens. Still 401. The cookies you passed are not the cookies reaching the server.

---

## The Setup

```python
# one shared client, created at server startup
client = httpx.AsyncClient()

# every adapter passes per-request cookies
response = await client.get(
    url,
    cookies={"SESSION": session_token, "XSRF-TOKEN": xsrf_token},
)

response = await client.post(
    url,
    cookies={"SESSION": session_token, "XSRF-TOKEN": xsrf_token},
)
```

The assumption: whatever you pass in `cookies=` is what gets sent. The GET works, so the tokens are valid. The POST should work identically.

---

## What httpx Does When You Pass `cookies=`

When httpx builds the outgoing `Cookie` header it does not use only what you passed. It **merges** two sources:

1. **Jar cookies first** — everything the client accumulated from prior `Set-Cookie` response headers
2. **Per-request cookies second** — what you passed in `cookies=`

If the jar has a `SESSION` cookie from a previous response, the merged header looks like:

```
Cookie: SESSION=<stale_jar>; XSRF-TOKEN=<stale_jar>; SESSION=<yours>; XSRF-TOKEN=<yours>
```

Four cookies. Two pairs. Stale jar leading.

> [!danger] Per-request cookies do not override the jar. They append after it. You cannot override the jar by passing `cookies=`.

---

## Why the Server Rejects It

RFC 6265 (the HTTP cookie spec): when a server receives multiple cookies with the same name, it uses the **first** match.

The server reads `SESSION=<stale_jar>` — the rotated token the upstream issued in its GET response — and rejects it. Your fresh token is sitting in second position, never read.

```mermaid
sequenceDiagram
    participant C as Shared Client
    participant J as Cookie Jar
    participant S as Upstream Service

    C->>S: GET /data (jar empty — only your tokens sent)
    S-->>J: Set-Cookie: SESSION=rotated; XSRF-TOKEN=rotated
    S-->>C: 200 OK

    C->>S: POST /action (jar prepended — stale tokens first)
    Note over S: SESSION=rotated → rejected (already rotated away)
    S-->>C: 401 Unauthorized
```

---

## How to Confirm It

Add temporary logging to inspect what httpx actually puts on the wire:

```python
response = await client.post(url, cookies=cookies)

# on-wire cookie header — what the server actually received
print(response.request.headers.get("cookie"))
```

If you see duplicate cookie names with different values, the jar is polluted.

---

## The Fix — Clear the Jar Before Every Request

```python
self.client.cookies.clear()

response = await self.client.post(url, cookies=cookies, ...)
```

With an empty jar, only your per-request cookies go on the wire:

```
Cookie: SESSION=<yours>; XSRF-TOKEN=<yours>
```

> [!success] Two cookies, not four. Server reads first match, gets your fresh token, accepts the request.

Place `cookies.clear()` in whatever shared wrapper every adapter passes through — not in each adapter individually. One location, every caller protected.

---

## Edge Cases / When This Doesn't Apply

**When you want accumulation:** If your flow is login → carry session forward automatically, the jar is doing its job. Don't clear it.

**`Authorization` header sidesteps this entirely:** The jar only manages `Cookie` / `Set-Cookie`. If the upstream accepts a `Bearer` token in the `Authorization` header, httpx never interferes with it.

**Per-request client (no sharing):** If you create a new `httpx.AsyncClient` per request (inside `async with`), the jar starts empty every time. No pollution possible — but you pay a connection handshake on every call.

---

## Mental Model To Remember

> [!info] `cookies=` in an httpx request is an addition, not a replacement. Jar cookies come first; your cookies come second; RFC 6265 gives the server the first match. For service-to-service calls with explicit per-request auth, `client.cookies.clear()` before every request is the fix — it empties the jar so your cookies are the only ones on the wire.
