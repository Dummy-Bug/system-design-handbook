
> [!info] Profile cache failure — preventing a DynamoDB cascade
> When the profile cache Redis goes down, every profile read misses and falls through to DynamoDB. Without protection, this creates a thundering herd on DynamoDB that could take it down too. Request coalescing prevents the cascade.

---

## The cascade risk

The profile cache Redis goes down. Every inbox load now needs to fetch 20 profiles from DynamoDB instead of Redis. At peak:

```
5,500 users/second opening inbox × 20 profiles = 110,000 profile reads/second
× 20% unique = 22,000 unique profile reads/second hitting DynamoDB
```

We showed earlier that 22,000 RPS is within DynamoDB's capacity during cold start. But the profile cache failure is worse than a cold start — it happens suddenly, with no warm-up period, potentially during peak traffic.

More critically: if multiple users open their inbox at the same moment and all need Charlie's profile, without coalescing that's thousands of identical DynamoDB reads for the same row simultaneously.

---

## Request coalescing — the singleflight pattern

Request coalescing ensures that for any given profile key, only one DynamoDB read is in-flight at any moment. All other requests for the same key wait for that one result.

```
10,000 inbox loads all need user:charlie → cache miss (Redis down)
→ Thread 1: no in-flight request for charlie → starts DynamoDB fetch
→ Threads 2-9999: in-flight request exists → attach to Thread 1's future
→ DynamoDB returns Charlie's profile
→ All 10,000 threads get the result simultaneously
→ Result: 1 DynamoDB read, not 10,000
```

**Implementation in Java using CompletableFuture:**

```java
ConcurrentHashMap<String, CompletableFuture<UserProfile>> inFlight 
    = new ConcurrentHashMap<>();

public CompletableFuture<UserProfile> getProfile(String userId) {
    // Check cache first
    UserProfile cached = redis.get("user:" + userId);
    if (cached != null) {
        return CompletableFuture.completedFuture(cached);
    }

    // Cache miss — coalesce in-flight requests
    return inFlight.computeIfAbsent(userId, key ->
        fetchFromDynamo(key)
            .whenComplete((result, ex) -> {
                inFlight.remove(key);
                if (result != null) {
                    redis.set("user:" + key, result); // re-cache if Redis recovers
                }
            })
    );
}
```

`computeIfAbsent` is atomic — only one thread creates the `CompletableFuture` for a given key. Every other thread calling `computeIfAbsent` with the same key gets back the existing future and waits on it.

---

## Why this is per app server, not distributed

The in-flight map lives in the app server's memory. It deduplicates requests within one server — not across all servers.

If you have 100 app servers, each one might independently send one request to DynamoDB for user:charlie. That's 100 reads instead of 10,000 — a 100x reduction, which is enough to keep DynamoDB safe.

A distributed coalescing layer (e.g. a shared cache in front of DynamoDB) would reduce it further to 1 read globally, but the per-server approach is simpler and sufficient at this scale.

---

## Circuit breaker as the last line of defence

If DynamoDB starts struggling despite coalescing — error rate rises above 1% — the circuit breaker opens. New profile reads fail fast, the app server returns a degraded response (inbox loads without profile names/avatars), and DynamoDB is protected from further load.

```
Profile cache down → coalescing limits DynamoDB reads → DynamoDB survives
If DynamoDB still struggles → circuit breaker opens → fail fast → DynamoDB protected
```

> [!tip] Interview framing
> "Profile cache failure triggers a cold start on DynamoDB. Request coalescing (singleflight pattern) means each unique profile generates at most one DynamoDB read per app server at any moment — reducing 10,000 simultaneous reads to ~100 across the fleet. If DynamoDB still struggles, the circuit breaker opens as a last resort."
