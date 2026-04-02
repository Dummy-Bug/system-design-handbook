# Reliability & Redundancy — Overview

> Availability means the system is reachable. Reliability means it gives correct answers. These are different problems with different solutions.

> [!abstract] A system can be perfectly available and completely broken at the same time — returning wrong data, stale responses, or corrupt results. This folder covers reliability as a separate concern from availability, and introduces the key patterns and metrics (N+1, MTBF, MTTR, RTO, RPO) used to design and measure it.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Reliability.md | What reliability is, available-but-wrong examples, vs availability |
| 02-N+1-Redundancy.md | Always have one more than you need |
| 03-MTBF-and-MTTR.md | How often things break vs how fast you recover |
| 04-RTO-and-RPO.md | Maximum acceptable downtime vs maximum acceptable data loss |
| 05-Interview-Cheatsheet.md | How to use reliability concepts in a design interview |
