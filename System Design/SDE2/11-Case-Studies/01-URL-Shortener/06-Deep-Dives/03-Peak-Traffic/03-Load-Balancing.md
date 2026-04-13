
> [!info] Distributing 1M requests/sec
> Hot key problem solved. DB replicas handle cache misses. But 1M requests/sec still need to reach the right app server. You need something in front of your app server fleet to distribute traffic — and that something is an API Gateway.

---

## Why API Gateway now and not in base architecture

In base architecture, there was one app server. An API Gateway in front of one server adds complexity with zero benefit — it's just an extra hop.

At peak traffic with a fleet of app servers, the picture changes completely. You need:
- Traffic distributed across app servers
- TLS terminated at the edge (not on every app server)
- Rate limiting to protect against abuse
- A single entry point for all clients

Now API Gateway earns its place.

---

## What API Gateway does

**Load balancing** — distributes incoming requests across the app server fleet. Round-robin, least connections, or consistent hashing based on client IP.

```
1M requests/sec → API Gateway → spread across 20 app servers → 50k each
```

**TLS termination** — the SSL/TLS handshake is CPU-intensive. Doing it on every app server wastes compute that should be spent on application logic. The API Gateway handles all TLS, forwards plain HTTP to app servers internally.

```
Client → HTTPS → API Gateway (TLS terminated here)
API Gateway → HTTP → App servers (plain, no TLS overhead)
```

**Rate limiting** — protects the system from a single client sending millions of requests. Especially important for the creation endpoint — you don't want one user creating millions of short URLs and filling up the DB.

```
Per IP: max 100 URL creations/minute
Per IP: max 1000 redirects/minute
```

**Single entry point** — clients always talk to one address. The internal fleet can scale up and down without clients needing to know.

---

## Auto-scaling the app server fleet

At 1M requests/sec peak and ~50k requests/sec per app server, you need ~20 app servers at peak. But traffic spikes are sudden — you need auto-scaling to provision servers before the spike overwhelms the existing fleet.

```
Metric: CPU usage or requests/sec per server
Threshold: scale out when average CPU > 70%
Scale out: add N servers, API Gateway starts routing to them
Scale in: remove servers when load drops, after a cooldown period
```

Cloud providers (AWS Auto Scaling, GCP Managed Instance Groups) handle this automatically. The API Gateway detects new servers via health checks and starts sending traffic.

---

> [!tip] Interview framing
> "API Gateway is introduced at scale — not base architecture. It gives load balancing across the app server fleet, TLS termination at the edge, and rate limiting. With auto-scaling, the fleet grows during spikes and shrinks when traffic drops. The Gateway is the single entry point — internal fleet topology is invisible to clients."
