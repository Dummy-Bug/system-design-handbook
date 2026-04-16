
> [!info] Backpressure — what happens when the system is overwhelmed
> Auto-scaling is not instant. In the gap between a traffic spike and new machines coming online, the system needs a way to stay alive without collapsing.

---

## The scenario

New Year's midnight. 500M users open WhatsApp. Messages flood in. Your app servers are at 95% CPU. DynamoDB writes are queuing up. The system is struggling.

You trigger auto-scaling. New app servers will be ready in 2-3 minutes.

What happens in those 2-3 minutes?

Without any protection, requests keep arriving faster than the app servers can process them. Threads pile up waiting for DynamoDB. Memory fills. The app server runs out of resources and crashes. Now you have fewer servers, not more — the spike just got worse.

This is a cascade failure. The system doesn't degrade gracefully — it collapses.

---

## The solution — controlled degradation

Backpressure is the system's way of saying "slow down" to whoever is upstream. Instead of trying to process everything and dying, the system processes what it can and rejects the rest.

The key insight is that a slow, partially available system is far better than a crashed system. A user who gets "message failed, retry in 1 second" recovers immediately when load drops. A user whose app server is down gets nothing.

```
Without backpressure:
spike → app server overwhelmed → crash → all users affected

With backpressure:
spike → app server at capacity → rejects excess → 10% of users retry
       → auto-scaling kicks in after 2-3 min → full capacity restored
       → all users back to normal
```

> [!important] Degraded is better than dead
> The goal of backpressure is not to handle everything — it's to handle as much as possible while staying alive long enough for auto-scaling to kick in.
