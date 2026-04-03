# Authentication and JWT

## Authentication vs Authorization

> [!info] Two different checks. People mix them up constantly.

```
Authentication  → who are you?
                  happens once at login
                  "prove your identity"

Authorization   → what are you allowed to do?
                  happens on every request
                  "you're logged in, but can you delete this?"
```

---

## Why Not Just Use Passwords On Every Request

After login, the server can't ask for your password on every request. It needs a way to remember you're authenticated without re-verifying credentials every time.

Two approaches:

```
Session token  → server generates random string, stores in DB
                 client sends it on every request
                 server does DB lookup to verify
                 problem: 1M requests/sec = 1M DB lookups/sec

JWT            → server generates self-contained token, signs it cryptographically
                 client sends it on every request
                 server just verifies the signature — no DB lookup
                 scales horizontally with zero coordination
```

JWT wins at scale because it's stateless.

---

## JWT Internals

> [!info] A JWT is three base64-encoded parts separated by dots: `header.payload.signature`

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiIxMjMifQ.abc123xyz
      header                  payload             signature
```

**Header** — algorithm used:
```json
{ "alg": "HS256", "typ": "JWT" }
```

**Payload** — the actual data (never put passwords here — it's just base64, not encrypted):
```json
{ "userId": "123", "role": "user", "exp": 1712000000 }
```

**Signature** — tamper protection:
```
HMAC(header + payload, server_secret_key)
```

On every request, server recomputes the signature. If payload was tampered with, signature won't match → request rejected.

> [!important] JWT payload is readable by anyone — it's just base64 encoded, not encrypted. Never store sensitive data (passwords, secrets) in a JWT. The signature only proves it wasn't tampered with — it doesn't hide the contents.

---

## Access Token + Refresh Token Flow

> [!info] Short-lived access token for security. Long-lived refresh token for UX. Two tokens working together.

**Why two tokens?**

```
Problem: JWT cannot be revoked — server verifies by signature, no DB check
         If access token is stolen, attacker has access until it expires
Solution: keep access token short-lived (15 min) to limit damage window
          but don't make user log in every 15 min → use a refresh token
```

**The flow:**

```
1. User logs in
   → server generates: access token (JWT, 15min) + refresh token (random string, 30 days)
   → refresh token stored in DB (so it can be revoked)
   → both returned to client

2. Client uses access token on every API request
   Authorization: Bearer <access_token>

3. Access token expires → server returns 401 Unauthorized
   → client does NOT show login page
   → client calls POST /auth/refresh with refresh token
   → server checks DB: is refresh token valid? not expired? not revoked?
   → yes → generate new access token → return to client
   → client retries original request with new access token
   → user sees nothing, flow is seamless

4. Refresh token expires
   → /auth/refresh fails
   → client shows login page
   → user logs in again → new pair of tokens
```

**Logout:**
```
Delete refresh token from DB
→ next /auth/refresh call fails
→ user must log in again
→ access token still valid for up to 15min — acceptable, harmless
```

> [!important] Access token — stateless JWT, not in DB, cannot be revoked, keep it short-lived.
> Refresh token — stored in DB, can be revoked, long-lived, sent only to /auth/refresh.

---

## Cookies vs Bearer Token

> [!info] Two ways to send tokens. Different use cases.

```
Bearer token    → client manually attaches to every request header
                  Authorization: Bearer <access_token>
                  used by: mobile apps, API clients, SPAs
                  pro: works everywhere, full control
                  con: if XSS attack hits, JavaScript can read it via document.cookie

HttpOnly Cookie → browser automatically sends on every request
                  used by: web apps
                  pro: JavaScript cannot read it (document.cookie won't return it)
                       XSS attack cannot steal it
                  con: browser-only, doesn't work for mobile/API clients
```

**Best practice for web:**
```
Access token  → memory or localStorage (short-lived, acceptable risk)
Refresh token → HttpOnly cookie (long-lived, must be protected from XSS)
```

> [!tip] HttpOnly flag = JavaScript cannot access the cookie. Even if an XSS attack injects a script into your page, `document.cookie` won't return the HttpOnly cookie. Refresh token stays safe.

**CORS and cookies:**
```
CORS → browser mechanism preventing other websites from calling your API
       using your credentials
       evil.com cannot call bank.com on your behalf
       configured on server: "only accept requests from myapp.com"
       applies to browser only — not mobile or server-to-server calls
```
