
> [!info] Centralised rate limiting via Redis INCR
> A Redis counter per user, shared across all connection servers, enforces the rate limit correctly regardless of which server the user is on or how many times they reconnect.

---

## The solution

Every connection server, before forwarding a message, increments a shared Redis counter for that user:

```
Key:   rate:<user_id>
Value: message count in current second
TTL:   1 second (auto-resets every second)
```

The flow on every incoming message:

```
Alice sends a message
→ Connection server: INCR rate:user_alice
→ If result > 10: reject message
→ If result ≤ 10: forward message to app server
```

On the first message of a new second, the key doesn't exist — Redis creates it with value 1 and sets TTL to 1 second. At the end of the second, the key expires automatically. The counter resets with no cleanup needed.

---

## Why INCR is the right operation

Redis INCR is atomic. Two connection servers can INCR the same key simultaneously and Redis guarantees they each get a unique, correct result. There's no race condition, no double-counting.

```
Server 3: INCR rate:user_alice → returns 8
Server 7: INCR rate:user_alice → returns 9   (Alice reconnected mid-second)
Server 7: INCR rate:user_alice → returns 10
Server 7: INCR rate:user_alice → returns 11 → REJECT
```

All servers are looking at the same counter. Reconnecting doesn't help.

---

## Key design

```
Key:    rate:<user_id>
Value:  integer (incremented per message)
TTL:    1 second
Limit:  10 messages/second for 1:1 messaging
```

The Redis call adds ~1ms latency per message. At 10 messages/second per user this is negligible.

> [!tip] Interview framing
> "Rate limiting lives on the connection server. On every incoming message, we INCR a Redis key for that user with a 1-second TTL. If the count exceeds the limit, we reject the message. The atomic INCR means all 500 connection servers share one counter per user — reconnecting doesn't bypass it."
