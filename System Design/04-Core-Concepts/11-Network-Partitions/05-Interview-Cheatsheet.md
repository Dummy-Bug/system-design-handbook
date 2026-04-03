# Interview Cheatsheet — Network Partitions

> [!question] When does partition come up in an interview?
> The moment you add a second node. Any distributed system will partition. The interviewer will ask "what happens during a network failure?" — this cheatsheet is your answer.

---

## The One-Line Definition

*"A network partition is when nodes are alive but can't communicate. Not a crash — both sides are running. The question is what each side does while isolated."*

---

## Moment 1 — "What happens if two nodes can't communicate?"

*"During a partition each isolated node must choose — serve potentially stale data or refuse requests entirely. For a payment system I'd refuse — wrong balance could cause financial loss. For a social feed I'd serve stale — slightly old content is better than an error page. This tradeoff is exactly what CAP theorem formalizes."*

---

## Moment 2 — "How do you prevent split-brain?"

*"Quorum — a node only acts as primary if it can reach a majority of nodes. With 3 nodes, quorum is 2. If a partition isolates 1 node from 2, the group of 1 steps down — can't reach quorum. The group of 2 maintains quorum and keeps serving. Only one primary at a time — no conflicting writes, no split-brain."*

---

## Moment 3 — "Why odd number of nodes?"

*"Even numbers create deadlock scenarios. With 4 nodes a 2-2 partition means neither group has quorum — both stop, entire system unavailable. With 3 or 5 nodes, one group always has a clear majority. Odd numbers guarantee one group always wins during any partition."*

---

## Moment 4 — "What's the difference between quorum and consensus?"

*"Quorum is just a number — the minimum nodes that must agree. R + W > N for read/write safety. Consensus is the full protocol — how leaders are elected, how writes are ordered, how split-brain is prevented. Consensus algorithms like Raft use quorum internally as one of their rules."*

---

## Serve vs Refuse Decision Table

| System | During Partition | Reason |
|---|---|---|
| Social feed, recommendations | Serve stale | Staleness harmless |
| Shopping cart | Serve stale | Availability > consistency |
| Bank balance | Refuse | Wrong balance = financial loss |
| Payment processing | Refuse | Double charge unacceptable |
| Hotel/seat booking | Refuse | Double booking = broken trust |
| Inventory | Refuse | Overselling = serious problem |

---

## Full Checklist

- [ ] Defined partition correctly — nodes alive, can't communicate (not a crash)
- [ ] Mentioned partitions are inevitable — not a design choice
- [ ] Explained the serve vs refuse decision — system-dependent
- [ ] Mentioned split-brain — two primaries, conflicting writes
- [ ] Explained quorum solution — majority must agree, minority steps down
- [ ] Justified odd number of nodes — even numbers can deadlock
- [ ] Distinguished quorum (number) from consensus (process)

---

## Quick Reference

```
Partition:
  Nodes alive, cannot communicate
  Inevitable in any distributed system
  Each node must: serve stale OR refuse

Split-brain:
  Both nodes think they're primary
  Both accept writes → conflicting data
  Fix: quorum — only majority group continues

Quorum:
  Formula: floor(N/2) + 1
  3 nodes → 2, 5 nodes → 3, 7 nodes → 4
  R + W > N → guaranteed to see latest write
  Always odd numbers → one group always wins

Quorum vs Consensus:
  Quorum    → minimum nodes that must agree (a number)
  Consensus → full protocol — Raft, Paxos (a process)
  Consensus uses quorum internally
```
