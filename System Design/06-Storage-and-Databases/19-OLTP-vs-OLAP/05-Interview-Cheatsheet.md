# Interview Cheatsheet — OLTP vs OLAP

> [!question] What is OLTP and when do you use it?
>> [!success]-
>> OLTP (Online Transaction Processing) is your production database — the one serving live users. Every operation is small and fast: insert a row, fetch a user by ID, update a column. Thousands of these happen per second, each touching very few rows. PostgreSQL, MySQL, and DynamoDB are OLTP databases. Row-oriented storage makes single-row reads fast.

---

> [!question] What is OLAP and when do you use it?
>> [!success]-
>> OLAP (Online Analytical Processing) is a separate database built for heavy analytics — full table scans, aggregations, GROUP BY across billions of rows. It serves analysts and dashboards, never live users. BigQuery, Redshift, and Snowflake are OLAP databases. Column-oriented storage means only the queried columns are read off disk, making scans dramatically faster.

---

> [!question] Why can't you run analytics on your production database?
>> [!success]-
>> A full table scan at scale — say, COUNT across 500M rows — consumes disk I/O and CPU for minutes. It competes with live user queries for the same resources. The production database slows down, users experience latency spikes and timeouts. Analytics must run on a separate OLAP warehouse isolated from live traffic.
>>
>> > [!tip] Interview framing
>> > "Running analytics on the production OLTP database is a classic mistake. At scale, a single GROUP BY query can cause a full table scan that starves live user traffic. The right pattern is to replicate data into a separate OLAP warehouse — analysts query that, production is never touched."

---

> [!question] Why is column-oriented storage faster for analytics?
>> [!success]-
>> Analytics queries typically touch 2–3 columns out of 20+. In row-oriented storage, reading any column means loading the entire row off disk — including all the columns you don't need. At 500M rows, that's gigabytes of wasted I/O. Column-oriented storage keeps all values of a column together, so a query that only needs `country` reads only the country column — a fraction of the data.

---

> [!question] How do you keep the OLAP warehouse up to date?
>> [!success]-
>> Two options: ETL and CDC.
>>
>> **ETL** — a batch job runs every few hours, extracts changed rows from OLTP, transforms them, and loads them into the warehouse. Simple but data is hours stale.
>>
>> **CDC** — Change Data Capture reads the database write log (WAL/binlog), publishes every change to Kafka, and a consumer writes it into the warehouse in near real-time (seconds of lag). More complex but dramatically fresher.
>>
>> > [!tip] Interview framing
>> > "For real-time use cases like fraud detection, CDC via Kafka gives seconds of lag. For batch reporting and BI dashboards, ETL every few hours is simpler and sufficient."

---

> [!question] When would you mention OLAP in an interview?
>> [!success]-
>> Any time the interviewer asks about analytics, reporting, or dashboards. The pattern is always: production OLTP DB → CDC or ETL pipeline → OLAP warehouse → analytics queries run there. Never say "we'll run reports against the main database."

---

## Quick Reference

| | OLTP | OLAP |
|---|---|---|
| Purpose | Serve live users | Serve analysts |
| Operations | Small, fast, single-row | Large scans, aggregations |
| Storage | Row-oriented | Column-oriented |
| Examples | PostgreSQL, MySQL, DynamoDB | BigQuery, Redshift, Snowflake |
| Latency | Milliseconds | Seconds to minutes |

```
Live users
    ↓
OLTP DB (PostgreSQL)     ← row-oriented, fast for single row ops
    ↓  CDC (seconds lag) or ETL (hours lag)
OLAP DB (BigQuery)       ← column-oriented, fast for full column scans
    ↑
Analysts / dashboards
```
