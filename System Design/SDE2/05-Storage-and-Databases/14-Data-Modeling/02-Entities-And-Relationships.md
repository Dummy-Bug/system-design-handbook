# Entities and Relationships

## Extracting entities

Entities come from the nouns in your functional requirements. Every noun that needs to be stored, queried, or managed is an entity — it becomes a table (SQL), a collection (MongoDB), or a partition (Cassandra).

For Instagram:

| Noun | Entity | Table |
|---|---|---|
| User | Person using the app | `users` |
| Post | A photo with caption | `posts` |
| Comment | Text reply on a post | `comments` |
| Like | A user liking a post | `likes` |
| Follow | A user following another | `follows` |

Photo is not a separate entity — it's an attribute of Post (stored as a URL pointing to S3).
Feed is not a stored entity — it's a derived view (cached in Redis, not stored in SQL).

---

## Mapping relationships

Verbs in requirements become relationships. There are three types:

**1:1** — one entity maps to exactly one of another
- User → Profile (if profile is separate from user)
- Usually just embed as columns in the same table

**1:Many** — one entity maps to many of another
- User → Posts (one user has many posts)
- Implemented with a foreign key on the "many" side: `posts.user_id`

**Many:Many** — neither side maps to just one of the other
- User → Like → Post: one user can like many posts, and one post can be liked by many users
- User → Follow → User: one user can follow many users, and one user can be followed by many users
- Implemented with a **junction table** containing both foreign keys

---

## Junction tables

A junction table sits between two entities in a many-to-many relationship. It contains the primary keys of both entities as a composite primary key.

```sql
likes (
    user_id  UUID NOT NULL,
    post_id  UUID NOT NULL,
    PRIMARY KEY (user_id, post_id)   ← composite PK enforces uniqueness
)
```

The composite PK does two things:
- Prevents duplicates — a user can't like the same post twice
- Acts as an index — "has user_123 liked post_456?" is an O(1) lookup

---

## Self-referential tables

When an entity has a relationship with itself — like users following other users — you use a self-referential junction table. Both foreign keys reference the same table:

```sql
follows (
    follower_id  UUID NOT NULL,   -- the person who follows
    following_id UUID NOT NULL,   -- the person being followed
    created_at   TIMESTAMP,

    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id)  REFERENCES users(user_id),
    FOREIGN KEY (following_id) REFERENCES users(user_id)
)
```

Both columns point to `users`. The naming makes the direction of the relationship explicit — `follower_id` is doing the following, `following_id` is being followed.

Here's what the table looks like with real data:

```
follower_id  | following_id | created_at
-------------|--------------|------------
user_1       | user_2       | 2024-01-01    ← user_1 follows user_2
user_1       | user_3       | 2024-01-02    ← user_1 follows user_3
user_2       | user_1       | 2024-01-03    ← user_2 follows user_1
user_3       | user_1       | 2024-01-04    ← user_3 follows user_1
```

Notice that `user_1` appears multiple times in `follower_id`. This is why `user_id` alone can never be the primary key — a PK must be unique per row, and no single column here is unique.

But the combination of `(follower_id, following_id)` is always unique — a user can only follow someone once. That composite PK also enforces this business rule for free:

```sql
-- Try to make user_1 follow user_2 again
INSERT INTO follows (follower_id, following_id) VALUES ('user_1', 'user_2');
-- ERROR: duplicate key violates primary key constraint ✗
```

No extra application code needed — the DB rejects the duplicate automatically.

---

## Always think about both directions of a junction table

Every junction table has two read directions. Both need to be fast.

For the `follows` table:

```sql
-- Direction 1: who does user_123 follow?
SELECT following_id FROM follows WHERE follower_id = '123';
-- → hits composite PK index (starts with follower_id) ✓

-- Direction 2: who follows user_123?
SELECT follower_id FROM follows WHERE following_id = '123';
-- → composite PK starts with follower_id, not following_id → full scan ✗
```

Direction 2 can't use the PK index. You need a separate index:

```sql
CREATE INDEX idx_follows_following ON follows(following_id);
```

> [!important] Junction table rule
> Whenever you create a junction table, immediately ask yourself: "do I need to query this in both directions?" If yes — you need an index for each direction. The composite PK covers one direction. Add a separate index for the other.
