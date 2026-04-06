# Network Partitions — Overview

> Nodes don't always crash. Sometimes they just stop talking to each other. That's worse.

> [!abstract] A network partition is when nodes in a distributed system are alive but cannot communicate. Every distributed system will experience partitions — the question is not if, but when. This folder covers what partitions are, what happens during them, the split-brain problem, and how quorum prevents it.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Network-Partitions.md | What a partition is, partition vs crash, why inevitable |
| 02-During-Partition.md | The serve vs refuse decision — bridge to CAP theorem |
| 03-Split-Brain.md | Both nodes accept writes, conflicting data, quorum solution |
| 04-Quorum-vs-Consensus.md | Quorum as a number, consensus as a process |
| 05-Interview-Cheatsheet.md | What to say, checklist |
