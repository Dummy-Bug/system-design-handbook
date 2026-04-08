# Advanced Kafka: Scale and Correctness

> [!abstract] Up to now, we've treated Kafka as a high-speed highway. But in the real world, highways need maintenance (Retention) and lanes need strict traffic laws to prevent accidents (Exactly-Once). This section is about how Kafka moves from "fast messaging" to "guaranteed financial-grade storage."

---

## The two "Boss Levels" of Kafka

When you move from a simple hobby project to **Google-scale** ad clicking (100,000 events per second), you hit two massive walls:

1.  **The Storage Wall:** You are generating 3 Petabytes of data a year. You physically cannot buy enough hard drives to keep it all forever. You need a way to clean up without losing the "Source of Truth."
2.  **The Correctness Wall:** At 100k events/sec, network glitches happen every minute. If those glitches cause you to double-charge a customer even 0.1% of the time, you'll lose millions of dollars and all your users' trust.

---

## Files in this folder

| File | Topic |
|---|---|
| **01-Retention-and-Compaction.md** | How Kafka manages its own trash. The difference between "Delete by time" and "Keep the latest state." |
| **02-Exactly-Once-Processing.md** | The "Holy Grail." How we ensure a $10 charge happens exactly once, even if the server crashes mid-way. |
| **03-Interview-Cheatsheet.md** | Quick-reference patterns, trade-offs, and "Interview Framing" for revision. |

---

## The Mental Model Shift

In this section, we stop thinking about Kafka as a "Queue" and start thinking about it as a **Distributed Database**. 

We'll explore how a **Compacted Topic** allows us to get rid of our SQL Database entirely, and how **Transactions** allow us to link "Reading a Click" and "Updating a Balance" into one single, unbreakable handshake.

---

## What we are building towards

We are using our **Billing Service** as the ultimate test case. 
- It must handle 100k clicks/sec.
- It must NEVER charge a user twice.
- it must be able to restart from a total crash and "re-learn" every user's balance in seconds.

> [!tip] As you read these notes, always ask: "If I were the engineer at Google, which of these would I pick to save money on disks while keeping my Billing boss happy?"
