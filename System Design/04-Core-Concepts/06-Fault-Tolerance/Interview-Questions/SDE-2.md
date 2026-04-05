# Fault Tolerance — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around cascading failures, circuit breakers, retry strategies, and blast radius containment. Expected at SDE-2 level.

---

## Q1 — Cascading Failure Prevention

> [!question] Your checkout service calls 4 downstream services: inventory, payments, notifications, and fraud detection. The fraud detection service is slow. Walk me through how this causes a cascading failure and how you prevent it.

> [!success]- Answer
>
> **How the cascade happens:**
> ```
> Fraud detection is slow (3 seconds instead of 200ms)
>
> Each checkout request: thread blocks for 3 seconds waiting for fraud response
>
> At 100 req/s: 100 threads per second × 3 seconds blocked = 300 threads occupied
> Thread pool: 200 threads → fully exhausted
>
> Now:
>   New checkout request arrives → no thread available → queued
>   Queue fills → requests start failing
>   Checkout goes down
>
> Users can't checkout → payments, inventory, notifications also idle
>   → Entire checkout flow is down because of fraud detection being slow
> ```
>
> **Prevention — two independent tools:**
>
> **1. Timeout (immediate fix):**
> ```
> Set timeout on fraud detection call: 500ms
>
> Fraud service slow → after 500ms → TimeoutException → thread freed
> Checkout continues with fraud = "unknown" → use fallback policy
>   (allow low-value orders, flag high-value for manual review)
>
> Thread exhaustion prevented ✓
> ```
>
> **2. Circuit breaker (sustained failure protection):**
> ```
> After 10 consecutive timeouts → circuit OPENS
>
> While OPEN:
>   Fraud check fails immediately (no actual call made)
>   Thread freed in microseconds
>   Use fallback policy for all orders
>
> After 30 seconds → HALF-OPEN:
>   One test request to fraud service
>   Success → circuit CLOSES, normal operation
>   Failure → stays OPEN
> ```
>
> **3. Bulkhead (blast radius containment):**
> ```
> Fraud detection thread pool: 10 threads (isolated from checkout pool)
> Checkout main thread pool: 100 threads
>
> Fraud slow → exhausts its own 10 threads → doesn't touch the 100
> Other downstream calls (payments, inventory) completely unaffected ✓
> ```
>
> > [!tip] Interview framing
> > *"Slow service is more dangerous than crashed service — it causes thread exhaustion without anyone noticing. Three defenses: timeout (free threads fast), circuit breaker (stop calling when clearly broken), bulkhead (isolate the damage to its own thread pool). All three together contain the blast radius."*

---

## Q2 — Retry Strategy Design

> [!question] Design a retry strategy for a payment service calling an external payment processor (like Stripe). What parameters do you choose and why?

> [!success]- Answer
>
> **The requirements:**
> ```
> Must not double-charge (non-idempotent call)
> Must handle transient network failures (brief blips)
> Must not overwhelm Stripe during their incident
> Must not hang indefinitely
> ```
>
> **The strategy:**
>
> **1. Idempotency key — make retries safe:**
> ```
> Before calling Stripe:
>   Generate idempotency_key = UUID (e.g. "order-abc123-payment-attempt-1")
>   Store it with the order
>
> Every retry: send SAME idempotency_key
>
> Stripe behaviour:
>   First call: processes charge, stores key → responds with result
>   Retry call: sees key already exists → returns original response, no new charge
>
> Makes payment call idempotent ✓
> ```
>
> **2. Distinguish retryable vs non-retryable errors:**
> ```
> Retryable (transient):
>   502 Bad Gateway  → Stripe's infra blip, likely resolves
>   503 Service Unavailable → temporary overload
>   Network timeout  → didn't reach Stripe at all
>
> Non-retryable (permanent):
>   400 Bad Request  → malformed data, retry won't fix it
>   402 Card Declined → card refused, retry won't help customer
>   401 Unauthorized → wrong API key, retry pointless
>
> Don't retry on 4xx — just fail fast with appropriate error message
> ```
>
> **3. Exponential backoff + jitter:**
> ```
> Attempt 1: immediately
> Attempt 2: wait 1 second + random 0-500ms jitter
> Attempt 3: wait 2 seconds + random 0-500ms jitter
> Attempt 4: wait 4 seconds + random 0-500ms jitter
> Max retries: 3 (after that, return error to user)
>
> Jitter: prevents thundering herd if many orders fail simultaneously
>          all retrying at exactly the same intervals
> ```
>
> **4. Dead letter queue for unresolvable failures:**
> ```
> After max retries: don't lose the payment intent
>   → Move to dead letter queue
>   → Alert operations team
>   → Manual retry after Stripe recovers
> ```
>
> > [!tip] Interview framing
> > *"Idempotency key first — makes retries safe by preventing double charges. Only retry on 5xx and timeouts (transient), never on 4xx (permanent errors). Exponential backoff with jitter prevents retry storms. Max 3 retries, then dead letter queue for manual recovery."*

---

## Q3 — Bulkhead Pattern Design

> [!question] Your user-facing API calls both a critical product service and a non-critical recommendation service. How do you ensure a recommendation service overload doesn't affect product service calls?

> [!success]- Answer
>
> **The problem without bulkheads:**
> ```
> Shared thread pool: 200 threads total
>
> Recommendation service becomes slow (Black Friday traffic, bug, etc.)
> Recommendation calls: 100 concurrent requests × 3s each = 300 threads needed
> Thread pool exhausted: 200/200 threads occupied
>
> Product service requests arrive: no threads available → queued → timeout
> Users can't see products → checkout impossible
>
> Non-critical service (recommendations) took down critical service (products) ✗
> ```
>
> **The fix — bulkhead: separate thread pools per downstream:**
> ```
> Product service thread pool:        150 threads
> Recommendation service thread pool: 30 threads
> Other services:                     20 threads
>
> Recommendation service overloaded:
>   → exhausts its own 30 threads
>   → Product service pool: 150 threads untouched ✓
>   → Product calls continue normally
>
> Recommendation requests queue up or fail → circuit breaker opens
> → No impact on product calls
> ```
>
> **Combined with circuit breaker:**
> ```
> Recommendation bulkhead pool full:
>   New recommendation request → rejected immediately (no waiting)
>   Circuit breaker counts rejections
>   N rejections → circuit OPENS
>   All recommendation requests return fallback immediately
>   Product calls: 100% unaffected ✓
> ```
>
> **Where to implement:**
> ```
> Application-level (Resilience4j, Hystrix):
>   Per-service thread pools in the JVM
>   Precise control, per-service configuration
>
> Infrastructure-level:
>   Separate container/pod per downstream service call type
>   Kubernetes resource limits isolate CPU/memory
> ```
>
> > [!tip] Interview framing
> > *"Bulkhead gives each downstream service its own thread pool. Recommendation pool exhaustion cannot touch the product pool. Critical services are structurally protected from non-critical ones. Pair with circuit breaker: once the bulkhead is full, fail fast instead of queuing — no backup pressure."*

---

## Q4 — Idempotency Implementation

> [!question] You need to make a "create order" endpoint idempotent so client retries don't create duplicate orders. Design the implementation.

> [!success]- Answer
>
> **The requirement:**
> ```
> POST /orders called multiple times with same intent → only one order created
> Client can safely retry on timeout without worrying about duplicates
> ```
>
> **The implementation:**
>
> **Step 1 — Client generates a unique key:**
> ```
> Client: before calling POST /orders, generate UUID
>         idempotency_key = UUID.randomUUID()  // e.g. "f47ac10b-58cc-4372-a567"
>         Store it locally with the in-progress order
>
>         Request: POST /orders
>                  Headers: Idempotency-Key: f47ac10b-58cc-4372-a567
>                  Body: { items: [...], total: 50.00 }
> ```
>
> **Step 2 — Server checks key before processing:**
> ```
> Server receives request:
>   1. Check DB: SELECT * FROM idempotency_keys WHERE key = 'f47ac10b...'
>   2. If found: return the original stored response (no new order created)
>   3. If not found: process the order, then store:
>        INSERT INTO idempotency_keys (key, response, created_at)
>        VALUES ('f47ac10b...', '{order_id: 789, status: created}', NOW())
> ```
>
> **The race condition — two requests arrive simultaneously with same key:**
> ```
> Use DB unique constraint on key column:
>   INSERT INTO idempotency_keys ...
>   → if second INSERT with same key: UNIQUE CONSTRAINT VIOLATION
>   → catch exception → retry the SELECT → return the stored response
>
> DB constraint guarantees only one "create" succeeds ✓
> ```
>
> **TTL on keys:**
> ```
> Idempotency keys are only needed for the retry window
>   → 24 hours is typically sufficient
>   → Scheduled job: DELETE FROM idempotency_keys WHERE created_at < NOW() - 24h
>   → Prevents table growing indefinitely
> ```
>
> **What to store as the response:**
> ```
> Store the full HTTP response (status code + body)
> On retry: return exactly the same response
> Client cannot tell if it's a real response or a cached one — same behaviour
> ```
>
> > [!tip] Interview framing
> > *"Client generates UUID before calling. Server checks key in DB first — if found, return stored response. If not found, process + store response atomically. DB unique constraint prevents race condition where two simultaneous retries both pass the check. Keys expire after 24 hours."*

---

## Q5 — Graceful Degradation Under Load

> [!question] Your social platform is running at 95% capacity. Traffic is still growing. Before you can scale, you need to protect the core experience. Design a graceful degradation plan.

> [!success]- Answer
>
> **The goal:**
> Protect the most valuable user experience while shedding non-essential load.
>
> **Step 1 — Classify features by criticality:**
> ```
> Tier 1 — Never degrade (core product):
>   View feed (main feature)
>   Post content
>   Like / comment
>   User login / auth
>
> Tier 2 — Degrade gracefully:
>   Personalised recommendations → show trending/popular instead
>   Real-time notifications → delay, batch send every 5 minutes
>   Search autocomplete → disable, search still works without suggestions
>
> Tier 3 — Turn off entirely:
>   Analytics event logging → drop events during overload
>   Non-critical background jobs → pause
>   Email digests → queue, send when capacity recovers
>   Social graph suggestions ("People you may know") → disable
> ```
>
> **Step 2 — Feature flags for instant control:**
> ```
> All Tier 2 and Tier 3 features behind feature flags
> At 90% capacity: auto-disable Tier 3
> At 95% capacity: auto-disable Tier 2 (show fallback content)
> Engineer can also flip manually during incident
> ```
>
> **Step 3 — Load shedding at the gateway:**
> ```
> At 95%+ CPU:
>   Reject low-priority requests with 503 (not 500)
>   Priority order: authenticated > anonymous, Tier 1 > Tier 2
>
>   Anonymous feed requests: return cached static version
>   Logged-in feed: always serve (even from slightly stale cache)
> ```
>
> **Step 4 — Communication:**
> ```
> Status page: "We're experiencing high traffic. Some features temporarily limited."
> In-app banner: "Recommendations temporarily unavailable — showing trending content"
> Don't let users discover degradation silently
> ```
>
> > [!tip] Interview framing
> > *"Classify features into tiers before the incident. Tier 1 never goes down. Tier 2 degrades to a cheaper fallback. Tier 3 turns off entirely. Feature flags give instant control. Load shed anonymous or non-critical requests at the gateway. Communicate degradation explicitly — users tolerate known limitations better than silent failures."*
