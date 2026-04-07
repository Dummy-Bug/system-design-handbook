# Durability — Overview

> Data that isn't persisted isn't data — it's a promise waiting to be broken.

> [!abstract] Durability means data survives — crashes, power loss, disk failure, data center fires, and even your own bugs. This folder covers the four layers of durability, from a single server surviving a reboot to an entire region going offline without losing a byte.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Durability.md | What durability is, durability vs availability |
| 02-WAL.md | Write-Ahead Log — how databases survive crashes |
| 03-Replication.md | Copies across nodes, racks, and regions |
| 04-Backups.md | Full vs incremental, RPO connection, restore strategy |
| 05-Interview-Cheatsheet.md | The four layers, what to say, full checklist |
