
> [!info] The service split is where fault isolation becomes concrete — two independent fleets with no shared process, machine, or load balancer.

---

## The split

The monolith becomes two services:

**pasteData service** — owns all write traffic
- Handles `POST /api/v1/pastes` (create)
- Handles `DELETE /api/v1/pastes/:shortCode` (delete)
- Writes to Postgres primary
- Writes content to S3

**viewData service** — owns all read traffic
- Handles `GET /api/v1/pastes/:shortCode` (read)
- Reads from Postgres (metadata check)
- Reads from Redis (cache hit) or S3 (cache miss)
- Returns content to client

These two services run on completely separate machine fleets. A crash, memory leak, or bad deployment on the pasteData fleet has no process or machine in common with the viewData fleet.

---

## Routing — API Gateway and Load Balancers

Two components sit above the services:

**API Gateway** — decides which service a request goes to, based on the HTTP method and path:

```
POST   /api/v1/pastes              → pasteData service
DELETE /api/v1/pastes/:shortCode   → pasteData service
GET    /api/v1/pastes/:shortCode   → viewData service
```

The API Gateway is a routing layer. It inspects the request and forwards it to the correct downstream fleet. It also handles auth token validation, rate limiting, and request logging in one place — so individual services don't need to implement these themselves.

**Load Balancers** — one per service, decides which instance within the fleet handles the request:

```
Client → API Gateway → LB (write) → pasteData instance 1
                                  → pasteData instance 2
                                  → pasteData instance 3

                     → LB (read)  → viewData instance 1
                                  → viewData instance 2
                                  → viewData instance 3
```

The API Gateway answers "which service?" The load balancer answers "which instance within that service?"

These are distinct responsibilities. If you collapse them into one component, a misconfiguration or crash in that single component takes down routing for both services — you've recreated a shared failure mode at the routing layer.

---

## How the paths fail independently

If the entire pasteData fleet goes down:

```
Client → API Gateway → LB (write) → pasteData fleet ← all instances down
                                                        LB returns 503 for writes

                     → LB (read)  → viewData fleet  ← completely unaffected
                                                        reads continue normally
```

Read traffic never touches the write fleet. The two paths share nothing above the database. viewData keeps serving reads without interruption — users can still view all existing pastes even while creation is broken.

---

## Independent scaling

The 100:1 read:write ratio means the two services have very different resource needs:

```
pasteData:  30 writes/sec peak  → 2–3 instances sufficient
viewData:   3,000 reads/sec peak → more instances, Redis in front
```

Because they're separate fleets, you scale them independently. You don't need to over-provision the write fleet to match the read fleet's size, or vice versa. Each fleet is right-sized for its own traffic.

---

> [!tip] Interview framing
> "Split into pasteData (writes) and viewData (reads) — separate machine fleets, separate load balancers. API Gateway routes by request type (POST/DELETE → pasteData, GET → viewData), load balancer picks the instance within each fleet. If pasteData crashes entirely, viewData is unaffected — no shared process, no shared machine, no shared LB. Independent scaling as a bonus: pasteData needs 2–3 instances, viewData needs more to handle 100× the traffic."
