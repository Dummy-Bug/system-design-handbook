# Layer 4 Load Balancing — Overview

> Layer 4 is fast because it's blind — it sees IP addresses and ports, never what's inside the packet.

> [!abstract] Layer 4 load balancing operates at the Transport layer. It routes based on IP and port alone — no content inspection, no HTTP parsing. This makes it extremely fast but limited to scenarios where you don't need to differentiate requests by their content. This folder covers how L4 works from first principles, with full walkthroughs using Valorant and PostgreSQL as real examples.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Fundamentals.md | OSI model, what L4 sees vs can't see, port numbers, IANA |
| 02-How-It-Works.md | NAT, backend pool, TCP walkthrough, UDP walkthrough |
| 03-Connection-Tables.md | TCP 4-tuple table, UDP session table, TTL, DNS vs Valorant |
| 04-Real-World.md | Valorant, PgBouncer, Cloudflare DNS, Twitch, Goldman Sachs |
