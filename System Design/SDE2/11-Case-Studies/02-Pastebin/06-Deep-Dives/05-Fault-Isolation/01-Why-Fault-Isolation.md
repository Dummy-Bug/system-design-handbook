
> [!info] Fault isolation means failures in one part of the system cannot propagate to unrelated parts. The goal is to shrink the blast radius of any single failure.

---

## The monolith problem

In the base architecture, everything runs on one set of app servers. The read path and the write path live in the same process, deployed together, running on the same machines.

This creates **shared failure modes** — situations where one thing going wrong takes down something completely unrelated.

Consider a bad deployment to the write service. You push a bug that causes the paste creation handler to crash. In a monolith, that crash takes down the entire process — including the read handler. Users who just want to view a paste they already created cannot do so, because the write bug killed the whole server.

Or consider a memory leak in the write path. The paste creation handler accumulates memory under load. Eventually the process runs out of memory and the OS kills it. Reads go down with it — even though the read code itself had no bug.

```
Monolith failure:
  Bug in write handler → process crashes → reads also down
  Memory leak in write path → OOM → reads also down
  Bad write deployment → rollback required → reads also down during rollback
```

None of these failures have anything to do with the read path. But in a monolith, they take it down anyway.

---

## What fault isolation means

Fault isolation means drawing hard boundaries between parts of the system so failures cannot cross those boundaries.

The NFR for Pastebin is explicit: **if the write service goes down, reads must still work. If a read component crashes, writes must still work.**

To enforce this, the read path and write path must share no process, no machine, and no load balancer. They can share a database — that's acceptable, and we handle database failures separately. But everything above the database must be independent.

```
Without isolation:
  Write bug → everything down

With isolation:
  Write service down → read service completely unaffected
  Read replica down → write service completely unaffected
```

The blast radius of any single failure shrinks from "the whole system" to "one service."

---

> [!tip] Interview framing
> "In a monolith, a bug or crash in the write path takes down reads too — they share a process. Fault isolation means separating them completely: different services, different machines, different load balancers. A failure in one cannot cross into the other. The database is the one shared component — handled separately with standby nodes."
