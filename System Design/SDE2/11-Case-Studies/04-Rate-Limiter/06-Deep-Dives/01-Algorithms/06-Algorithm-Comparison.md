
## Algorithm Comparison — When to Pick Which

Five algorithms, each solving a different problem. Here is how to think about the choice in an interview.

---

## The Evolution

Each algorithm exists because the previous one had a problem:

```
Fixed Window Counter
  → simple and fast
  → problem: 2× burst at window boundaries

Sliding Window Log
  → fixes boundary bug perfectly
  → problem: memory scales with limit size (unusable at high limits)

Sliding Window Counter
  → fixes memory problem with approximation
  → good enough for most production use cases
  → used by: Nginx, Cloudflare

Token Bucket
  → completely different model — allows controlled bursts
  → two knobs: capacity (burst) + refill rate (sustained)
  → used by: AWS API Gateway, Stripe

Leaky Bucket
  → zero burst — constant output rate
  → used when downstream can't handle spikes
  → used for: SMS gateways, external APIs with strict contracts
```

---

## Decision Table

| Situation | Algorithm |
|---|---|
| Simple API, small bursts acceptable | Fixed Window Counter |
| Sensitive endpoint, exact accuracy needed, low limit (≤10/min) | Sliding Window Log |
| General API rate limiting at scale | Sliding Window Counter |
| Bursty clients (mobile apps, webhooks, SDKs) | Token Bucket |
| Forwarding to downstream with strict rate contract | Leaky Bucket |

---

## Memory Comparison

```
Algorithm                Memory per user     Scales with limit?
─────────────────────────────────────────────────────────────
Fixed Window Counter     ~8 bytes            No
Sliding Window Log       limit × 58 bytes    Yes — unusable at high limits
Sliding Window Counter   ~16 bytes           No
Token Bucket             ~16 bytes           No
Leaky Bucket             ~16 bytes           No
```

Sliding Window Log is the only algorithm whose memory scales with the limit. Everything else is constant per user.

---

## Accuracy Comparison

```
Algorithm                Accuracy
──────────────────────────────────────────────────────────────
Fixed Window Counter     Allows up to 2× burst at window edges
Sliding Window Log       Perfect — true rolling window, no approximation
Sliding Window Counter   Approximate — assumes uniform distribution
Token Bucket             Exact — precise token accounting
Leaky Bucket             Exact — precise queue accounting
```

---

## What Production Systems Actually Use

**Nginx** — Sliding Window Counter (called "leaky bucket" in their docs, but the implementation is a sliding counter approximation)

**Cloudflare** — Sliding Window Counter for most rate limiting

**AWS API Gateway** — Token Bucket (burst limit + rate limit as two separate config parameters)

**Stripe** — Token Bucket (generous burst for webhook retries, strict sustained rate)

**Redis itself** — provides `redis-cell` module which implements Token Bucket natively

---

## Interview Answer

If an interviewer asks "which algorithm would you use?" — the honest answer is it depends on the endpoint:

```
Most API endpoints → Sliding Window Counter
  Simple, memory-efficient, good enough approximation

Sensitive endpoints (/login, /payment) → Sliding Window Log
  Low limit (5-10/min), perfect accuracy needed, memory cost acceptable

Bursty client APIs → Token Bucket
  Mobile SDKs, webhook delivery, client-initiated bursts are legitimate

Downstream protection → Leaky Bucket
  Forwarding to SMS gateway, external payment processor, hardware
```

> [!tip] Interview framing
> "For general API rate limiting I'd use Sliding Window Counter — it's what Nginx and Cloudflare use in production. Memory is fixed at two integers per user regardless of limit size, and the approximation error is acceptable for most endpoints. For sensitive endpoints like /login where even a small burst is exploitable, I'd use Sliding Window Log — the limit is low so memory cost is manageable and I need exact accuracy. For bursty clients like mobile SDKs, Token Bucket — two knobs let me allow startup bursts while capping sustained rate."
