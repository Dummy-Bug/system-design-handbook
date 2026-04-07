# Consistency Models — Overview

> How stale is too stale? The answer depends entirely on what the data represents.

> [!abstract] In a distributed system with multiple nodes and replicas, every read might return slightly outdated data. Consistency models define the rules — how up-to-date a read must be, whether your own writes are visible to you, whether related operations appear in order. This folder covers the full spectrum from eventual to linearizable, and when each model is the right choice.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Consistency-Models.md | The full spectrum — eventual, read-your-writes, monotonic, causal, strong, linearizable |
| 02-When-To-Use.md | System → model decision table, real world examples |
| 03-Interview-Cheatsheet.md | What to say, the spectrum, full checklist |
