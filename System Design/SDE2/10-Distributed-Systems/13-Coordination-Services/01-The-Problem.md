
> [!info] The core idea
> In a distributed system, multiple servers need to agree on shared state — who is the leader, what is the current config, which server owns a lock. Storing this in one of your own application servers creates a SPOF. You need a dedicated, reliable, single source of truth that all servers can read from and write to. That is what etcd provides.

---

## The coordination problem

You have 10 application servers all running together. A few questions immediately come up:

- Who is the leader right now?
- What is the current database host — which IP should everyone connect to?
- Only one server should run a specific background job at a time — how do you enforce that?

These are **coordination problems** — multiple servers need to agree on shared state. Getting this wrong means split brain, duplicate work, or config drift.

---

## Use case 1 — distributed configuration

Your database moves to a new host. IP changes from `10.0.0.5` to `10.0.0.8`.

All 10 application servers need to know the new address immediately.

**Naive approach — hardcode in config files:**

```
SSH into server 1  → update config → restart
SSH into server 2  → update config → restart
...
SSH into server 10 → update config → restart
```

During that rollout window, some servers are still pointing at the old IP. Requests fail. It takes time, it's error-prone, and you need to restart each server.

**Better approach — one central config store:**

```
Update config once in etcd:  /db/host = "10.0.0.8"
All 10 servers read from etcd → pick up the change immediately
No restarts needed
```

Every server watches the key in etcd. The moment it changes, all servers get notified and switch instantly. One update, zero downtime.

---

## Use case 2 — distributed locks

You have a background job — send digest emails every night at midnight. You have 10 servers. If all 10 run it simultaneously:

```
Server 1 sends digest email to user@gmail.com
Server 2 sends digest email to user@gmail.com
...
Server 10 sends digest email to user@gmail.com
→ user receives 10 copies of the same email
```

You need exactly one server to run it at a time. That server acquires a **distributed lock** — "I am the one running this job right now, everyone else back off."

```
Server 3 acquires lock → runs the job
Servers 1,2,4..10 see lock is held → skip
Server 3 finishes → releases lock
Next midnight → one server acquires it again
```

If Server 3 crashes mid-job, the lock must automatically expire — so another server can pick it up and finish the work. This automatic expiry is called a **TTL (time-to-live)** on the lock.

---

## Why not store this in your own application server?

The naive approach — pick one of your 10 servers as the "config server" and have everyone read from it.

This immediately reintroduces **SPOF**. If that server goes down:

- No one can read the current config
- No one can acquire or release locks
- Leader election has no arbiter

You've solved the coordination problem by creating a single point of failure — which is exactly what distributed systems are designed to avoid.

What you need is a **dedicated coordination service** that is itself highly available, strongly consistent, and fault-tolerant. That is etcd.
