# Distributed Transactions — Overview

> [!info] The core problem
> ACID gives you atomicity within one database. But when a transaction spans multiple services, each with their own database, there is no single database to wrap a transaction around. This is the distributed transaction problem.

---

## Why this matters

Modern systems are built as microservices. A single user action — placing a Swiggy order — touches multiple services: Payment, Inventory, Order. Each service owns its own database. If Payment succeeds but Order fails, the user gets charged with no order. You need a way to make all steps either succeed or fail together — across service boundaries.

Two solutions exist:

- **2PC (Two-Phase Commit)** — tries to give true atomicity across multiple databases using a coordinator and locks
- **Saga pattern** — gives up on true atomicity, breaks the transaction into local steps with compensating transactions to undo failures

---

## Files in this folder

| File | What it covers |
|---|---|
| `01-The-Problem.md` | Why ACID doesn't work across multiple databases |
| `02-2PC-How-It-Works.md` | Two phases, coordinator, happy path |
| `03-2PC-Failures.md` | Coordinator crash, in-doubt transactions, blocking protocol |
| `04-Saga.md` | What Saga is, compensating transactions, idempotency |
| `05-Choreography.md` | Event-driven Saga, full Swiggy pipeline, failure scenarios |
| `06-Orchestration.md` | Central orchestrator, crash handling, DB persistence |
| `07-2PC-vs-Saga.md` | Full comparison, when to use which |
| `08-Interview-Cheatsheet.md` | Quick reference for revision |
