> [!info] MongoDB's flexibility is real, but it comes with hard trade-offs. Understanding the limitations is what makes you credible in an interview — anyone can say "use MongoDB for flexible schema", but knowing where it breaks and why is what matters.

## No cross-document joins

In SQL, joining two tables is one query handled by the database:

```sql
SELECT posts.caption, users.name
FROM posts JOIN users ON posts.user_id = users.id
WHERE posts.post_id = 1
```

One round trip to the database. The database engine handles the join.

In MongoDB, there is no equivalent. You fetch separately and join in application code:

```
Step 1: db.posts.findOne({ post_id: 1 })   → get post, extract user_id: 42
Step 2: db.users.findOne({ user_id: 42 })  → get user name
Step 3: combine in application code
```

Two round trips. At scale — imagine rendering a feed of 20 posts, each needing the author's name — that's 21 database calls instead of 1.

MongoDB has `$lookup` (an aggregation stage that simulates a join) but it's expensive, not a first-class operation, and not designed for high-throughput use. The correct answer in MongoDB is to **denormalize** — embed or duplicate the data you need, so you never need the join.

---

## No schema constraints

MongoDB has no enforcement of:

```
NOT NULL          →  a document can be missing any field, MongoDB won't complain
FOREIGN KEY       →  no referential integrity — you can have a comment with a 
                     post_id that points to a deleted post (orphaned document)
UNIQUE            →  only enforced if you explicitly create a unique index
CHECK constraint  →  doesn't exist
```

**Your application code becomes the last line of defence**. A bug that writes a document with a missing required field will succeed silently. You won't know until a read fails because the field isn't there.

```
SQL:      INSERT INTO users (email) VALUES (NULL)  → rejected by DB ✗
MongoDB:  db.users.insertOne({ name: "Rahul" })    → accepted, no email ✓ (silently)
```

This is why MongoDB is wrong for:
- Financial transactions — you need the database to guarantee integrity
- Order records — a missing `amount` field must be caught at write time, not at billing time
- Anything regulated — compliance requires strict data contracts

---

## 16MB document size limit

A single MongoDB **document** cannot exceed 16MB. For most use cases this is never a concern. But it becomes a hard constraint when you embed unbounded data.

```
50,000 comments × 200 bytes each = 10MB → approaching the limit
100,000 comments                  = 20MB → exceeds limit, write rejected ✗
```

This is the mechanical reason behind the embedding vs referencing rule. Unbounded arrays will eventually hit this wall.

---

## Intentional denormalization — the operational cost

MongoDB pushes you toward denormalization to avoid joins. Denormalization works, but it creates an ongoing operational burden:

```
User updates their profile picture
  → new avatar_url must propagate to:
      - every post they wrote
      - every comment they left  
      - every product review they submitted
      - ...

In SQL:   update users SET avatar_url = '...' WHERE user_id = 42
          → one row updated, all joins automatically see new value ✓

In MongoDB: must update every denormalized copy across multiple collections
            → background job, async, eventually consistent
```

You trade SQL's update simplicity for MongoDB's read simplicity. For read-heavy systems where profile pictures rarely change, this is the right trade. For write-heavy systems with frequently changing shared data, it becomes painful.

---

## Summary of limitations

```
No cross-document joins    →  denormalize or accept multiple round trips
No schema constraints      →  application must enforce data integrity
16MB document limit        →  unbounded arrays must be referenced, not embedded
Denormalization cost       →  update propagation is your problem, not the DB's
```

> [!danger] Common interview trap
> MongoDB is flexible so I'll use it everywhere. Wrong. Use it where variable schema and document-centric access patterns are the dominant need. Financial data, relational data with complex joins, and anything needing strict integrity belongs in SQL.
