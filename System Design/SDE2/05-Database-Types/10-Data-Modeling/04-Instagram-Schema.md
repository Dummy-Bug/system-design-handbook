# Instagram — Full Schema Walkthrough

## Step 1 — Entities (nouns from requirements)

- Users can post photos
- Users can follow other users
- Users can like and comment on posts
- Users can see a feed of posts from people they follow

**Entities:** User, Post, Comment, Like, Follow

---

## Step 2 — Relationships (verbs from requirements)

```
User     → posts →    Post      (1:many)
User     → follows → User       (many:many, self-referential)
User     → likes →   Post       (many:many)
User     → comments → Post      (many:many with body text)
```

---

## Step 3 — Access patterns

- Load user profile → fetch 1 user by ID
- Load user's posts → fetch posts by user_id, newest first
- Load feed → fetch recent posts from everyone the user follows
- Load comments on a post → fetch comments by post_id, oldest first
- Check if user liked a post → yes/no per post per user (runs 20x per feed load)
- Count followers → count follows where following_id = user

The feed and the like-check are the hottest reads. Both need special handling beyond a simple SQL query.

---

## Step 4 — Schema

### Users table

```sql
users (
    user_id     UUID PRIMARY KEY,
    username    VARCHAR(30)  UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    bio         TEXT,
    profile_pic VARCHAR(500),
    created_at  TIMESTAMP
)
```

**Why UUID over auto-increment?**
Auto-increment integers are sequential — if you shard by user_id, all new users land on the last shard. One shard gets hammered, the rest sit idle. That's a hotspot. UUID is random — new users distribute evenly across all shards.

> Never use auto-increment as a shard key. Sequential keys = hotspot on the last shard.

---

### Posts table

```sql
posts (
    post_id    UUID PRIMARY KEY,
    user_id    UUID NOT NULL,
    caption    TEXT,
    image_url  VARCHAR(500),    -- points to S3, never store files in DB
    created_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
)

CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);
```

**Why composite index on (user_id, created_at DESC)?**

Access pattern: "load user_123's posts, newest first"
```sql
SELECT * FROM posts WHERE user_id = '123' ORDER BY created_at DESC LIMIT 20;
```
The index's leftmost column `user_id` filters to just that user's posts. The second column `created_at DESC` means results are already sorted — no sort step needed. Pure index scan.

---

### Follows table

```sql
follows (
    follower_id  UUID NOT NULL,   -- the person who follows
    following_id UUID NOT NULL,   -- the person being followed
    created_at   TIMESTAMP,

    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id)  REFERENCES users(user_id),
    FOREIGN KEY (following_id) REFERENCES users(user_id)
)

CREATE INDEX idx_follows_following ON follows(following_id);
```

Both columns reference the `users` table — this is a self-referential junction table.

The composite PK `(follower_id, following_id)` covers direction 1 — "who does user_123 follow?" The separate index on `following_id` covers direction 2 — "who follows user_123?" Both directions need to be fast.

---

### Likes table

```sql
likes (
    user_id    UUID NOT NULL,
    post_id    UUID NOT NULL,
    created_at TIMESTAMP,

    PRIMARY KEY (user_id, post_id)
)
```

The composite PK enforces uniqueness (can't like the same post twice) and makes the most critical query O(1):

```sql
SELECT 1 FROM likes WHERE user_id = '123' AND post_id = '456';
```

**Why is this query so hot?**

On every feed load, the app renders 20 posts. Every post has a heart icon — red if the current user liked it, empty if not. That's 20 like-check queries per feed load, for every user, every time they refresh. At 500 million users this is one of the most frequent queries in the system.

**At scale — cache in Redis:**

```
KEY   → likes:post_456
VALUE → Redis Set { user_123, user_789, user_456 ... }

SISMEMBER likes:post_456 user_123  → O(1), in-memory
```

For viral posts with millions of likes where a Redis set becomes too large — use a **Bloom filter**. It uses far less memory and can instantly tell you "definitely not liked" vs "maybe liked." A "maybe liked" falls back to a DB check.

---

### Comments table

```sql
comments (
    comment_id UUID PRIMARY KEY,
    post_id    UUID NOT NULL,
    user_id    UUID NOT NULL,
    body       TEXT,
    created_at TIMESTAMP,

    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)

CREATE INDEX idx_comments_post_created ON comments(post_id, created_at ASC);
```

Access pattern: "load comments on post_456, oldest first"
```sql
SELECT * FROM comments WHERE post_id = '456' ORDER BY created_at ASC LIMIT 20;
```
Same composite index pattern as posts — filter on entity ID, sort by time.

---

## Feed — Redis, not SQL

The feed query in pure SQL:

```sql
SELECT posts.*, users.username, users.profile_pic
FROM posts
JOIN follows ON follows.following_id = posts.user_id
JOIN users ON users.id = posts.user_id
WHERE follows.follower_id = current_user
ORDER BY posts.created_at DESC
LIMIT 20;
```

A user follows 500 people, each with thousands of posts. Two joins, sorted by timestamp. At 500 million users simultaneously loading feeds — this query cannot run against the DB.

**Solution — Redis sorted set per user:**

```
KEY   → feed:user_123
VALUE → sorted set { post_id_1 → timestamp, post_id_2 → timestamp, ... }

ZREVRANGE feed:user_123 0 19  → top 20 post IDs instantly
```

**Fan-out on write** — when a normal user posts:
```
User posts photo
    ↓
background job fetches all followers
    ↓
inserts post_id into each follower's feed sorted set
```

Works fine for 500 followers. But Kylie Jenner has 200 million followers — 200 million cache writes on every post. The background job takes hours.

**Fan-out on read for celebrities:**

```
Normal users  → fan-out on write → post pre-inserted into all follower caches
Celebrities   → fan-out on read  → post NOT written to follower caches
                                    when you load your feed:
                                    merge your regular cache + celebrity posts live
```

```
Load feed for user_123:
    ↓
fetch feed:user_123 from Redis (posts from normal follows)
    ↓
fetch latest posts from celebrities user_123 follows (live DB query, small result set)
    ↓
merge + sort by timestamp
    ↓
return top 20
```

---

## Complete schema summary

```
users      → user_id (UUID PK), username, email, bio, profile_pic, created_at
             UUID to avoid shard hotspot

posts      → post_id (UUID PK), user_id (FK), caption, image_url, created_at
             index: (user_id, created_at DESC)
             image_url points to S3 — never store files in DB

follows    → (follower_id, following_id) composite PK, created_at
             index: (following_id) for reverse lookup
             self-referential — both FKs reference users

likes      → (user_id, post_id) composite PK
             Redis Set for like checks at scale
             Bloom filter for viral posts with millions of likes

comments   → comment_id (UUID PK), post_id (FK), user_id (FK), body, created_at
             index: (post_id, created_at ASC)

feed       → Redis sorted set per user (feed:user_id → post_id + timestamp)
             fan-out on write for normal users
             fan-out on read for celebrities
```
