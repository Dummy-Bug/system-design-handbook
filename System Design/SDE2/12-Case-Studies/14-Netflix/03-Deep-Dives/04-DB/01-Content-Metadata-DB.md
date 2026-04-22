## What Is Content Metadata

When a user opens Netflix and browses titles, or clicks on a movie to see its detail page, the app needs to show: title, genre, description, cast (actors, directors, producers), release year, CDN URL for the trailer, S3 URL for the actual chunks. None of this is video — it is structured text data describing the content. This is **content metadata**.

The database design question is: which DB do you pick to store this, and why?

---

## Access Patterns — Read Overwhelmingly Dominates

Before picking a DB, you have to understand how the data is actually used.

Netflix has ~20,000 titles. A new title is uploaded maybe a few hundred times a day. But reads are constant and massive:

```
Top 10 thrillers query    → read
Latest releases query     → read
Movie detail page load    → read
Search results            → read
Homepage recommendations  → read
```

Every user browsing Netflix is generating read queries. Every user clicking a title generates a read. Writes happen when Netflix ingests a new title or updates metadata — maybe a few hundred times a day across the entire catalogue.

This is a heavily **read-optimised** workload. The DB choice must reflect that.

---

## Eliminating Wide Column (Cassandra)

Wide column databases like Cassandra are optimised for high-throughput writes — millions of writes per second distributed across nodes. They are designed for append-heavy workloads: sensor data, event logs, time-series.

Content metadata is the opposite — low write volume, high read volume, complex queries (filter by genre, sort by release date, fetch full cast). Wide column DBs sacrifice query flexibility for write throughput. That trade-off is wrong here.

**Wide column is eliminated.**

---

## Sizing — Do We Even Need a Distributed DB?

Before choosing between relational and document databases, calculate the actual data size. This matters because distributed databases (Cassandra, MongoDB's sharded mode) add operational complexity — and that complexity is only worth it if the data volume justifies it.

Netflix has ~20,000 titles. 60% are TV series with multiple episodes, 40% are movies.

**TV Series (12,000 titles):**

Each episode has its own description, CDN URL, S3 URL, episode title. Assume an average of 10 episodes per series, 5 seasons:

```
Episodes per series = 10 episodes × 5 seasons = 50 episodes
Total episodes      = 12,000 series × 50       = 600,000 episodes
Metadata per episode ≈ 200 bytes (description + URLs + title)

Total = 600,000 × 200B = 120,000,000 bytes = 120 MB
```

The series-level data (cast, genre, overall description) is shared across all episodes — stored once per series, not per episode.

**Movies (8,000 titles):**

```
Metadata per movie ≈ 500 bytes (longer description, full cast, URLs)

Total = 8,000 × 500B = 4,000,000 bytes = 4 MB
```

**Total content metadata: ~124 MB.**

This fits comfortably in the RAM of a single database server, let alone on disk. There is no sharding problem here. The entire Netflix content catalogue — every title, every episode, every cast member — is less than 200 MB of structured text.

> [!important] Why this calculation matters
> The moment you establish that 124 MB fits on one server, "MongoDB is already distributed" stops being a relevant argument. Distributed architecture solves a scale problem. There is no scale problem here. Choosing a distributed DB for 124 MB of data adds operational overhead — sharding, replication configuration, eventual consistency trade-offs — with zero benefit.

---

## MongoDB vs Relational — The Real Analysis

With sharding off the table, the question becomes purely: which DB models this data better?

**The case for MongoDB:**

Movie metadata looks like a natural document. One movie, one JSON object — title, genre, description, cast array, URLs all nested inside. A single read returns everything. No joins needed.

```json
{
  "title": "Inception",
  "genre": "Thriller",
  "description": "A thief who steals corporate secrets...",
  "cast": [
    { "name": "Leonardo DiCaprio", "role": "Actor" },
    { "name": "Christopher Nolan", "role": "Director" }
  ],
  "cdn_url": "https://cdn.netflix.com/inception/",
  "s3_url": "https://s3.amazonaws.com/netflix/inception/"
}
```

This looks clean. But the moment you think about actors appearing in multiple movies, the model breaks.

**Where MongoDB embedding breaks down:**

Christian Bale appears in 40+ films. If you embed his data inside every movie document, you store his name, photo URL, and bio 40 times. Now Netflix updates his profile photo — you have to find and update 40 documents simultaneously and keep them consistent. This is a write amplification and consistency problem.

The fix is to store actors as separate documents and reference them by ID — exactly like a foreign key in a relational DB:

```json
{
  "title": "Inception",
  "cast": ["actor_id_123", "actor_id_456"]
}
```

But now when the movie detail page loads, the app has to:
1. Fetch the movie document
2. Parse the cast ID array
3. Fire N separate queries to fetch each actor document
4. Join them in application code

You have re-invented SQL joins — but in application code, with no query optimiser, no index hints, and no foreign key guarantees. You get all the complexity of relational data modelling with none of the tooling that relational databases provide for it.

**The case for PostgreSQL:**

Movie metadata has a well-defined, consistent schema. Every title has a genre, a description, a release year, a set of cast members. There are no unpredictable fields, no flexible nested structures that vary title by title. The schema does not need flexibility — it needs correctness.

Relational databases handle actor-to-movie relationships natively:

```
movies  table → movie_id, title, genre, description,release_year

actors  table → actor_id, name, bio, photo_url

roles   table → movie_id, actor_id, role_type (actor/director/producer)
```

Fetching the full movie detail page is one query with joins — handled by the DB engine with full query optimisation and index support.

The schema is also enforced by the DB itself. If a movie is inserted without a genre, the DB rejects it. If an actor reference points to a non-existent actor, the DB rejects it. Data integrity is guaranteed at the storage layer, not left to the application to enforce.

---

## The Verdict — PostgreSQL

```
MongoDB wins when:
  → Schema is unpredictable or varies wildly across documents
  → Data is truly hierarchical and self-contained (no cross-document relationships)
  → Data has no natural relationships AND write volume requires horizontal scaling

PostgreSQL wins when:
  → Schema is well-defined and consistent
  → Data has natural relationships (actors ↔ movies)
  → Data volume does not require sharding
  → Data integrity constraints add real value
```

Netflix content metadata is 124 MB, has a fixed schema, and has natural many-to-many relationships between actors and movies. Every MongoDB advantage either does not apply or actively works against this use case.

**PostgreSQL is the correct choice for content metadata.**

> [!info] What about read performance?
> PostgreSQL on a single server with proper indexes handles tens of thousands of read queries per second — far more than Netflix's content metadata queries generate. If read load grows, a read replica handles it. Sharding is never needed for 124 MB of data regardless of query volume.
