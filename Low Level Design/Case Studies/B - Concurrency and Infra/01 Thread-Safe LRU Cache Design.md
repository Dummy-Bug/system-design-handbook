---
track: B — Concurrency & Infra
salesforce: #1 most-likely LLD (see [[00 Loop Notes]], [[01 Problem Lists]])
status: in progress — deriving
---
> [!abstract] Thread-Safe LRU Cache
> Track B (concurrency) · Salesforce #1-frequency LLD · Patterns: Strategy (eviction seam, later)
> Build cold single-threaded first, then the *"now make it thread-safe"* escalation.

---

## 📖 Jargon (say these by name in the room)

- **Sentinel node** — a dummy `head`/`tail` node that holds no real data, sitting permanently at
  each end of the linked list. Because there's always a dummy on both sides, no real node ever has a
  null `prev`/`next`, so insert/remove need **zero** null-checks or special cases.
- **TOCTOU** — *Time-Of-Check to Time-Of-Use.* A race where you check a condition, then act on it,
  and another thread changes things **in the gap** so the check is stale. Our `get`:
  `containsKey` says yes → another thread evicts → `map.get` returns null → `.value` is an NPE. Fix:
  put check + use inside **one lock** so nothing can slip into the gap. (Same shape as Parking Lot's
  find-then-occupy.) More precise than saying "race condition."
- **Lost update** — two threads read the same value, both write based on it, one write silently
  overwrites the other. Our `addToFront`: two threads both read the same `head.next`, one insertion
  is lost. No exception — just silent corruption.
- **Sharding** — splitting into N independent smaller caches, each with its **own map + list + lock**.
  A key is routed by `hash(key) % N` to one shard. Different keys → different locks → run in
  parallel, cutting lock contention ~N-fold. Cost: LRU becomes per-shard (approximate global LRU),
  which is fine for a cache. *This is the answer to "reduce contention at scale" — name it, don't
  build it at 3 YOE.* Not to be confused with **striping** (many locks over **one** shared structure)
  — striping can't work here because the single linked list is shared by all keys.
- **Read-write lock** — a lock that allows many concurrent readers OR one writer. **Useless here**
  because `get` mutates the list (moves node to front), so every operation is a *writer*.

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

## 🧱 Classes (single-threaded — ✅ built & passing)

**`Node`** — `private class Node { K key; V value; Node prev, next; }`. Inner class (implementation
detail, never public). Holds **both** key and value: value because the node *is* the storage (one
map does lookup + ordering); key because eviction starts from a node (`tail.prev`) and must reach
back into the map — `map.remove(node.key)` — and the map is one-directional `K → Node`.

**`Cache<K,V>`** — owns:
- `Map<K, Node> map` — O(1) key → node
- doubly-linked list with **dummy `head` and `tail` sentinels** (wired `head <-> tail` in the ctor).
  `head` = MRU end, `tail` = LRU end. Sentinels are `final`, never reassigned.

> [!important] Only two methods touch pointers — everything else calls them
> `addToFront(node)` and `removeNode(node)` are the **only** pointer surgery. `get`, `put`, and
> `removeLRU` are written in terms of those two. Every bug during the build was a hand-written
> special case (`if head.next == node`, `if tail.prev == node`, manual `tail.prev = tail.prev.prev`);
> every fix was "delete the special case, reuse the helper." Sentinels exist precisely so `add`/
> `remove` need **zero** special cases — `prev`/`next` are never null, so the same 4/2 lines work at
> front, middle, or back.
> ```java
> void addToFront(Node n){ n.prev=head; n.next=head.next; head.next.prev=n; head.next=n; }
> void removeNode(Node n){ n.prev.next=n.next; n.next.prev=n.prev; }
> ```

- `get(key)` → miss ⇒ null; hit ⇒ `removeNode` + `addToFront` (move to MRU), return value. O(1).
- `put(key,value)` → existing ⇒ update value + move to front; new ⇒ evict LRU if full, `addToFront`,
  `map.put`. O(1).
- `removeLRU()` → `node = tail.prev`; `map.remove(node.key)`; `removeNode(node)`. **Must unlink both
  directions** — the bug was updating only the backward pointer, leaving the evicted node a *ghost*
  in the forward chain (symptom: `size == 3` but 4 rows printed).

## 🔒 Making it thread-safe (the Salesforce escalation)

Not thread-safe as built. The races, precisely (Java maps don't throw "key not found" — get the
failure mode right):

1. **Eviction over-evict** — two threads both pass the `size == CAPACITY` check, both evict → two
   entries dropped when one should go, and concurrent pointer surgery on the same `tail.prev`.
2. **`get` TOCTOU → NPE** — `containsKey` passes, another thread evicts the key, `map.get(key)`
   returns null, `.value` → **NullPointerException** (not "not found").
3. **`addToFront` lost update** — two threads (even two `get`s on *different* keys) both read the
   same `head.next`; one insertion is silently lost. Corrupts the DLL with **no exception**.
4. **Plain `HashMap` self-corruption** — concurrent writes can corrupt its own buckets (resize race).

**Root:** races span **both** structures (map + DLL) and **both** methods (`get` + `put`), and the
two structures must stay mutually consistent. A `get` *writes* (moves to front) — so reads are not
read-only.

> [!warning] Why the "clever" options don't apply here
> - **Read-write lock** — no. `get` mutates the DLL, so it's a *writer*, not a reader. RWLock buys
>   nothing when every op is a write.
> - **Striped / per-key locks** — no. The DLL is one shared structure (all nodes share `head`/`tail`);
>   you can't partition it by key.
> - **`ConcurrentHashMap` alone** — no. It makes the map safe but the DLL invariant spans map *and*
>   list; they must update atomically *together*, which one concurrent map can't guarantee.
> → **One lock guarding the whole cache** (both structures, both methods) is the correct answer for a
> single-node in-memory LRU. `synchronized` on `get`/`put`, or one `ReentrantLock`. Say out loud that
> it serializes access, and that that's acceptable because each op is O(1) (µs), not I/O-bound.
> *Distributed* escalation → Redis / consistent hashing (different problem).

## 📐 Build Scope
- ✅ single-threaded LRU, O(1) get/put, correct eviction, driver prints eviction visibly
- ☐ thread-safe version (one lock)
- ☐ (stretch) LFU as a second policy → *then* extract `EvictionPolicy` seam

## 🔍 Post-Build
- ☐ extension test: add LFU — does the eviction seam extract cleanly on the second policy?
- ☐ concurrency walkthrough out loud: name races 1–3 + the one lock that closes them
- ☐ say the `LinkedHashMap` production one-liner
