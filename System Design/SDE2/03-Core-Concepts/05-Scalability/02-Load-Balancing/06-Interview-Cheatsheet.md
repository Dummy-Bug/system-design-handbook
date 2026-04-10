# Interview Cheatsheet — Load Balancing

> [!question] When does load balancing come up in an interview and what do you actually say?
> It comes up the moment you add a second server. The interviewer will ask how traffic gets distributed — and then follow up on algorithm choice, L4 vs L7, and how you handle the LB itself as a SPOF.

---

## Moment 1 — "You added more servers. How does traffic get distributed?"

This is the opening. Don't just say "load balancer." Walk through the decision:

*"I'd put a load balancer in front of the app servers. For a stateless REST API with uniform request durations, round robin is fine — it distributes evenly and has zero overhead. If request durations vary significantly (some endpoints are heavy, some are light), I'd switch to least connections so slower servers don't pile up. If users need session affinity — for example, a stateful WebSocket connection — I'd use IP hashing so the same client always hits the same server. But ideally the app is stateless and affinity isn't needed."*

---

## Moment 2 — "What layer is your load balancer?"

This is the follow-up. Know when to use each:

| Question | Answer |
|---|---|
| Is the protocol HTTP/HTTPS? | L7 |
| Do you need URL-based routing? | L7 |
| Do you need auth, rate limiting, JWT validation? | API Gateway (L7) |
| Is the protocol TCP but not HTTP? (DB connections, game servers) | L4 |
| Is the protocol UDP? (video streaming, real-time game state) | L4 |
| Maximum throughput, minimum latency, no HTTP parsing needed? | L4 |

*"For a typical REST API, I'd use an L7 load balancer — it can route by URL, inspect headers, and terminate SSL. For database connection pooling or a UDP game server, L4 is the right choice — it routes by IP and port only, no protocol parsing, much lower overhead."*

---

## Moment 3 — "Isn't the load balancer itself a single point of failure?"

Always address this proactively — shows you think about failure modes:

*"Yes — a single load balancer is a SPOF. The standard fix is active-passive with a floating IP. Two load balancers share a virtual IP — the active one owns it and handles all traffic. If it fails, a heartbeat detects it within seconds and the passive LB claims the floating IP. DNS still points to the same IP — clients see nothing. For cloud deployments, managed load balancers like AWS ALB handle this automatically."*

---

## Moment 4 — "Do you need an API Gateway?"

Know the difference:

*"An L7 load balancer distributes traffic. An API Gateway does that plus cross-cutting concerns — JWT authentication, rate limiting, request transformation, versioning, and analytics. If I have multiple microservices with different auth requirements, I'd put an API Gateway in front. Internal service-to-service traffic behind the gateway uses internal L4 load balancers — no need to re-authenticate on the private network."*

---

## The Algorithm Decision — One-Line Rules

| Algorithm | Use When |
|---|---|
| Round Robin | Stateless service, uniform request duration (default choice) |
| Weighted Round Robin | Servers have different capacities (some bigger, some smaller) |
| Least Connections | Request durations vary widely (some fast, some slow) |
| IP Hashing | Session affinity needed (WebSockets, stateful protocols) |

---

## The Three-Layer Architecture — Say This for Microservices

```
Internet
  ↓
L4 NLB (public-facing, handles TCP/UDP at scale)
  ↓
API Gateway cluster (auth, rate limiting, routing — itself scaled horizontally)
  ↓
Internal L4 LB per service (distributes within each microservice)
  ↓
Service instances
```

*"At the edge I'd use an L4 NLB — it handles raw TCP at massive scale, terminates nothing, just routes. Behind it, an API Gateway cluster handles auth and rate limiting once for all services. The gateway itself is a service — it scales horizontally behind the NLB. Inside the private network, each microservice gets its own internal load balancer distributing across its instances."*

---

## Health Checks — Always Mention Them

*"The load balancer runs health checks — HTTP GET /health every 5 seconds. Three consecutive failures removes the server from rotation. When it recovers, three consecutive successes add it back. Unhealthy servers receive zero traffic automatically — no manual intervention needed."*

---

## The Full Load Balancing Checklist

- [ ] Named the algorithm and justified the choice
- [ ] Stated whether L4 or L7 and why (protocol-driven decision)
- [ ] Mentioned API Gateway if the system has multiple microservices or auth requirements
- [ ] Addressed LB as SPOF — floating IP / active-passive / managed LB
- [ ] Mentioned health checks and automatic removal of unhealthy servers
- [ ] Confirmed app servers are stateless (if using round robin or least connections)
- [ ] For microservices: mentioned three-layer architecture

---

## Quick Reference

```
Algorithm choice:
  Default stateless API     → Round Robin
  Variable request duration → Least Connections
  Session affinity needed   → IP Hashing
  Mixed server sizes        → Weighted Round Robin

Layer choice:
  HTTP/HTTPS, URL routing, auth   → L7 / API Gateway
  TCP non-HTTP, UDP, raw protocol → L4

SPOF fix:
  Active-passive LB pair + floating IP
  OR managed LB (AWS ALB, GCP Load Balancer)

Health check:
  GET /health every 5s → 3 failures → remove
                       → 3 recoveries → add back

Three-layer (microservices):
  L4 NLB → API Gateway cluster → Internal L4 LB → instances
```
