# Security — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of authentication, JWT, encryption, rate limiting, and input validation. Every SDE candidate is expected to answer these confidently.

---

## Q1 — Authentication vs Authorization

> [!question] What is the difference between authentication and authorization?

> [!success]- Answer
>
> **Authentication — who are you?**
> Verifying the identity of the caller. Proving they are who they claim to be.
>
> ```
> User sends: username + password
> Server checks: does this password match the stored hash?
> If yes → identity confirmed → issue a token
>
> Other auth methods:
>   JWT token in header → verify signature → identity confirmed
>   OAuth2 → third-party (Google, GitHub) verifies identity
>   API key → pre-issued credential proves who you are
> ```
>
> **Authorization — what can you do?**
> Checking if an authenticated identity has permission to perform a specific action.
>
> ```
> User is authenticated as alice@example.com
>
> Can Alice read /api/orders/123?
>   → Is order 123 Alice's order? Yes → authorized ✓
>   → Is order 123 Bob's order? → unauthorized ✗ → 403 Forbidden
>
> Can Alice access /admin/users?
>   → Is Alice an admin? No → unauthorized ✗ → 403 Forbidden
> ```
>
> **Both are required on every request — in order:**
> ```
> Step 1: Authentication → verify identity (401 Unauthorized if fails)
> Step 2: Authorization  → verify permission (403 Forbidden if fails)
>
> Skipping step 1: attacker can forge any identity
> Skipping step 2: any user can access any resource
> ```
>
> > [!important] They're sequential, not interchangeable. Authentication first (who are you?), then authorization (what can you do?). A 401 means not authenticated. A 403 means authenticated but not permitted.
>
> > [!tip] Interview framing
> > *"Authentication is identity — verifying who the caller is. Authorization is permissions — verifying what that identity is allowed to do. Both are required on every request. 401 = not authenticated. 403 = authenticated but not authorized."*

---

## Q2 — How JWT Works

> [!question] How does a JWT token work? What's inside it and how does the server verify it without a database lookup?

> [!success]- Answer
>
> **JWT — JSON Web Token:**
> A token with three parts: header, payload, signature.
>
> ```
> Header.Payload.Signature
>
> Header:  { "alg": "HS256", "typ": "JWT" }     → algorithm used to sign
> Payload: { "user_id": 123, "exp": 1234567890 } → claims (who, when expires)
> Signature: HMAC_SHA256(header + payload, secret_key)
> ```
>
> **Why no database lookup:**
> ```
> Server has a secret key that only it knows.
>
> When issuing:
>   Sign the payload with the secret key → creates the signature
>
> When verifying:
>   Recalculate the signature using header + payload + secret key
>   Compare with the signature in the token
>   If they match → token is authentic, not tampered with → user_id is trusted
>
> No database needed — the signature IS the proof
> Attacker cannot forge a valid signature without the secret key
> ```
>
> **What JWT does NOT prevent:**
> ```
> Token theft → if stolen, attacker can use it until expiry
> Fix: short expiry (15 minutes) + refresh tokens
>
> Token revocation → can't "cancel" a JWT before it expires
> Fix: short expiry makes the window small
>      or: token blacklist (DB lookup, defeats the purpose of stateless)
> ```
>
> > [!tip] Interview framing
> > *"JWT is header.payload.signature. Server verifies by recomputing the signature with its secret key — no DB lookup needed. The payload carries user_id and expiry. Can't be forged without the secret. Can't be revoked before expiry — which is why access tokens should have short lifetimes (15 minutes) paired with revocable refresh tokens."*

---

## Q3 — Access Tokens and Refresh Tokens

> [!question] Why do JWTs have short expiry times? What is a refresh token and how does the pair work?

> [!success]- Answer
>
> **The problem with long-lived JWTs:**
> ```
> JWT cannot be revoked before expiry (stateless, no DB to invalidate)
>
> JWT stolen by attacker → attacker can use it for its full lifetime
>
> JWT valid for 30 days → attacker has 30 days of access
> JWT valid for 15 minutes → attacker has at most 15 minutes of access
> ```
>
> **The solution — two-token system:**
>
> ```
> Access token:  Short-lived JWT (15 minutes)
>                Used on every API request
>                Stateless — no DB lookup to verify
>                If stolen: expires in 15 minutes
>
> Refresh token: Long-lived opaque token (30 days)
>                Stored in database (can be revoked)
>                Used ONLY to get a new access token
>                Stored in HttpOnly cookie (JS can't read it)
>                If stolen: revoke it in DB immediately
> ```
>
> **The flow:**
> ```
> 1. User logs in → server issues access token (15min) + refresh token (30d)
> 2. User makes API calls → sends access token in Authorization header
> 3. Access token expires → client calls /auth/refresh with refresh token
> 4. Server checks refresh token in DB → valid → issues new access token
> 5. User logs out → refresh token deleted from DB → can't get new access tokens
> ```
>
> > [!important] The access token is for speed (stateless verification). The refresh token is for control (DB-backed, revocable). Short access token expiry limits the damage window if stolen.
>
> > [!tip] Interview framing
> > *"Short access tokens limit theft damage to 15 minutes — can't revoke JWTs but can minimize their window. Refresh tokens are long-lived but DB-backed and revocable. On logout, delete the refresh token — attacker can't refresh even if they have the old access token."*

---

## Q4 — SQL Injection

> [!question] What is SQL injection? Show me a vulnerable query and the fix.

> [!success]- Answer
>
> **SQL Injection:**
> When user input is concatenated directly into a SQL query, an attacker can inject SQL code to manipulate the query.
>
> **The vulnerable query:**
> ```java
> // User inputs: ' OR '1'='1
> String query = "SELECT * FROM users WHERE username = '" + username + "'";
>
> // Becomes:
> SELECT * FROM users WHERE username = '' OR '1'='1'
>
> '1'='1' is always true → returns ALL users
> ```
>
> **More dangerous variant:**
> ```
> // User inputs: '; DROP TABLE users; --
> SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
>
> First query: returns nothing
> Second query: drops the entire users table
> ```
>
> **The fix — parameterized queries:**
> ```java
> // Correct — parameter is escaped by the DB driver
> PreparedStatement stmt = conn.prepareStatement(
>     "SELECT * FROM users WHERE username = ?"
> );
> stmt.setString(1, username);
>
> // User inputs: ' OR '1'='1
> // DB treats it as a literal string, not SQL
> // Query looks for username literally equal to "' OR '1'='1"
> // Returns nothing — no injection ✓
> ```
>
> **The rule:** Never concatenate user input into SQL. Always use parameterized queries or an ORM that handles parameterization automatically.
>
> > [!important] SQL injection is consistently the #1 web vulnerability. The fix is parameterized queries — always. Never string-concatenate user input into SQL, even for "simple" cases.
>
> > [!tip] Interview framing
> > *"SQL injection is concatenating user input into queries — attacker sends SQL fragments as input, they execute. Fix: parameterized queries — the DB driver escapes the input as a literal string. Every ORM does this automatically. Never manually concatenate user input into SQL."*

---

## Q5 — Rate Limiting

> [!question] What is rate limiting? Where should it be enforced and what does it protect against?

> [!success]- Answer
>
> **Rate limiting:**
> Restricting how many requests a client can make to an endpoint within a given time window.
>
> ```
> Rule: max 5 login attempts per minute per IP
>
> Requests 1-5:  allowed → HTTP 200
> Request 6:     blocked → HTTP 429 Too Many Requests
> After 1 minute: counter resets
> ```
>
> **Where to enforce it:**
> ```
> API Gateway / Load Balancer — NOT at the application server
>
> Why at the gateway:
>   Blocked requests never reach app servers
>   App servers don't waste resources on abusive traffic
>   Centralized enforcement — all servers protected automatically
>   Attacker can't bypass by hitting a specific backend server directly
> ```
>
> **What it protects against:**
>
> | Attack | How rate limiting helps |
> |---|---|
> | Brute force password attack | Limit login attempts per IP → attacker can't try millions of passwords |
> | Credential stuffing | Limit auth requests → automated attacks slow to unviable |
> | API scraping | Limit reads per token → scraping entire dataset becomes impractical |
> | DDoS | Limit requests per IP → flood traffic absorbed before reaching servers |
>
> **Different rules for different endpoints:**
> ```
> /api/login         → 5 attempts/minute per IP (strictest)
> /api/search        → 100 requests/minute per user
> /api/feed          → 1000 requests/minute per user
> /api/public/*      → per IP limits (no auth yet)
> ```
>
> > [!tip] Interview framing
> > *"Rate limiting at the API gateway — blocked requests never reach servers. Login endpoint gets strictest limits (5/min per IP) to prevent brute force. Other endpoints per-user or per-IP. Protects against brute force, credential stuffing, scraping, and DDoS."*
