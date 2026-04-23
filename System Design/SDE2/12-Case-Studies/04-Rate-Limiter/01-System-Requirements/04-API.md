## Who Calls This API

The rate limiter is not called by end users. It is called by the **API gateway** — the component that sits in front of all backend services and intercepts every incoming request.

The flow on every request:

```
User → API Gateway → Rate Limiter → [allow] → Backend Service
                                  → [block] → 429 returned immediately
```

The API gateway extracts the user ID and IP from the incoming request, calls the rate limiter, gets an allow/block decision, then either forwards the request or returns 429 to the user. The backend service never sees blocked requests.

---

## The Identifier Problem — Authenticated vs Unauthenticated

Rate limiting requires an identifier — something to count requests against. The natural identifier is `user_id`. But not every request comes from an authenticated user. An unauthenticated user hitting `/login` has no user ID.

The fallback is `ip_address`. Every request has an IP. If `user_id` is present, rate limit by user ID. If `user_id` is null (unauthenticated request), fall back to IP address.

> [!important] IP-based limiting has a known problem
> Corporate offices, universities, and mobile carrier NAT can put hundreds or thousands of users behind a single IP. Aggressively rate limiting by IP in these environments will block many legitimate users. For endpoints where unauthenticated access matters (like `/login`), IP-based limiting thresholds should be more generous than user-based ones. This is a known trade-off, not a solved problem.

The request body handles both cases in one model:

```json
{
  "user_id": "u_abc123",   // optional — null if unauthenticated
  "ip_address": "203.0.113.5",  // always present
  "endpoint": "/api/v1/login"   // always present
}
```

The rate limiter's logic: if `user_id` is populated, use it as the limiting key. If null, use `ip_address`. No flag needed — the presence or absence of `user_id` is the signal.

---

## GET vs POST — Why It Matters at 400K QPS

The first instinct is to use POST with a JSON body. POST is used for "doing something" — creating resources, triggering actions. A rate limit check is a read — you are checking state, not modifying it. GET is semantically correct.

But the performance argument is more important than the semantics.

**POST with body:** The HTTP client must serialize a JSON object, set `Content-Type: application/json`, and include the body in the request. The server must read the body, parse JSON, deserialize it. This happens 400,000 times per second. Even 0.1ms of extra serialization overhead per request adds up.

> [!info] What is an HTTP client?
> An HTTP client is the library or module that makes HTTP requests. When the API gateway calls the rate limiter, it uses an HTTP client — something like OkHttp in Java, axios in Node.js, or net/http in Go. It takes the URL, headers, and body, serializes everything into bytes, opens a TCP connection, and sends it. The HTTP client is the thing doing the serialization work on every call.

**GET with query parameters:** No body. Parameters go in the URL. Nearly zero serialization cost — query params are already plain strings, the HTTP client just appends them to the URL. No JSON marshaling, no object traversal.

```
GET /api/v1/rate_limit?user_id=u_abc123&ip=203.0.113.5&endpoint=/api/v1/login
```

**The math at 400K QPS:**

The way to think about this: one CPU core can do exactly 1 second of work per second. If the total work required exceeds that, you need more cores — or requests queue up and latency explodes.

```
POST overhead per request:
  JSON serialize {user_id, ip, endpoint}  → ~0.05ms
  Set Content-Type header                 → ~0.01ms
  Body parse on server side               → ~0.05ms
  Total                                   → ~0.1ms of CPU work per request

Total CPU work needed per second:
  400,000 requests × 0.1ms = 40,000ms = 40 seconds of CPU work
  But you only have 1 second of real time
  → You need 40 CPU cores just to handle serialization overhead

GET overhead per request:
  String concat into URL                  → ~0.001ms of CPU work per request

Total CPU work needed per second:
  400,000 requests × 0.001ms = 400ms = 0.4 seconds of CPU work
  → Less than 1 core handles it comfortably
```

Same 1 second of wall clock time. GET needs 0.4s of CPU work to serve it. POST needs 40s of CPU work to serve it. That's a 100x difference — 40 cores vs less than 1 core, just for the serialization step.

**The counterargument for POST:** Query parameters end up in server access logs, proxy logs, and CDN logs by default. `user_id` and `ip_address` in a URL means they get logged everywhere. POST body is not logged by default — better for privacy.

**Verdict:** In a high-performance internal service (API gateway → rate limiter is an internal call, not a public URL), GET with query params is the right choice. Privacy concern is minimal since these are internal service calls, not public URLs being cached or indexed. At 400K QPS, the performance advantage of GET is real.

---

## Final API

### Check Rate Limit

```
GET /api/v1/rate_limit
    ?user_id=u_abc123        (optional)
    &ip_address=203.0.113.5  (required)
    &endpoint=/api/v1/login  (required)
```

**Response — Allowed (200 OK):**
```json
{
  "accepted": true,
  "retry_after": 0
}
```

**Response — Blocked (429 Too Many Requests):**
```json
{
  "accepted": false,
  "retry_after": 30,
  "error": "rate limit exceeded"
}
```

`retry_after` is in seconds — how long the caller must wait before the current window resets and they can try again.

---

### Update Rules (Admin)

```
POST /api/v1/rules
Body:
{
  "endpoint": "/api/v1/login",
  "dimension": "per_user",
  "limit": 5,
  "window_seconds": 60
}
```

Rules are stored externally and hot-reloaded — no restart required. This endpoint is admin-only, not in the critical request path.

---

> [!tip] Interview framing
> "The rate limiter exposes a single GET endpoint called by the API gateway on every request. GET over POST because at 400K QPS the body serialization overhead of POST is real — parameters go in the query string since this is an internal call and never hits public logs. Request carries user_id (optional), ip_address (always present), and endpoint. If user_id is null we fall back to IP-based limiting. Response is either 200 accepted or 429 with a retry_after telling the client when to try again."
