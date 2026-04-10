# Access Patterns — Why They Drive Everything

## The core idea

Schema serves queries. Access patterns are those queries — the actual reads your system needs to support. Every schema decision flows from them:

- Which columns to index
- What order columns go in a composite index
- Whether to normalize or denormalize
- Whether to embed or reference (document stores)
- What becomes the partition key (Cassandra)
- What to cache in Redis

Design schema without knowing your access patterns and you'll end up with a schema that looks reasonable on paper but requires expensive full table scans on your hottest read paths.

---

## How access patterns determine indexes

Every access pattern maps directly to an index decision.

**Pattern:** "load all posts by user_123, newest first"
```sql
SELECT * FROM posts WHERE user_id = '123' ORDER BY created_at DESC LIMIT 20;
```
→ needs composite index on `(user_id, created_at DESC)`
→ leftmost column = filter, second column = sort order

**Pattern:** "load all comments on post_456, oldest first"
```sql
SELECT * FROM comments WHERE post_id = '456' ORDER BY created_at ASC LIMIT 20;
```
→ needs composite index on `(post_id, created_at ASC)`

**Pattern:** "has user_123 liked post_456?"
```sql
SELECT 1 FROM likes WHERE user_id = '123' AND post_id = '456';
```
→ composite PK on `(user_id, post_id)` handles this in O(1)

The rule: **your WHERE clause tells you what to index. Your ORDER BY tells you the column order.**

---

## How access patterns determine denormalization

Normalization removes duplication — every fact lives in one place. But at scale, joins on hot read paths become expensive.

**Normalized approach:**
```sql
-- to render a post in the feed, you need:
SELECT posts.*, users.username, users.profile_pic
FROM posts
JOIN users ON users.id = posts.user_id
WHERE posts.post_id = '456';
```

One join per post. For 20 posts in a feed — 20 joins. At 500 million users all loading feeds simultaneously — the users table becomes a bottleneck.

**Denormalized approach:**
```sql
posts (
    post_id      UUID,
    user_id      UUID,
    username     VARCHAR(30),   -- duplicated from users
    profile_pic  VARCHAR(500),  -- duplicated from users
    caption      TEXT,
    image_url    VARCHAR(500),
    created_at   TIMESTAMP
)
```

Now rendering a post needs zero joins. The trade-off: if a user changes their username, you need to update it in both `users` and all their `posts`. The write path gets more complex.

> [!important] Denormalization rule
> Denormalize only when a specific read query would require expensive joins at scale. Always state the trade-off: "I'm duplicating username into posts to avoid a join on the hot feed read path — the cost is maintaining consistency on writes."

---

## How access patterns determine caching

The most expensive access pattern for Instagram is the feed:

```sql
SELECT posts.*, users.username, users.profile_pic
FROM posts
JOIN follows ON follows.following_id = posts.user_id
JOIN users ON users.id = posts.user_id
WHERE follows.follower_id = current_user
ORDER BY posts.created_at DESC
LIMIT 20;
```

A user follows 500 people. Each has thousands of posts. Two joins. Sorted by timestamp. At 500 million users — this query cannot run against the DB on every feed load.

Access pattern tells you this is the hottest read in the system → cache it.

**Redis sorted set per user:**
```
KEY   → feed:user_123
VALUE → sorted set { post_id → timestamp, post_id → timestamp, ... }
```

Feed load becomes:
```
ZREVRANGE feed:user_123 0 19  → top 20 post IDs in O(log n)
```

Then fetch post details for those 20 IDs. No joins, no full table scan.

---

## How access patterns determine partition keys (Cassandra)

In Cassandra, the access pattern directly dictates your data model — one table per query pattern.

**Access pattern:** "last 50 messages in conversation X"

```
Partition key  → conversation_id   (route to the right node)
Clustering key → timestamp DESC    (sort within the partition)
```

```sql
SELECT * FROM messages
WHERE conversation_id = 'abc'
ORDER BY timestamp DESC
LIMIT 50;
→ pure index scan on one node, no cross-partition query
```

If you had partitioned by `user_id` instead — fetching a conversation's messages would require hitting multiple nodes and merging results. Expensive and slow.

> In Cassandra: partition key = "which node?", clustering key = "in what order?" Both are driven entirely by your access pattern.
