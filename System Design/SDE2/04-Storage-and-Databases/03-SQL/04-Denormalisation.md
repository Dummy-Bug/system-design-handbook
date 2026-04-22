# Denormalisation

> [!question] You just spent all that effort removing duplication. Why would you ever put it back?
> Because reads are expensive too — and joins are the silent killer at scale.

---

## The Join Problem at Scale

You're building Twitter's home feed. To display one tweet you need data from multiple tables:

```
tweet text      → tweets table
author name     → users table
author avatar   → users table
like count      → likes table
retweet count   → retweets table
```

That's 4 joins per tweet. A feed shows 20 tweets — that's 80 joins per feed load. At 100 million users simultaneously loading their feeds, those joins are happening constantly, in parallel, on every server.

Joins aren't free. The database has to look up rows across multiple tables, match them on a key, and combine them — on every single request. At that scale, it becomes a bottleneck.

The fix? Deliberately put the duplication back — store the author's name and avatar directly in the tweets table.

```
Denormalised tweets table:
| tweet_id | tweet_text    | author_name | author_avatar |
|----------|---------------|-------------|---------------|
| 1        | "Hello world" | Alice       | alice.jpg     |
| 2        | "Second post" | Alice       | alice.jpg     |
```

One table, one query, no joins. Feed loads instantly.

> [!info] **Denormalisation** — deliberately storing duplicate data to eliminate joins and make reads faster. You trade storage and write complexity for read speed.

---

## Why You Can Afford It for Read-Heavy Data

The obvious question: Alice's name is now duplicated across 500 tweet rows. She changes her name — you have to update 500 rows. Doesn't that create inconsistency?

Yes — but only for a short window.

```
Alice changes her name → 500 rows updating → tiny inconsistency window → done ✓
How often does this happen? Once a year.
Impact during the window? User sees old name for a few seconds — cosmetic.
```

You're not *accepting* inconsistency — you're *managing the window*. The window is seconds, the impact is cosmetic, and it happens once a year. That's an acceptable trade-off for eliminating 80 joins per feed load across 100 million users.

Compare that to the alternative: keeping the data normalised, doing 4 joins per tweet, 80 joins per feed, for every user, every second. The join cost is permanent. The inconsistency window is temporary.

> [!important] The question is never "can we afford inconsistency" — it's "how long is the inconsistency window and what's the impact?"
> ```
> Author name   → window = seconds, impact = cosmetic    ✓ acceptable
> Bank balance  → window = any,     impact = money lost  ✗ never acceptable
> ```

---

## Why You Can't Afford It for Write-Heavy Data

Like count is the opposite of author name. It doesn't change once a year — it changes every second. Thousands of users liking Kylie Jenner's tweet simultaneously.

First, let's understand why the database handles concurrent writes safely on a normalised table.

You might think: two users like at the same time — don't they both read `1200`, both add 1, both write `1201`, and you lose a like?

That's what happens if you do it naively. But the database gives you an atomic update:

```sql
UPDATE likes SET like_count = like_count + 1 WHERE tweet_id = 1
```

This is not "read then write." It's one atomic operation. The database processes it internally without exposing an intermediate state. Even if 1000 users do this simultaneously, the database serialises them — one after the other on that row:

```
User A's update → 1200 → 1201
User B's update → 1201 → 1202
...
Final count = correct ✓
```

Now — the real problem with denormalising write-heavy data is not the race condition. It's the **hotspot**.

When you update a row, the database locks it while the update runs. Other operations on that same row have to wait.

If `like_count` lives in its own small dedicated table:
```
likes table:
| tweet_id | like_count |   ← tiny row, lock held for microseconds
```

The lock is tiny. It's released instantly. The queue of waiting updates moves fast.

But if you denormalise `like_count` into the tweets table:
```
tweets table — one fat row:
| tweet_id | text | author | avatar | bio | like_count | retweet_count | ... |
```

Now every like locks the entire fat row. While `like_count` is updating, nobody can read or write anything else on that row — not the tweet text, not the author name, not the avatar. Everything on that row is blocked.

```
Kylie Jenner's tweet → millions of likes/sec
→ fat tweet row locked millions of times/sec
→ someone just wants to read the tweet text → blocked, waiting for a like to finish
→ everyone experiences slow responses ✗
```

At millions of likes per second, that row becomes a permanent hotspot. The lock is almost never released before the next update arrives.

> [!important] Denormalising write-heavy columns into large rows creates **hotspots**. The row-level lock blocks all reads and writes on that row while the update runs. At high write frequency, the lock is almost permanently held — everything slows down.

---

## The Rule

```
Denormalise when:
  → read-heavy data (author name, avatar, tweet text)
  → data that changes rarely (once a year, not every second)
  → inconsistency window is short and impact is cosmetic

Keep normalised when:
  → write-heavy data (like count, retweet count, inventory)
  → financial data (balance, transactions)
  → data where any inconsistency has real impact
```

> [!tip] Twitter does exactly this in production. The feed per user is pre-computed and denormalised — loading your feed is a single read, no joins. Author names and avatars are duplicated across millions of tweet rows. Like counts live in their own normalised table, updated atomically, never denormalised into the tweet row.
