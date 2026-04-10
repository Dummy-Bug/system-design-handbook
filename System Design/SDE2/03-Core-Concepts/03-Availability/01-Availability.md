# Availability

> [!question] Your system is running. But can users actually use it?
> That's availability. Not whether your servers are on — whether the entire path from user to response is working.

---

## What it is

You open WhatsApp to send a message. It shows **"Connecting..."** and never connects.

The servers are running. The code is deployed. But you can't use it. That experience — the system being unreachable or non-functional when a user tries to use it — is what availability measures.

**Availability = what percentage of the time is your system actually usable?**

```
Availability = Uptime / (Uptime + Downtime)
```

Example — system was down for 1 hour in a 30 day month:
```
Total time   = 30 × 24 = 720 hours
Uptime       = 719 hours
Availability = 719 / 720 = 99.86%
```

---

## What causes unavailability

| Cause | Example |
|---|---|
| **Node failure** | A server crashes or loses power |
| **Traffic overload** | Too many requests, threads exhausted, requests rejected — 503 |
| **Deployments** | Engineer pushes new code, server restarts, brief window of no service |
| **Network partition** | Servers are fine but the network between them or to users goes down |
| **Dependency failure** | Your code is fine but a service you depend on goes down (Stripe, AWS S3) |

> [!warning] Availability is not just "is my server on or off"
> It's whether the **entire path from user to response** is working.
> Any single point in that path failing = unavailability.

---

## Why it matters in system design

Every system design interview will ask about availability either directly or indirectly.

- *"What happens if this server goes down?"* — availability question
- *"How do you handle failures?"* — availability question
- *"What's your SLO?"* — availability question

It connects directly to what you've already learned:
- **SLO** — your availability target (99.9%, 99.99%)
- **Error Budget** — how much downtime you're allowed
- **Latency** — a system that's too slow is effectively unavailable to the user
