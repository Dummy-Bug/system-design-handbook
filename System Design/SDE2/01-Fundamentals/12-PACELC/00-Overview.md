# PACELC Theorem — Overview

> CAP tells you what breaks during a failure. PACELC tells you what you're trading away even when everything is fine.

> [!abstract] CAP theorem only describes trade-offs during a network partition. But partitions are rare — your system runs normally 99.9% of the time. PACELC extends CAP by asking: during normal operation, what are you trading? The answer is always latency vs consistency. Every distributed system makes this trade-off on every single request, failure or not.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-PACELC-Theorem.md | The if-else breakdown, the four combinations, why PC/EL is nonsensical |
| 02-PA-EC-The-Middle-Ground.md | Why PA/EC exists, the pilot analogy, MongoDB, why most engineers avoid it |
| 03-System-Examples.md | DynamoDB, Cassandra, Zookeeper, Spanner, MongoDB — labels and reasoning |
| 04-Interview-Cheatsheet.md | Reference table, what to say out loud, traps to avoid |
