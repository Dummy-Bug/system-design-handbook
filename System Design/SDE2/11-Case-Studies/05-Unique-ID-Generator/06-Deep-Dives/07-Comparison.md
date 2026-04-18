# Approach Comparison

## The journey

Every approach we evaluated was an attempt to solve the same core problem: generate unique IDs across multiple servers without coordination. Each one fixed a previous problem but introduced a new one — until Snowflake solved them all.

```
Single server counter
  → works, but SPOF

Multiple servers with independent counters
  → SPOF fixed, but collisions

UUID
  → no coordination, no collisions, but not sortable + double storage + page splits

Ticket Server (Redis shared counter)
  → unique across servers, but Redis is a new SPOF + network hop per ID

Pre-Generated Key Pool (KGS)
  → no request-time coordination, crash-safe, but no embedded timestamp

Snowflake
  → unique, time-sortable, 64-bit, no coordination, no SPOF
```

---

## Full comparison table

| Property | Single Counter | UUID v4 | UUID v7 | Ticket Server | Key Pool (KGS) | Snowflake |
|---|---|---|---|---|---|---|
| Globally unique | ✅ | ✅ probabilistic | ✅ probabilistic | ✅ | ✅ | ✅ structural |
| Time-sortable | ⚠️ order only | ❌ | ✅ | ⚠️ order only | ⚠️ order only | ✅ |
| Embedded timestamp | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Storage | ✅ 8 bytes | ❌ 16 bytes | ❌ 16 bytes | ✅ 8 bytes | ✅ 8 bytes | ✅ 8 bytes |
| B+ tree performance | ✅ sequential | ❌ page splits | ✅ sequential | ✅ sequential | ✅ sequential | ✅ sequential |
| No SPOF | ❌ | ✅ | ✅ | ❌ Redis | ✅ | ✅ |
| No coordination at request time | ✅ | ✅ | ✅ | ❌ Redis call | ✅ in-memory | ✅ |
| Crash-safe | ❌ counter lost | ✅ | ✅ | ✅ | ⚠️ gaps on crash | ✅ |

---

## When to use what

**UUID v4** — when you need zero infrastructure, zero coordination, and don't care about sortability or storage. Quick prototypes, non-critical systems, systems where IDs are never used for ordering.

**UUID v7** — when you need zero coordination but also want time-sortability. Modern systems that can afford 16-byte IDs. A strong choice when you want simplicity without the page split problem.

**Ticket Server** — when simplicity matters more than availability. Small-scale internal systems where Redis downtime is acceptable or Redis is already highly available in your infrastructure.

**Pre-Generated Key Pool** — when you want coordination-free request serving and can tolerate gaps on crash. Works well for systems that pre-warm their key cache on startup.

**Snowflake** — when you need everything: uniqueness, time-sortability, 64-bit, no SPOF, no coordination at request time, and an embedded timestamp. The right choice for any large-scale system. Used by Twitter, Discord, Instagram, and most major platforms.

---

> [!tip] Interview framing
> In an interview, walk through the evolution — don't jump straight to Snowflake. Show that you understand why each simpler approach fails, and that Snowflake is the answer because it systematically eliminates every failure mode. That reasoning is what separates a strong answer from a name-drop.
