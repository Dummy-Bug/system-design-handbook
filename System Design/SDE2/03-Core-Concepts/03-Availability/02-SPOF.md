# SPOF and Redundancy

> [!question] What's the single thing that can take your entire system down?
> That's your SPOF. And redundancy is the only way to eliminate it.

---

## SPOF — Single Point of Failure

A SPOF is any component in your system that, if it fails, takes the entire system down with it.

Examples:
- One server serving all traffic → server dies → system is down
- One database with no replica → DB crashes → all data is unreachable
- One load balancer → load balancer fails → no requests get through
- One datacenter → datacenter loses power → everything is gone

> [!danger] Every SPOF is a ticking clock
> It's not a question of *if* it will fail — it's *when*. Hardware fails. Networks go down. Power cuts happen. Design assuming failure is inevitable.

---

## The Answer to Every SPOF — Redundancy

The answer to every availability problem is the same single word: **redundancy**.

Remove every single point of failure by having a backup.

| SPOF | Redundancy solution |
|---|---|
| One server | Run two or more servers |
| One database | Replicate it — primary + replica |
| One datacenter | Deploy in multiple datacenters |
| One region | Deploy in multiple regions |
| One load balancer | Run two load balancers |

The pattern is always the same — if one fails, the other keeps serving.

---

## Redundancy alone isn't enough — you need Failover

Redundancy gives you a backup. Failover is the mechanism that **automatically switches to that backup when the primary fails**.

> [!warning] Manual failover is not good enough
> If your primary server dies at 3am and an engineer has to manually switch to the backup — you're down for however long it takes that engineer to wake up, log in, and fix it. That could be 30 minutes.
>
> At a 99.99% SLO you only have **4.32 minutes** of downtime allowed per month.
>
> Failover must be **automatic**.

---

## How automatic failover works

1. A **health check** continuously pings each server — *"are you alive?"*
2. If a server stops responding, it's marked as unhealthy
3. Traffic is automatically rerouted to healthy servers
4. An alert fires so engineers know to investigate

This happens in seconds — not minutes. No human needed.

---

## The cascading failure problem

Redundancy protects against one component failing. But what about this scenario:

Your primary DB fails → replica gets promoted → now you have only one DB again → that one fails too → system is down.

This is a **cascading failure** — one failure triggers another. Redundancy must be maintained continuously, not just set up once and forgotten.

> [!tip] Redundancy is not a one-time setup — it's an ongoing operational requirement
> The moment your backup becomes your primary, you need a new backup.
