
> [!info] The fallback — offline delivery covers the registration gap
> Between the moment Alice connects and the moment her registry write completes, she is connected but invisible to the routing layer. Any message sent to her during this window needs a fallback.

---

## The gap

Alice connects at midnight. Her registry write is queued in Kafka. It will be processed in the next few seconds. Meanwhile, Bob sends Alice "Happy New Year."

The app server looks up Alice's registry entry. It's not there yet. Without a fallback, the message is dropped or returns an error.

---

## The fallback — treat her as offline

The offline delivery system we already designed handles exactly this case. When the registry lookup misses, the app server treats the user as offline and writes the message to `pending_deliveries`.

```
Bob sends Alice "Happy New Year" at 00:00:01
→ App server: HGET registry user:alice
→ Miss (registry write still in queue)
→ Write to pending_deliveries (treat Alice as offline)

2 seconds later:
→ Registry worker processes Alice's connect event
→ HSET registry user:alice conn_server_7
→ Delivery worker picks up pending message
→ Routes to conn_server_7
→ Alice receives "Happy New Year"
```

Alice gets the message 2-3 seconds late. On New Year's midnight, this is completely acceptable — nobody notices a 2-second delay in a "Happy New Year" message.

---

## Why this works cleanly

The offline delivery system was designed for the case where a user is genuinely offline. It happens to solve the connection storm registration gap for free — the gap looks identical to a brief offline period from the routing layer's perspective.

No special-casing needed. The existing fallback absorbs the delay window naturally.

> [!important] The two systems compose perfectly
> Offline delivery + async registry writes = connection storm handled. The user is connected and live. The routing layer catches up within seconds. Any messages in the gap land in pending_deliveries and are delivered promptly once the registry is updated.

> [!tip] Interview framing
> "Registry writes are async via Kafka, so there's a brief window where the user is connected but not yet registered. The fallback is the offline delivery system — a registry miss is treated as offline, message goes to pending_deliveries, delivered once the registry catches up. 2-3 second delay at worst."
