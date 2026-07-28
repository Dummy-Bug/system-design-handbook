---
track: B — Concurrency & Infra
salesforce: #1 most-likely LLD (see [[00 Loop Notes]], [[01 Problem Lists]])
status: in progress — deriving
---

> [!abstract] Thread-Safe LRU Cache
> Track B (concurrency) · Salesforce #1-frequency LLD · Patterns: Strategy (eviction seam, later)
> Build cold single-threaded first, then the *"now make it thread-safe"* escalation.

---

## 📄 Problem Statement

Design an in-memory cache with a **fixed capacity**. When it fills up, evict the **least recently
used** entry to make room. Both read and write must be fast regardless of size.

Given thin, on purpose (Salesforce style) — the requirements below were extracted by asking
clarifying questions, not handed over.

---

## ✅ Functional Requirements

1. **Two operations, both O(1):**
   - `get(key)` → value, or null if absent. Counts as a *use*.
   - `put(key, value)` → insert or update. Counts as a *use*. Evicts the LRU entry if over capacity.
2. **Generic** — key and value are any type (`K`, `V`).
3. **Fixed capacity `N`** — a maximum **entry count**, fixed at construction (`new LRUCache(3)`).
   *Assumption announced, not asked:* capacity is in entries, not bytes.
4. **LRU eviction** — on a `put` that overflows, the least-recently-used entry is removed.
   Eviction policy is a **named seam**, not a runtime-config system (see judgment call).
5. **Single-threaded first** — thread-safety is the escalation, handled after the core works.

### Out of scope (v1 — announce, don't build)

TTL / expiry · persistence or write-behind · byte/memory-based capacity · distribution (multi-node) ·
multiple live-selectable policies.

---

## 🧠 Judgment Calls

> [!tip] Eviction policy is a seam, not a v1 Strategy — and it's not a `pickVictim()` function
> Building runtime-selectable eviction before a second policy exists is YAGNI (same lesson as the
> Parking Lot allocation strategy — extract on the *second* caller). Build **LRU concretely** first.
> **The deeper point:** eviction policy is not a clean Strategy, because the policy *dictates the
> data structure* and must update on **every access in O(1)**. LRU needs a doubly-linked list; LFU
> needs frequency buckets + min-freq pointer; FIFO needs a queue. So the real seam is a policy that
> is **notified** and owns its own bookkeeping — not one that picks a victim on demand:
> ```java
> interface EvictionPolicy<K> {
>     void recordAccess(K key);   // every get + put
>     void recordInsert(K key);
>     K evictCandidate();         // O(1) — the policy already knows
> }
> ```
> Extract this when LFU arrives, not now. Naming *this* (vs "I'll add an EvictionStrategy") is the
> hire → strong-hire difference on this problem.

> [!note] `LinkedHashMap` is the production answer — say so, then hand-build
> Java's `LinkedHashMap(accessOrder=true)` + `removeEldestEntry()` gives LRU almost for free. The senior move: *"in production I'd use `LinkedHashMap`; I'll hand-build the HashMap + DLL to show I know the mechanics."* Knowing the shortcut and choosing the demonstration scores.

---

## 🔩 Why a plain HashMap isn't enough (motivates the structure)

`HashMap<K,V>` already gives O(1) `get` and `put` — but it stores **no recency order**. To do LRU
you'd have to stamp each entry with a last-access time, and then eviction = scan all N entries for
the minimum → **O(n) per eviction**, breaking FR1.

So the lookup structure (HashMap) needs a partner that maintains **recency order with O(1)
updates**. → *derivation continues below.*

---

## 🧱 Classes
*(to derive)*

## 📐 Build Scope
*(to derive)*

## 🔍 Post-Build
*(to derive)*
