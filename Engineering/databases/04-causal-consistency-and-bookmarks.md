#databases #consistency #bookmarks #replication #clusters

---

# Causal Consistency and Bookmarks

A teacher updates a student's grade in the gradebook. A second later, the same teacher refreshes the page — the new grade isn't there. Five seconds later, it appears. What just happened, and how do databases solve it?

---

## The Setup — Clusters, Leaders, Followers

Most managed cloud databases run as **clusters**, not a single server. A typical setup:

- One **leader** node — handles all writes
- Several **follower** nodes — handle reads, replicate from the leader

This scales reads horizontally and survives a node failure. But it introduces a small lag: the followers replicate the leader's writes asynchronously, taking a few milliseconds to catch up.

```
       ┌──── replication lag (few ms) ────┐
       ↓                                   ↓
   [Leader]  ──────writes────────►  [Follower 1]
                                    [Follower 2]
                                    [Follower 3]
```

---

## The Read-Your-Writes Problem

Now imagine your application:

1. Sends `UPDATE grade = 'A'` — goes to the **leader**
2. Sends `SELECT grade ...` — load balancer sends it to **Follower 2**

Between step 1 and step 2, only a millisecond has passed. Follower 2 hasn't replicated the write yet. Your read returns the **old** grade, not 'A'.

> [!warning] In a clustered database, immediately reading what you just wrote is **not guaranteed** unless you do something to coordinate. This is called the read-your-writes problem.

---

## What a Bookmark Is

A bookmark is a **token** the server hands you after a write. Think of it as a marker:

```
"FB:kcwQabcd...tx42"
```

It encodes "the database state immediately after transaction 42." It's just an opaque string from your application's perspective.

---

## How Bookmarks Solve the Problem

The mechanism in four steps:

```
1. Write to leader        →  server returns bookmark "tx42"
2. App stores bookmark
3. Read query sent with bookmark
4. Follower checks: "am I caught up to tx42?"
      yes → answer immediately
      no  → wait a few ms, then answer
```

The follower won't answer your read until it has replicated up to the bookmark you sent. So you always see your own writes — at the cost of a tiny wait when replication is behind.

---

## How Sessions Hide This

Most drivers wrap bookmarks inside a **session** so you don't have to manage them:

```python
async with driver.session() as session:
    await session.run("CREATE (:Person {name: 'Alice'})")  # gets bookmark
    await session.run("MATCH (:Person {name: 'Alice'})")    # uses bookmark — sees Alice
```

The session stores the bookmark internally between calls. Two queries inside one session always see each other's writes.

---

## Across Sessions — You Pass the Bookmark Yourself

If your write and read are in **different sessions** (different requests, different processes), you have to carry the bookmark yourself:

```python
# Request 1 — write
async with driver.session() as s1:
    await s1.run("CREATE (:Order {id: 42})")
bookmarks = await s1.last_bookmarks()    # extract token
# Stash bookmarks in cache, request state, etc.

# Request 2 — read (later, possibly different process)
async with driver.session(bookmarks=bookmarks) as s2:
    result = await s2.run("MATCH (:Order {id: 42}) RETURN ...")
    # waits for follower to catch up
```

---

## When Bookmarks Actually Matter

| Scenario | Bookmarks needed? |
|----------|-------------------|
| Write and read in the same session | Built in, no work |
| Write, then immediate read in next request (page reload after submit) | Yes — must pass bookmark |
| Write today, read tomorrow | No — replication caught up long ago |
| Eventually-consistent read is fine (analytics, lists) | No |

> [!info] Bookmarks pay rent only when reads happen **right after** a write, on a **different session**, and **stale data would be wrong**. Otherwise ignore them.

---

## Why You Often Don't Need Them

For most application flows, write and read are far apart in time:

- A user creates a record, navigates away, comes back tomorrow — replication has caught up
- An admin confirms an action, the next admin acts on it minutes later — replication has caught up
- An analytical job reads yesterday's data — definitely caught up

Bookmarks become important when:
- A user submits a form and the redirect must show the new state
- A multi-step workflow writes data in step 1 that step 2 must see
- A test case writes test data and immediately asserts on it

For everything else, just open a fresh session per operation and let the cluster handle itself.

---

## Mental Model

> [!info] A cluster is like a teacher dictating notes to a room of students. The teacher (leader) speaks first, the students (followers) write it down a moment later. A bookmark is the line you point to: "I want the answer **after** this line is written, not before." Without it, a student answering quickly might give you stale information.
