
> [!info] Why per-server counters don't work
> The connection server sees every message — so counting messages per user on the connection server seems like the right fix. It isn't, because users can reconnect across servers.

---

## The per-server counter idea

Each connection server maintains an in-memory counter per connected user:

```
user_alice: 7 messages this second
user_bob:   2 messages this second
```

When Alice sends her 11th message, the server rejects it. Simple.

The problem: this counter only exists on the server Alice is currently connected to. If Alice disconnects and reconnects — even a second later — she lands on a different connection server. That server has no memory of her previous 10 messages. Her counter resets to 0.

---

## The bypass attack

With 500 connection servers, a malicious user can exploit this trivially:

```
Alice connects to server 1  → sends 9 messages → disconnects
Alice connects to server 2  → sends 9 messages → disconnects
Alice connects to server 3  → sends 9 messages → disconnects
...
Alice connects to server 500 → sends 9 messages

Total: 9 × 500 = 4,500 messages in under a minute
Rate limit: completely bypassed
```

The per-server counter enforces a limit per connection, not per user. Those are very different things.

> [!important] Rate limits must be per user, not per connection
> A user can have multiple connections across their lifetime (reconnects, multiple devices). The rate limit must be tracked at the user level — which means it needs to live somewhere all servers can see.
