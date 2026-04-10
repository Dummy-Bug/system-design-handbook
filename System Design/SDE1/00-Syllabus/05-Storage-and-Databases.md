## Phase 5 - Storage and Databases

> HLD relevance: every serious design needs a clear storage choice.
> At SDE-1 level, you should be able to choose between SQL, NoSQL, cache, and object storage for practical reasons, not buzzwords.

### 5.1 Database fundamentals
- structured vs semi-structured vs unstructured data
- schema-on-write vs schema-on-read
- row-oriented vs column-oriented intuition
- metadata vs blob separation

### 5.2 ACID properties
- atomicity
- consistency
- isolation
- durability
- know why money movement and reservations usually need ACID

### 5.3 SQL databases
- tables, rows, primary keys, foreign keys
- normalization
- denormalization for read-heavy systems
- joins and when they are useful
- SQL is the default unless access pattern says otherwise

### 5.4 Indexing basics
- why indexes speed up reads
- primary vs secondary index
- composite index and leftmost-prefix intuition
- too many indexes slow writes

### 5.5 NoSQL basics
- key-value stores
- document stores
- wide-column stores at a high level
- use NoSQL because of access pattern or scale needs, not fashion

### 5.6 Replication
- primary-replica
- read replicas
- replication lag
- stale reads from replicas

### 5.7 Sharding
- why a single database eventually becomes too large or too hot
- shard key selection
- hot-partition risk
- cross-shard queries are hard

### 5.8 Object and blob storage
- images, videos, files, backups
- metadata in DB, file in object store
- pre-signed upload/download URL pattern

### 5.9 Data modeling basics
- design from access patterns
- users, posts, comments, messages, orders
- think about read path and write path separately

### 5.10 What SDE-1 should confidently say
- "I would start with Postgres or MySQL here"
- "I would store images in S3 and metadata in SQL"
- "I would add read replicas before redesigning the whole system"
- "I would shard only when one DB is no longer enough"

