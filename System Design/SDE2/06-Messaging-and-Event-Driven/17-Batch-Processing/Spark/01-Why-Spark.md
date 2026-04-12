## The MapReduce Disk Bottleneck

MapReduce writes intermediate results to disk between every phase:

```
Map → disk → Shuffle → disk → Reduce → disk
```

Disk is 100x slower than RAM. For a 5-step pipeline that's 10 disk reads/writes before you get your answer. This is why MapReduce jobs take **minutes to hours**.

---

## What Spark Does Differently

Spark keeps all intermediate results **in RAM**. Disk is only touched at the start (read input) and end (write output).

```
MapReduce:   Map → disk → Shuffle → disk → Reduce → disk
Spark:       Map → RAM  → Shuffle → RAM  → Reduce → disk (final output only)
```

RAM access is ~100x faster than disk. Result: Spark is **10–100x faster** than MapReduce for the same job.

---

## When To Use Spark vs MapReduce

| | MapReduce | Spark |
|---|---|---|
| Speed | Slow (disk I/O) | Fast (in-memory) |
| Iterative workloads | Bad — reads/writes disk every iteration | Great — stays in RAM |
| Memory requirement | Low — spills to disk | High — needs enough RAM |
| Fault tolerance | Re-read from disk | Recompute from lineage |
| Use case | Simple batch ETL, large data that doesn't fit in RAM | ML training, iterative analytics, fast batch jobs |

**Key interview point:** "For the nightly billing report I'd use Spark — process the raw event log from S3 in memory for fast exact counts. MapReduce would work too but Spark is significantly faster for iterative aggregations."
