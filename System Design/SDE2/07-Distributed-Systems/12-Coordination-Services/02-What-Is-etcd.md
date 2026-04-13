
> [!info] The core idea
> etcd is a distributed key-value store built specifically for coordination data — config, leader identity, locks. The name comes from Unix's `/etc` directory (where system config lives) + `d` for distributed. Under the hood it runs Raft, so every write requires quorum and every read is guaranteed fresh. It is the single source of truth for your entire distributed system.

---

## The name

**etcd = distributed `/etc`**

On a Linux machine, `/etc` is where all system configuration files live — `/etc/hosts`, `/etc/nginx/nginx.conf`, `/etc/passwd`. It is the single source of truth for how that machine is configured.

etcd does the same thing — but for your entire distributed system. Instead of one machine reading from `/etc`, hundreds of servers read from etcd.

---

## What etcd actually is

etcd is a key-value store. That is it. You store a key, you read a key.

```
/db/primary      → "10.0.0.6"
/db/replicas     → ["10.0.0.7", "10.0.0.9"]
/leader          → "server-3"
/locks/job       → "server-5"
```

Exactly like Redis in structure. But etcd makes three guarantees that Redis does not:

**1. Strongly consistent — no stale reads ever**

Every read returns the latest confirmed write. If Server 3 wrote `/leader = server-3`, every other server reading `/leader` gets `server-3` — never an old value. This is non-negotiable for coordination data. A stale leader read causes split brain.

**2. Highly available — no SPOF**

etcd runs as a cluster of 3 or 5 nodes using Raft internally. Every write must be acknowledged by a quorum before it is confirmed. If one node dies, the cluster keeps working.

```
3-node etcd → quorum = 2 → tolerates 1 failure
5-node etcd → quorum = 3 → tolerates 2 failures
```

Always odd numbers — even numbers cannot form a clear majority.

**3. Watch — push notifications**

Any server can watch a key and get notified the instant it changes. No polling needed.

```
Server 1 watches /db/primary
→ failover automation updates /db/primary to "10.0.0.6"
→ etcd instantly pushes notification to Server 1
→ Server 1 switches to new primary immediately
→ zero downtime, zero human intervention
```

---

## etcd is CP in CAP

etcd explicitly chooses consistency over availability. If quorum is lost — say 2 out of 3 nodes go down — etcd stops accepting writes entirely rather than risk returning inconsistent data.

For coordination data this is the right trade-off. A stale config or a stale leader value is far more dangerous than a temporary write outage.

---

## The biggest user — Kubernetes

Every single piece of Kubernetes state lives in etcd:

```
/registry/pods/default/my-pod     → pod definition
/registry/services/default/my-svc → service definition
/registry/nodes/node-1            → node health status
```

The Kubernetes API server is essentially a thin layer on top of etcd. If etcd goes down — the entire control plane stops. You cannot deploy, scale, or modify anything. Existing workloads keep running but nothing new can happen.

This is why production Kubernetes always runs etcd as a 5-node cluster with regular backups. It is the most critical component in the entire system.
