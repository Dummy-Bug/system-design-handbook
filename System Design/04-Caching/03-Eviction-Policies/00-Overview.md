# Cache Eviction Policies — Overview

> [!abstract] Cache has limited memory. When it fills up, something has to go. Eviction policies decide what. Choosing the wrong one means your most-used keys get evicted while rarely-used ones stay.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-LRU.md | Least Recently Used — the default, temporal locality |
| 02-LFU.md | Least Frequently Used — better for stable hot items |
| 03-FIFO-and-TTL.md | FIFO (rarely used) and TTL — time-based expiry |
| 04-Interview-Cheatsheet.md | Which policy to use and when |

---

> [!important] Eviction and TTL are two separate mechanisms
> **TTL** — time-based. Key deleted when its timer runs out, regardless of memory pressure.
> **Eviction** — memory-based. Triggered only when cache is full and needs space for a new key.
> Both can apply to the same key. Whichever fires first wins.
