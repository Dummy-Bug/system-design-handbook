# Red Flags — Mistakes Interviewers Watch For

These are the things that signal to an interviewer that you don't deeply understand data modeling. Avoid all of them.

---

## 1. Jumping to schema without establishing entities and access patterns

The most common mistake. Candidate hears "design Instagram" and immediately starts listing tables.

**What the interviewer sees:** no process, no systematic thinking, just guessing.

**What to do instead:** explicitly say "before I design the schema, let me identify the entities from the requirements, map the relationships, and define the access patterns — because my schema will be shaped around what the system needs to query."

---

## 2. No primary key discussion

Every table needs a primary key. Candidates who just write column names without thinking about the PK signal they haven't thought about uniqueness, indexing, or sharding.

Always explicitly choose and justify your PK:
- Why UUID over auto-increment?
- Why composite PK on a junction table?
- What makes this a good shard key?

---

## 3. Using auto-increment as a shard key

Auto-increment integers are sequential. All new rows land on the last shard. One shard gets hammered, the rest sit idle.

```
Shard 1: users 1-1M    (old, low traffic)
Shard 2: users 1M-2M   (old, low traffic)
Shard 3: users 2M-3M   (ALL new users, ALL traffic) ← hotspot
```

**Fix:** use UUID (random distribution) or a hash of the natural key as the shard key.

> Never use auto-increment as a shard key. Sequential = hotspot on the last shard.

---

## 4. Not thinking about the write path when designing for reads

Denormalization makes reads fast but writes complex. Candidates who denormalize without acknowledging the write cost signal incomplete thinking.

If you duplicate `username` into the `posts` table:
- Read path: no join needed ✓
- Write path: user changes username → must update `users` AND every row in `posts` ← you must mention this

Always state the trade-off explicitly: "I'm denormalizing X into Y to avoid a join on the hot read path. The cost is that writes to X now require updating Y as well."

---

## 5. Storing derived data without explaining cache invalidation

If you cache the feed in Redis, when does the cache get updated? If you store a `follower_count` column in the users table, when does it get updated?

Candidates who add cached or derived data without explaining how it stays consistent signal they haven't thought through the system end-to-end.

Always answer: "when this data changes, here's how the cache/derived column gets updated."

---

## 6. Missing indexes on hot query paths

Designing a table without thinking about what queries will hit it. The `posts` table without an index on `(user_id, created_at)` means every "load user's posts" query is a full table scan.

After every table, ask yourself: "what are the queries against this table? Do I have indexes that serve those queries without a full scan?"

---

## 7. Ignoring both directions of a junction table

Junction tables have two read directions. Both need to be fast. Candidates who only index one direction miss the other.

For `follows(follower_id, following_id)`:
- The composite PK covers "who does user X follow?" ✓
- But "who follows user X?" needs a separate index on `following_id` ← often missed

> After every junction table: ask "do I need to query this in both directions?" If yes — add an index for the second direction.

---

## 8. Treating all users the same (missing the celebrity problem)

Fan-out on write works for normal users with hundreds of followers. Applying the same strategy to celebrities with millions of followers means a single post triggers millions of cache writes — the background job runs for hours.

In any social system with public profiles, always acknowledge the celebrity/hotspot problem and explain the fan-out on read approach for high-follower accounts.

---

## Quick checklist before presenting a schema

```
□ Did I extract entities from nouns in the requirements?
□ Did I map relationships from verbs?
□ Did I define access patterns before writing any tables?
□ Does every table have a justified primary key?
□ Did I avoid auto-increment as a shard key?
□ Does every hot query path have an index?
□ Did I think about both directions of every junction table?
□ Did I acknowledge denormalization trade-offs on the write path?
□ Did I explain how cached/derived data stays consistent?
□ Did I handle the celebrity/hotspot problem for social systems?
```
