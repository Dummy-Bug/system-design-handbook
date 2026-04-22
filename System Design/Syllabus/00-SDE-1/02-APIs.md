# APIs

## REST Fundamentals
- What REST is (not a protocol, a style)
- Core constraints — stateless, uniform interface, client-server
- URL design (resources, not actions — /users not /getUsers)
- HTTP methods in REST context (GET = read, POST = create, PUT/PATCH = update, DELETE)
- Request and response format (JSON)
- Status codes in REST context

## API Design
- Versioning — URL-based (/v1/) vs header-based, why versioning exists
- Pagination — offset-based vs cursor-based, when and why cursor wins
- Filtering and sorting
- Error response structure — consistent error format (code, message, details)
- Idempotency — what it means, why it matters for APIs
- Idempotency keys — client sends unique ID per operation, server deduplicates. Essential for payment, booking, any mutation that must not double-execute.

## gRPC (Awareness Level)
- What gRPC is — remote procedure call framework, uses Protocol Buffers not JSON
- Why it's faster than REST for internal services (binary encoding, HTTP/2 multiplexing)
- When to prefer gRPC — internal service-to-service. REST for public-facing APIs.
- You don't need to know the 4 streaming modes at SDE-1

## Async API Pattern
- Problem: some operations take too long to wait for (image processing, report generation)
- Pattern: return 202 Accepted with a job ID, client polls GET /jobs/{id} for status
- Alternative: webhook — caller provides a callback URL, server calls it when done
- When to use: any operation that takes more than a few seconds

## Webhooks
- What a webhook is — a push-based callback. External service calls YOUR endpoint when an event happens.
- Opposite of polling — instead of asking "any updates?", the source tells you immediately
- Example: Stripe fires POST /your-server/webhook when a payment completes
- Security: verify webhook signature (HMAC) so you know it's from the real source
- Your handler must be idempotent — same event can arrive twice

## Authentication in APIs
- API keys — long-lived, for service-to-service, passed in header
- Basic auth — how it works, why not to use in production
- Token-based auth — access tokens, how they're passed (Authorization: Bearer)
- JWT basics — what it contains, how it's verified, what it's not (not encrypted by default)

## Rate Limiting (Consumer Perspective)
- What rate limiting is and why APIs enforce it
- How rate limit headers work (X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After)
- How to handle 429 responses gracefully (back off, retry after the window)
