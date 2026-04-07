# State Machines — Overview

> An entity can be in exactly one state at a time. A state machine defines which states exist and which transitions between them are legal.

> [!abstract] State machines show up in 7+ system design case studies — Taxi, Hotel, Payment, Auction, Task Queue, Order, Chat. Every time you have an entity that moves through a lifecycle, you need a state machine. It prevents illegal transitions, solves concurrency for free via optimistic locking, and forces you to enumerate every edge case before designing the system.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-What-Is-A-State-Machine.md | States, transitions, the taxi example, connection to LLD State Pattern |
| 02-Implementing-In-Database.md | Status column, WHERE guard, state as version number, concurrency solved for free |
| 03-Timeout-Driven-Transitions.md | Background job vs lazy expiry, trade-offs, when each breaks |
| 04-Audit-Trail-vs-Overwrite.md | Overwrite vs append, doing both, atomic writes, transactions composing everything |
| 05-Interview-Cheatsheet.md | All real-world examples, what to draw, what to say, full checklist |
