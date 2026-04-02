# Layer 7 — Request Flow End to End

> [!question] You tap your Instagram profile. What actually happens between your phone and the server — and how does the system know you're logged in?
> Two complete walkthroughs — once with a plain L7 load balancer, once with an API Gateway.

---

## The Request

You open Instagram and tap your profile picture. The app fires:

```
GET /api/v1/user/profile HTTP/1.1
Host: api.instagram.com
Authorization: Bearer eyJhbGciOiJSUzI1NiJ9.eyJ1c2VySWQiOiI5ODc2NX0...
```

The `Authorization` header carries a **JWT (JSON Web Token)** — a signed token Instagram gave you when you logged in. It encodes your user ID and an expiry timestamp, cryptographically signed so it can't be forged.

---

## Flow 1 — Pure L7 Load Balancer

Auth validation happens inside the User Service itself.

```mermaid
sequenceDiagram
    participant App as Instagram App (192.168.1.50)
    participant LB as L7 Load Balancer (10.0.0.1:443)
    participant US as User Service B (10.0.0.5:8080)
    participant DB as Users DB

    App->>LB: HTTPS GET /api/v1/user/profile + JWT token (encrypted)
    Note over LB: Step 1: TLS handshake — decrypt HTTPS<br/>Step 2: Read URL → /api/v1/user/profile<br/>Step 3: Routing rule → User Service pool<br/>Step 4: Least connections → picks Server B<br/>Step 5: Forward plain HTTP to 10.0.0.5
    LB->>US: HTTP GET /api/v1/user/profile + JWT token (plain)
    Note over US: Step 6: Read Authorization header<br/>Step 7: Validate JWT signature<br/>Step 8: Check JWT expiry<br/>Invalid → return 401, stop here
    Note over US: Step 9: Decode JWT → userId = 98765
    US->>DB: SELECT * FROM users WHERE id = 98765
    DB->>US: User profile row
    US->>LB: 200 OK { name, bio, followers, posts... }
    LB->>App: 200 OK { profile data }
    Note over App: Profile renders ✓
```

**What happens if token is expired:**
```
User Service receives request
User Service decodes JWT → expiry: 2026-01-01 (past)
User Service returns 401 Unauthorized
L7 LB forwards 401 back to app
App shows "session expired, please log in"
```

---

### The Problem With This Architecture

Every single service validates the JWT itself:

```
User Service     → validates JWT on every request
Feed Service     → validates JWT on every request
Stories Service  → validates JWT on every request
Reels Service    → validates JWT on every request
Search Service   → validates JWT on every request
```

**What this means in practice:**
- JWT validation logic is copy-pasted across every service
- Instagram rotates signing keys every 90 days → update every service
- A bug in JWT validation exists in 20 places, not one
- Unauthenticated requests travel all the way to the service before being rejected — wasted compute

---

## Flow 2 — API Gateway Handles Auth

Auth validation moves to the gateway. Services never see the JWT.

```mermaid
sequenceDiagram
    participant App as Instagram App (192.168.1.50)
    participant GW as API Gateway (10.0.0.1:443)
    participant US as User Service B (10.0.0.5:8080)
    participant DB as Users DB

    App->>GW: HTTPS GET /api/v1/user/profile + JWT token (encrypted)
    Note over GW: Step 1: TLS handshake — decrypt HTTPS<br/>Step 2: Extract JWT from Authorization header<br/>Step 3: Validate JWT signature<br/>Step 4: Check JWT expiry<br/>Invalid → return 401 immediately<br/>Request NEVER reaches User Service
    Note over GW: Step 5: Decode JWT → userId = 98765<br/>Step 6: Attach internal header X-User-Id: 98765<br/>Step 7: Read URL → /api/v1/user/profile<br/>Step 8: Route to User Service pool → Server B
    GW->>US: HTTP GET /api/v1/user/profile + X-User-Id: 98765
    Note over US: Step 9: NO JWT validation<br/>Read X-User-Id: 98765 directly<br/>Gateway already verified — trust it
    US->>DB: SELECT * FROM users WHERE id = 98765
    DB->>US: User profile row
    US->>GW: 200 OK { profile data }
    GW->>App: 200 OK { profile data }
    Note over App: Profile renders ✓
```

**What happens if token is expired:**
```
API Gateway decodes JWT → expiry: 2026-01-01 (past)
API Gateway returns 401 immediately
Request never reaches User Service
Zero wasted compute on backend
```

---

## Side by Side Comparison

| Step | L7 LB only | API Gateway |
|---|---|---|
| TLS termination | ✓ at LB | ✓ at Gateway |
| JWT validation | ✗ — each service does it | ✓ — gateway does it once |
| Invalid token rejected at | Service (after routing) | Gateway (before routing) |
| userId passed to service | Via decoded JWT (service decodes itself) | Via `X-User-Id` header (pre-decoded) |
| Service complexity | High — must handle auth | Low — just fetch data |
| Auth logic duplication | Yes — every service | No — one place |

---

## The Trust Model — How Does the Service Know X-User-Id Wasn't Faked?

Critical question. What stops a malicious user from bypassing the gateway and sending:

```
GET /api/v1/user/profile
X-User-Id: 1              ← pretending to be user ID 1
```

**Answer: network isolation.**

The User Service lives in a **private network** — completely unreachable from the internet. Only the API Gateway can reach it. The firewall blocks all direct external connections.

```
Internet
    ↓
API Gateway (public-facing, 10.0.0.1)   ← only this is reachable from internet
    ↓  (private network)
User Service (10.0.0.5)                  ← internet cannot reach this
Feed Service (10.0.0.6)                  ← internet cannot reach this
Payment Service (10.0.0.7)              ← internet cannot reach this
```

If you try to hit `10.0.0.5:8080` directly from your phone — connection refused. Firewall blocks it.

So when User Service receives `X-User-Id: 98765`, it knows with certainty this came from the API Gateway — because nothing else can send requests to it. And the gateway only attaches that header after successful JWT validation.

> [!warning] This trust model only works if the private network is genuinely locked down
> If the User Service is accidentally exposed to the internet, the entire auth model collapses. Network isolation is the security guarantee — not the header itself.
