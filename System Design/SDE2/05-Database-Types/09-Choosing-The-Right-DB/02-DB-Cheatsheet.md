# Database Cheatsheet — Every DB, Its Type, and Its Managed Twin

> [!info] How to read this
> Every database fits into a category. Within each category, there are self-managed (open-source, you run it) and managed (cloud provider runs it for you) versions. The mental model and data model are the same — the difference is who operates it.

---

## Relational (SQL)

Row-oriented storage. ACID transactions. Schema-on-write. Optimized for low-latency reads and writes on individual rows. The default choice unless your access pattern or scale argues otherwise.

| Database | Type | Notes |
|---|---|---|
| PostgreSQL | Self-managed | Most popular open-source relational DB |
| MySQL | Self-managed | Widely used in web stacks |
| Oracle DB | Self-managed | Enterprise, heavily used in banking/finance |
| Amazon RDS | Managed (AWS) | Managed MySQL / PostgreSQL — same engine, AWS runs it |
| Amazon Aurora | Managed (AWS) | AWS's own MySQL/Postgres-compatible engine, faster replication |
| Cloud SQL | Managed (GCP) | Managed MySQL / PostgreSQL on GCP |
| Azure SQL | Managed (Azure) | Managed SQL Server on Azure |

```
MySQL  →  RDS MySQL      same engine, AWS operates it
MySQL  →  Aurora         AWS-built engine, MySQL-compatible, better performance
```

---

## Key-Value Stores

The simplest model — one key maps to exactly one value. Extremely fast point lookups. Used for caching, sessions, counters.

> [!important] True key-value means one key → one thing back
> Redis is a true key-value store. One key, one value (or one data structure like a sorted set). DynamoDB is often marketed as key-value but it's actually wide-column — a partition key can return multiple items, and a sort key range returns a sorted slice of items. See Wide-Column below.

| Database | Type | Notes |
|---|---|---|
| Redis | Self-managed | In-memory, supports strings, lists, sorted sets, hashes |
| Memcached | Self-managed | Pure in-memory cache, simpler than Redis |
| Amazon ElastiCache | Managed (AWS) | Managed Redis or Memcached — same engines, AWS runs it |

---

## Wide-Column Stores

Partition key routes to the right node. Sort key orders data within a partition. Optimized for extremely high write throughput. No joins. One table per query pattern.

| Database | Type | Notes |
|---|---|---|
| Apache Cassandra | Self-managed | LSM tree, tunable consistency, runs anywhere |
| ScyllaDB | Self-managed | Cassandra-compatible, rewritten in C++, faster |
| Amazon DynamoDB | Managed (AWS) | AWS's version of Cassandra — same problem space, proprietary internals |
| Apache HBase | Self-managed | Wide-column on top of Hadoop/HDFS |
| Google Bigtable | Managed (GCP) | Google's managed wide-column store, inspired the Cassandra design |

```
Cassandra  →  DynamoDB     same problem space (high-throughput writes, partition key model)
                            different internals, DynamoDB is AWS-only and fully managed
Cassandra  →  Bigtable      Google's managed equivalent
```

> [!important] DynamoDB is AWS's Cassandra
> DynamoDB and Cassandra solve the same class of problems — wide-column, partition key routing, high write throughput. The difference is operational: Cassandra runs anywhere and you manage it. DynamoDB is AWS-only and fully managed. AWS didn't just host Cassandra — they built their own system, but the lineage comes from the same 2007 Amazon Dynamo paper that also inspired Cassandra.

---

## Document Stores

Data stored as JSON/BSON documents. Flexible schema — no fixed columns. Great when an entity is read and written as a whole unit (e.g. a user profile with nested addresses).

| Database | Type | Notes |
|---|---|---|
| MongoDB | Self-managed | Most popular document store |
| CouchDB | Self-managed | HTTP-native, multi-master replication |
| Amazon DocumentDB | Managed (AWS) | MongoDB-compatible, AWS runs it |
| Firestore | Managed (GCP) | Google's managed document store, used in mobile apps |

```
MongoDB  →  DocumentDB    MongoDB-compatible API, AWS operates it
```

---

## Search Engines

Inverted index model. Optimized for full-text search, ranking, filtering. Not the source of truth — data is synced from your primary DB into the search index.

| Database | Type | Notes |
|---|---|---|
| Elasticsearch | Self-managed | Most widely used search engine |
| OpenSearch | Self-managed | AWS-backed open-source fork of Elasticsearch |
| Apache Solr | Self-managed | Older, built on Lucene like Elasticsearch |
| Amazon OpenSearch Service | Managed (AWS) | Managed OpenSearch/Elasticsearch |

```
Elasticsearch  →  OpenSearch Service    same engine, AWS operates it
```

---

## NewSQL

Distributed databases that give you SQL ergonomics + horizontal scale + strong consistency (ACID). Best of both worlds — but operationally complex and expensive.

| Database | Type | Notes |
|---|---|---|
| CockroachDB | Self-managed | Distributed, ACID, Postgres-compatible |
| YugabyteDB | Self-managed | Distributed, ACID, Postgres + Cassandra-compatible |
| Google Spanner | Managed (GCP) | Google's globally distributed ACID DB, TrueTime |
| Amazon Aurora DSQL | Managed (AWS) | AWS's distributed SQL with ACID guarantees |
| TiDB | Self-managed | MySQL-compatible distributed SQL, popular in Asia |

---

## Graph Databases

Nodes and edges. Optimized for relationship traversal — finding connections between entities. Use when the relationship IS the query (social graphs, fraud networks, recommendations).

| Database | Type | Notes |
|---|---|---|
| Neo4j | Self-managed | Most popular graph DB |
| Amazon Neptune | Managed (AWS) | Managed graph DB on AWS |
| JanusGraph | Self-managed | Distributed graph DB on top of Cassandra or HBase |

---

## Time-Series Databases

Optimized for append-only sequential writes with a timestamp. Used for metrics, monitoring, IoT sensor data, financial tick data.

| Database | Type | Notes |
|---|---|---|
| InfluxDB | Self-managed | Most popular time-series DB |
| TimescaleDB | Self-managed | Time-series extension on top of Postgres |
| Prometheus | Self-managed | Metrics scraping + storage, used with Grafana |
| Amazon Timestream | Managed (AWS) | Managed time-series on AWS |

---

## OLAP / Data Warehouses

Column-oriented storage. Optimized for scanning billions of rows and computing aggregations. Not for live user traffic — for analysts and dashboards. Data flows in from OLTP via ETL/CDC.

| Database | Type | Notes |
|---|---|---|
| ClickHouse | Self-managed | Extremely fast columnar DB, real-time analytics |
| Apache Druid | Self-managed | Real-time analytics on event streams |
| Apache Hive | Self-managed | SQL on Hadoop for batch analytics |
| Snowflake | Managed (Multi-cloud) | Cloud-agnostic data warehouse, very popular |
| BigQuery | Managed (GCP) | Google's serverless columnar warehouse |
| Amazon Redshift | Managed (AWS) | AWS columnar warehouse |

---

## Blob / Object Storage

Stores raw files — images, videos, backups, large documents. Not a database. Metadata lives in your DB; the bytes live here.

| Database | Type | Notes |
|---|---|---|
| Amazon S3 | Managed (AWS) | The default object store |
| Google Cloud Storage | Managed (GCP) | GCP equivalent of S3 |
| Azure Blob Storage | Managed (Azure) | Azure equivalent of S3 |
| MinIO | Self-managed | S3-compatible, runs on your own hardware |

---

## The one-line summary

```
Relational       →  Postgres / MySQL           →  RDS / Aurora (AWS)
Wide-Column      →  Cassandra / ScyllaDB       →  DynamoDB (AWS), Bigtable (GCP)
Document         →  MongoDB                    →  DocumentDB (AWS), Firestore (GCP)
Search           →  Elasticsearch              →  OpenSearch Service (AWS)
NewSQL           →  CockroachDB / YugabyteDB   →  Spanner (GCP)
Graph            →  Neo4j                      →  Neptune (AWS)
Time-Series      →  InfluxDB / TimescaleDB     →  Timestream (AWS)
OLAP             →  ClickHouse / Druid         →  BigQuery (GCP), Redshift (AWS)
Object Storage   →  MinIO                      →  S3 (AWS), GCS (GCP)
```
