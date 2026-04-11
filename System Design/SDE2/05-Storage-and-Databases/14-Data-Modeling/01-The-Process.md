> [!info] Why this matters
> Data modeling is where interviewers judge whether you actually understand the system. Anyone can say "use Cassandra" — but can you design the schema, pick the right indexes, and explain why? The data model section of a case study is where strong candidates separate themselves.

# The Data Modeling Process

## The wrong way

Most candidates hear "design the data model for Instagram" and immediately start throwing table names at the wall:

"Uh... users table, posts table, comments table, likes table..."

They jump straight to schema without establishing what the system actually needs. The result is a schema that looks plausible but falls apart under questioning — missing indexes, wrong shard keys, expensive queries on hot paths.

---

## The right way — 4 steps

### Step 1 — Extract entities from nouns

Read the functional requirements. Pick out every noun. Those are your entities — the things that need to exist in your database.

Instagram requirements:
- Users can post photos
- Users can follow other users
- Users can like and comment on posts
- Users can see a feed of posts from people they follow

Nouns: **user, post, photo, comment, like, follow**

Not every noun becomes a table. Before writing any schema, filter out the nouns that aren't real stored entities:

- **Photo** — not a separate entity. It's an attribute of Post (stored as a URL pointing to S3). Photo lives as a column on the posts table, not its own table.
- **Feed** — not a stored entity at all. A feed is a computed result — "show me recent posts from people I follow." It's derived from Posts + Follows at query time, or precomputed and cached in Redis. There is no `feeds` table.

What remains as actual entities: **user, post, comment, like, follow**

These become your tables (or collections, or documents, depending on your DB choice).

---

### Step 2 — Extract relationships from verbs

Read the same requirements. Pick out every verb. Those are the relationships between your entities.

- Users **post** photos → User has many Posts
- Users **follow** other users → User follows User (self-referential many-to-many)
- Users **like** posts → User likes Post (many-to-many)
- Users **comment** on posts → User comments on Post (many-to-many with content)

Map them out before writing any schema:

```
User     → posts →      Post       (1:many)
User     → follows →    User       (many:many, self-referential)
User     → likes →      Post       (many:many)
User     → comments →   Post       (many:many with body text)
Comment  → belongs to → Post       (many:1)
```

---

### Step 3 — Define access patterns

This is the most important step and the one most candidates skip.

Access patterns are the actual read queries your system needs to serve. They drive every schema decision that follows — what to index, what to denormalize, what to embed, what to cache.

For Instagram:
- Load a user's profile → fetch 1 user by ID
- Load a user's posts → fetch all posts by user_id, ordered by time
- Load the feed → fetch recent posts from everyone the user follows
- Load comments on a post → fetch all comments by post_id, ordered by time
- Check if user liked a post → yes/no lookup per post per user
- Count followers → count rows in follows where following_id = user

> [!important] Schema serves queries — not the other way around
> If you design your schema first and figure out queries later, you'll end up with expensive joins and full table scans on your hottest read paths. Always establish access patterns before writing a single table.

---

### Step 4 — Design the schema

Now you write the schema — but every decision is justified by your access patterns:

- Which columns to index → driven by your WHERE clauses
- Composite index column order → driven by your most common filter + sort
- Whether to normalize or denormalize → driven by join cost on hot queries
- UUID vs auto-increment → driven by whether you'll shard
- What to cache in Redis → driven by your hottest, most repeated queries

---

## The one-line rule for interviews

> "Before I design the schema, let me first identify the entities from the requirements, map the relationships, and define the access patterns — because my schema will be shaped around what the system needs to query."

Saying this out loud signals to the interviewer that you have a process. That alone puts you ahead of most candidates.
