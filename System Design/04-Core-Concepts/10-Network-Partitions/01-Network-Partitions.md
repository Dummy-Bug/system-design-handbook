# Network Partitions

## What a Partition Is

> [!info] A network partition = two or more nodes in a distributed system are alive and running, but cannot communicate with each other.

**The classic scenario:**

```
Node A — Mumbai data center
Node B — Singapore data center

Undersea cable cut by a ship's anchor

Node A: running perfectly, serving Mumbai users
Node B: running perfectly, serving Singapore users
But: Node A and Node B cannot talk to each other
```

Both nodes are healthy. The network between them is not.

---

## Partition vs Crash — Critical Distinction

> [!important] These are completely different problems requiring different handling

```
Server crash:
  Node goes down → stops responding
  Health check fails → detected quickly
  Fix: failover to another node

Network partition:
  Both nodes alive and running
  Neither can reach the other
  Each thinks the other might be dead
  Fix: much harder — you don't know if the other node is dead or just unreachable
```

**Why partition is harder:**

During a crash — you know the node is gone. During a partition — you don't know if:
- The other node is dead
- The network between you is down
- You are the one isolated

You can't tell from inside the partition.

---

## Why Partitions Are Inevitable

> [!warning] Every distributed system will experience partitions. This is not a maybe — it is a certainty at scale.

Common causes:

```
Physical:
  Undersea cable cut (happens multiple times per year globally)
  Power outage in one data center
  Router failure between data centers

Software:
  Network misconfiguration
  Firewall rule change
  DNS failure

Operational:
  Data center maintenance
  Cloud provider outage (AWS us-east-1 taking down half the internet)
  BGP routing issues
```

At large scale — Netflix, Google, Amazon — partitions happen multiple times per week. The system must be designed to handle them, not avoid them.

---

## What a Partition Looks Like

```
Normal operation:
  Node A ←──────────────→ Node B
  (constant replication, heartbeats, coordination)

During partition:
  Node A ✗──────────────✗ Node B
  (all communication lost)
  
  Node A: "Is Node B dead? Or is the network down?"
  Node B: "Is Node A dead? Or is the network down?"
  Neither knows.

After partition heals:
  Node A ←──────────────→ Node B
  (communication restored, must reconcile diverged state)
```

---

## The Fundamental Problem

During a partition, each isolated node must make a decision for every incoming request:

```
User request arrives at Node B (Singapore)
Node B cannot reach Node A (Mumbai)
Node B doesn't know if its data is fresh

Option 1: Serve the request  → might return stale data
Option 2: Refuse the request → user gets an error
```

This decision — serve or refuse — is the heart of the CAP theorem. Covered in the next file.
