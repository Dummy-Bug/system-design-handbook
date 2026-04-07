# Concurrency & Locking — Overview

> Two users. Same data. Same moment. Only one can win cleanly.

> [!abstract] The moment two requests touch the same data simultaneously, you have a concurrency problem. This folder covers how to detect it, prevent it, and design systems that handle simultaneous access correctly — from single database rows to distributed operations across multiple servers.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Race-Conditions.md | What goes wrong when two operations interfere |
| 02-Pessimistic-Locking.md | Lock first, act second — deadlocks and prevention |
| 03-Optimistic-Locking.md | Act first, verify after — version numbers and CAS |
| 04-Read-Write-Locks.md | Multiple readers, single writer |
| 05-MVCC.md | Snapshot isolation — readers never block writers |
| 06-Distributed-Locking.md | Redis locks across multiple servers |
| 07-Idempotency.md | Safe retries — idempotency keys across service hops |
| 08-Interview-Cheatsheet.md | Decision framework, what to say, full checklist |
