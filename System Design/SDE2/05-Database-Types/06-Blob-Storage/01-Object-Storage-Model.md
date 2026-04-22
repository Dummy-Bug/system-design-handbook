> [!info] Object storage is a system designed for one thing only — storing massive, unstructured files cheaply and reliably. No queries, no rows, no schema. Just: put file in, get key back. Use key to get file. Dumb but powerful.

## The problem with storing files in a database

Imagine you're building YouTube. A user uploads a 500MB video. Your first instinct is natural — store it in the database like everything else.

The problem is that a database like Postgres is built for **structured data** — rows, columns, IDs, text. It understands what's inside your data and can query it. A 500MB video is just a blob of raw bytes. No rows. No columns. No structure the database can reason about.

You technically *can* shove a file into a database via a BLOB or BYTEA column. But here's what happens when you do:

- Every read of that video pulls 500MB through your database connection pool
- Your DB's RAM fills up with video bytes instead of query caches and indexes
- Backups become enormous
- 1,000 users watching simultaneously means 500GB/s flowing through your database

The database chokes. It was never designed for this.

## What object storage is

Object storage is a completely different kind of system — built specifically for large, unstructured files. Amazon S3 is the most famous example.

Think of it like a **massive, flat filing cabinet in the cloud**.
- You put a file in → you get back a **unique key** (essentially a path like `videos/user_42/intro.mp4`)
- You want the file later → you use that key to fetch it

That's it. No tables. No rows. No queries. No schema. S3 has absolutely no idea what's inside your file — it doesn't care if it's a video, a medical PDF, a zip archive, or a trained ML model. It just stores bytes and gives them back when asked.

> [!info] Object storage vs Document store
> A document store like MongoDB also stores flexible data without a fixed schema — but it still **understands** what's inside. It can query fields, filter by values, index properties. Object storage is completely **opaque**. It cannot look inside the file, cannot filter by content, cannot search. The trade-off is: document stores handle smaller structured documents; object storage handles massive unstructured files.

---

## The two-layer pattern

Because object storage can only fetch by key, you need a way to find the right key in the first place. That's where your regular database comes in.

The pattern is: **your DB stores the pointer, S3 stores the file**.

```
User uploads video
→ Upload goes to S3
→ S3 returns key: "videos/user_42/intro.mp4"
→ You save that key in Postgres alongside the user's record

User wants to watch the video
→ Look up key in Postgres: SELECT video_key FROM videos WHERE id = 123
→ Use key to fetch the actual file from S3
→ S3 streams the bytes directly to the user
```

Your database never touches the video bytes. It only stores a short string — the key. This is efficient and clean. The heavy lifting (storing and serving gigabytes) is entirely S3's job.

---

## Flat namespace

One important detail: object storage has a **flat namespace**. There are no real folders or directories — just buckets and keys.

```
Bucket: my-youtube-videos
Key:    videos/user_42/intro.mp4
```

The `/` in the key is just a naming convention — i**t looks like a folder path but S3 treats it as a plain string**. The entire storage system is one giant flat list of keys inside a bucket.

This is different from a filesystem where directories actually exist as objects. In S3, "folders" are an illusion created by key prefixes.

> [!important] What object storage guarantees
> - Store any file of any size (S3 supports up to 5TB per object)
> - Retrieve it by key with high availability
> - Durable storage (S3 replicates across multiple availability zones — 99.999999999% durability)
>
> What it does NOT guarantee:
> - Queryability — you cannot ask "give me all files uploaded by user 42" without maintaining that index yourself elsewhere
> - Low latency for small reads — a relational DB with an index is faster for tiny structured lookups
