
> [!info] Availability is not "are the nodes alive?" — it's "did the user's request succeed?"
> In a 1,200-node cluster, gossip will tell you every node is alive. Meanwhile, a network partition is causing quorum failures and clients are getting 503s. Node liveness and service availability are different things.

---

## The gossip heartbeat trap

With our gossip protocol, every node knows which other nodes are alive. The instinct is to define availability as "percentage of nodes that are up." If 1,198 out of 1,200 nodes are alive, that's 99.83% — sounds fine.

But consider this:

```
1,198 out of 1,200 nodes are alive ✓
Gossip says everything is healthy ✓

But: the 2 dead nodes held the only replicas for 500 key ranges
  → any request for those key ranges fails with 503
  → 2% of all client requests are failing

Node availability: 99.83%
Request availability: 98%  ← this is what the client experiences
```

Node-level health doesn't translate to request-level health. The SLI must measure **what clients actually experience** — did their request succeed or not?

---

## The availability SLI formula

```
Availability = successful requests / total requests
```

Every node (acting as coordinator) keeps two counters:
- `total_requests` — incremented on every incoming client request
- `successful_requests` — incremented when the response is 2xx

These counters are tracked per operation type, because failure modes differ:

```
Read counters:   total_reads, successful_reads
Write counters:  total_writes, successful_writes
Delete counters: total_deletes, successful_deletes
```

The metrics collector scrapes all counters from all 1,200 nodes, sums them up, and computes the ratio.

---

## What counts as a success for the KV store

This is trickier than a simple web app, because our KV store has different consistency levels and different failure modes:

### Reads

```
GET /api/v1/item?key=user:123

→ 200 OK (value found)              ✓ success
→ 404 Not Found (key doesn't exist) ✓ success  (system worked correctly)
→ 200 OK (expired key, returns 404) ✓ success  (TTL check worked correctly)
→ 503 quorum not met                ✗ failure  (couldn't reach enough replicas)
→ 500 internal error                ✗ failure  (system broke)
→ timeout                           ✗ failure  (client got nothing)
```

404 is a success — the system looked up the key, didn't find it (or found it expired), and returned the correct response. The system worked as designed.

503 "quorum not met" is a failure — the client asked for strong consistency (R=2) but the coordinator could only reach 1 replica. The system couldn't fulfill the request.

### Writes

```
PUT /api/v1/item

→ 201 Created                       ✓ success
→ 503 quorum not met                ✗ failure  (couldn't get W=2 acks)
→ 500 internal error                ✗ failure  (system broke)
→ timeout                           ✗ failure  (client got nothing)
→ 429 rate limited                  ? depends  (see below)
```

### The rate limiting question

When a node rate-limits a request (429 Too Many Requests), is that a success or a failure?

It depends on perspective. The system **chose** to reject the request to protect itself — that's working as designed. But the client didn't get their data — from their perspective, the service failed.

Most teams count 429s as **failures against the availability SLI** because availability is measured from the client's perspective. If rate limiting is happening frequently enough to breach SLO, it means you need more capacity — not that the system is "correctly rejecting."

```
Conservative (client perspective):  429 = failure → counts against availability
Lenient (system perspective):       429 = success → system protected itself

Most teams: count 429 as failure. If your rate limiter fires often enough to
breach SLO, you're under-provisioned.
```

---

## Concrete example with our numbers

At peak: 300K reads/sec and 30K writes/sec = 330K total requests/sec. During a network partition affecting one rack, 500 key ranges lose quorum. Requests for those ranges fail with 503.

```
Total requests in one second: 330,000
Failed requests (503s):       350  (requests hitting partitioned key ranges)
Successful requests:          329,650

Availability SLI = 329,650 / 330,000 = 99.894%
```

Our SLO is 99.99%. We're at 99.894% — **breaching SLO**. Even though 1,198 out of 1,200 nodes are alive, the partition caused enough quorum failures to breach. This is why you measure requests, not nodes.

---

## Availability by consistency level

An important nuance: eventual consistency reads (R=1) and strong consistency reads (R=2) have different availability characteristics. During a partition, EC reads might succeed while SC reads fail:

```
During a partition affecting Node D:

EC read for key on B, C, D:
  R=1 → coordinator picks Node B → success ✓

SC read for same key:
  R=2 → coordinator contacts B, C, D → D unreachable → only B and C respond
  → R=2 met → success ✓

SC read when B and D are both down:
  R=2 → only C responds → quorum not met → 503 failure ✗
```

Tracking availability separately by consistency level helps debug:

```
Overall availability:  99.95%  ← below SLO
EC read availability:  99.99%  ← meeting SLO
SC read availability:  99.88%  ← dragging down the average
Write availability:    99.97%  ← close to SLO

Diagnosis: SC reads are the problem — some replica sets have 2 out of 3
nodes unreachable, so R=2 quorum can't be met.
```

---

> [!tip] Interview framing
> "Availability SLI is successful requests divided by total requests — measured on real client traffic, not gossip heartbeats. Each coordinator tracks total and successful request counters, scraped by Prometheus every 15 seconds. 2xx and 404 are successes — the system worked correctly. 503 quorum failures, 500 errors, and timeouts are failures. We track availability separately for EC reads, SC reads, and writes because they have different failure modes — during a partition, EC reads might be fine while SC reads are breaching SLO. 429 rate-limited requests count as failures because availability is measured from the client's perspective."
