# Layer 7 — Fundamentals

> [!question] All traffic arrives on port 443. L4 sees only TCP — it can't tell `/checkout` from `/recommendations`. How do you route to the right service?
> Layer 7 decrypts the request, reads what's inside, and routes based on the actual content.

---

## What L7 Does Differently

An L4 load balancer sees the envelope and forwards it. An L7 load balancer **opens the envelope, reads the letter, then decides where to send it.**

This costs more — decrypting HTTPS, parsing HTTP headers, making content-based decisions. But it enables everything L4 is blind to.

---

## SSL Termination — The First Step

Every HTTPS request is encrypted. The URL, headers, cookies — all unreadable until decrypted. Before L7 can route anything, it must decrypt the request first.

**Without SSL termination:**
```
Client ←HTTPS→ Server A  (Server A holds certificate, decrypts)
Client ←HTTPS→ Server B  (Server B holds certificate, decrypts)
Client ←HTTPS→ Server C  (Server C holds certificate, decrypts)
```

Every server manages its own certificate. Every server burns CPU on decryption. Certificate renewal happens on every server. One certificate expires → that server starts rejecting HTTPS.

**With SSL termination at L7:**
```
Client ←HTTPS→ L7 LB (holds certificate, decrypts once)
               L7 LB ←HTTP→ Server A
               L7 LB ←HTTP→ Server B
               L7 LB ←HTTP→ Server C
```

The L7 LB holds the certificate. It decrypts once. Backend servers receive plain HTTP — no certificates, no decryption overhead. Certificate renewed in one place.

> [!info] SSL termination is what makes L7 routing possible
> You cannot read an encrypted URL. The L7 LB must decrypt HTTPS first — only then can it see the path, headers, and cookies needed to make routing decisions.

---

## URL Path Based Routing

Once decrypted, the L7 LB reads the URL path and routes to the correct service pool:

```
GET  /api/recommendations  →  Recommendation Service (3 servers)
POST /api/checkout         →  Payment Service (2 servers)
GET  /api/user/profile     →  User Service (4 servers)
GET  /static/avatar.jpg    →  CDN / Static Asset Servers
```

All arriving on port 443. All decrypted. All routed correctly.

**Amazon example:**
```
GET  /products          →  Product Catalog Service
POST /cart              →  Cart Service
POST /checkout          →  Payment Service
GET  /reviews           →  Review Service
```

One domain. One entry point. Dozens of backend services. The L7 LB stitches it together invisibly. This is exactly what L4 cannot do — all these requests look identical to L4 (TCP on port 443).

---

## Header Based Routing

The L7 LB can route based on any HTTP header.

**Mobile vs Desktop:**
```
User-Agent: Mobile Safari  →  Mobile-optimised servers (lighter responses)
User-Agent: Chrome Desktop →  Desktop servers (full responses)
```

**API Versioning:**
```
Accept: application/vnd.api+json;version=2  →  v2 service (new)
Accept: application/vnd.api+json;version=1  →  v1 service (legacy, still running)
```

Both versions of the service run simultaneously. Clients that haven't upgraded continue hitting v1. New clients hit v2. No forced migration.

**Geographic routing:**
```
X-Country-Code: IN  →  India region servers  (lower latency for Indian users)
X-Country-Code: US  →  US region servers
```

---

## Cookie Based Routing — Canary Deployments

You've built a new version of the Payment Service. You don't want to deploy it to all users at once — what if it has a bug? You test it on 5% of traffic first.

**Without L7** — impossible. You'd have to deploy the new version to all servers or none.

**With L7 — canary deployment:**

```
Request with cookie: canary=true   →  Payment Service v2 (new — 5% of users)
Request without canary cookie      →  Payment Service v1 (stable — 95% of users)
```

You gradually increase — 5%, 10%, 25%, 50%, 100% — watching error rates at each step. Something breaks? Flip the routing rule back instantly. No redeploy, no downtime.

**A/B Testing works identically:**
```
Cookie: experiment=new_checkout  →  New checkout flow  (variant B)
No experiment cookie             →  Old checkout flow  (control)
```

Netflix runs hundreds of A/B tests simultaneously — every UI change, every algorithm experiment. All routed by the L7 LB reading experiment assignment cookies.

---

## How L7 Picks a Server Within a Service

L7 makes two decisions per request:

**Decision 1 — Which service?** (L7 intelligence — URL, headers, cookies)
**Decision 2 — Which server within that service?** (same algorithms as L4 — round robin, least connections)

```
GET /api/recommendations
        ↓
Decision 1: URL /api/recommendations → Recommendation Service pool
        ↓
Decision 2: Least connections → picks Server 2 of 3
        ↓
Forwards request to Server 2
```

---

## The Cost — Why You Don't Use L7 Everywhere

Every request through L7 requires:

```
1. TCP handshake with client
2. TLS handshake — decrypt HTTPS
3. Parse HTTP headers and URL
4. Make routing decision
5. Open new TCP connection to backend server
6. Forward plain HTTP request
```

vs L4 which does:

```
1. Table lookup
2. Forward packet
```

L7 adds **1–5ms of overhead** per request. For user-facing traffic hitting the edge once — acceptable. For internal microservice calls happening millions of times per second between services — unnecessary. Which is why production systems use L7 at the edge and L4 internally.

> [!warning] L7 overhead is per request, not per connection
> Every single HTTP request goes through the full decrypt → parse → route cycle. Unlike L4 which pays the connection table cost once per TCP connection and then just forwards packets.
