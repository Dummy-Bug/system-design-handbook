
> [!info] The reconnect storm — 1M clients reconnecting simultaneously
> When server 7 dies, all 1M connected clients detect the broken connection at roughly the same moment and attempt to reconnect simultaneously. Without coordination, this creates a spike that can overwhelm the remaining connection servers and the registry Redis.

---

## The problem

Server 7 dies. The OS sends TCP RST to all 1M connected clients. All 1M clients detect the broken connection within milliseconds of each other. All 1M immediately try to reconnect.

```
T=0:    Server 7 dies
T=0.1:  1M TCP RSTs sent
T=0.2:  1M clients begin reconnect simultaneously
        → 1M WebSocket upgrade requests hit the LB
        → 1M auth validations
        → 1M registry writes queued to Kafka
```

This is a manufactured thundering herd. The remaining 499 connection servers, which were handling their normal load, now absorb a sudden 1M connection spike on top of existing traffic.

The first retry often fails too — servers are briefly overwhelmed. So all 1M clients retry. Again simultaneously. The spike repeats.

---

## The fix — exponential backoff with jitter

The client-side SDK does not retry immediately on disconnect. It waits a random amount of time before the first retry, and increases the wait on each subsequent failure.

```
Client detects disconnect
→ wait: random(0ms, 1000ms)    ← jitter spreads the initial spike
→ attempt reconnect
→ if fails: wait random(0ms, 2000ms)
→ attempt reconnect
→ if fails: wait random(0ms, 4000ms)
→ ...
→ cap at random(0ms, 30000ms)
```

The jitter is the critical part. Without jitter, exponential backoff still produces synchronized retries — all clients back off for 1 second, then all retry at exactly T+1s. With jitter, each client picks a random point in the backoff window. 1M clients spread their reconnects across the full window instead of spiking at one moment.

```
Without jitter:
T=0:   1M clients disconnect
T=1:   1M clients retry simultaneously → spike
T=3:   1M clients retry simultaneously → spike
T=7:   1M clients retry simultaneously → spike

With jitter:
T=0:   1M clients disconnect
T=0 to T=1:   1M clients reconnect gradually → smooth ramp
Most succeed on first attempt, no second spike
```

---

## Why this is a client-side fix

The server cannot coordinate reconnects — it's dead. The load balancer can't stagger incoming connections — it just routes what arrives. The fix has to be in the client SDK, which controls when the reconnect attempt happens.

This is the same principle as TTL jitter in caching — randomisation prevents synchronised behaviour at scale.

> [!important] Jitter appears in multiple places in this system
> TTL expiry jitter (caching), reconnect jitter (fault isolation), and registry write spreading (peak traffic) all use the same underlying principle: randomisation breaks synchronisation at scale.

> [!tip] Interview framing
> "All 1M clients reconnect simultaneously — that's a manufactured thundering herd. The fix is exponential backoff with jitter on the client SDK. Each client picks a random point in the backoff window before retrying, spreading 1M reconnects across several seconds instead of spiking them all at once."
