# Distributed Caching — Overview

> [!abstract] A single cache node has two fundamental problems at scale: it runs out of memory, and it's a single point of failure. Distributed caching splits the cache across multiple nodes — but that introduces new problems: how do you route keys, keep replicas in sync, and handle node failures?

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Why-Single-Node-Fails.md | Memory limits and SPOF — why one node isn't enough |
| 02-Consistent-Hashing.md | Routing keys to nodes with minimal remapping on topology changes |
| 03-Cache-Coherence.md | Keeping replicas in sync — async vs sync, primary reads |
| 04-Replication.md | Read replicas for availability and throughput |
| 05-Two-Level-Caching.md | L1 local + L2 Redis — best of both worlds |
| 06-Node-Failure.md | What happens when a cache node goes down |
| 07-Interview-Cheatsheet.md | How to talk about distributed caching in a design round |
