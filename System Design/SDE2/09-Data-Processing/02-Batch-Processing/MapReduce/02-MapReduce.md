MapReduce is a programming model for processing large datasets in parallel across many machines. Google invented it in 2004 to process petabytes of web crawl data.

The core idea: **bring computation to the data, not data to the computation.**

Each machine processes its local chunk. The framework coordinates everything else.

---

## The 3 Phases

There are only two types of machines: **mapper machines** and **reducer machines**. shuffle is just the name for the data transfer process between them.

```
┌─────────────────────────────────────────────────────────┐
│  Input Data (1TB across 1000 machines)                  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  MAP PHASE  (runs on mapper machines)                   │
│  Each machine reads its local chunk                     │
│  Emits (key, value) pairs                               │
│  Writes pairs to local disk                             │
└─────────────────────┬───────────────────────────────────┘
                      │  SHUFFLE = mapper machines directly
                      │  send pairs to reducer machines
                      │  over the network
                      ▼
┌─────────────────────────────────────────────────────────┐
│  REDUCE PHASE  (runs on reducer machines)               │
│  Each reducer receives all pairs for its assigned keys  │
│  Groups them, aggregates, writes results to HDFS        │
└─────────────────────────────────────────────────────────┘
```

---

## Hadoop = MapReduce + HDFS

MapReduce is the computation model. It needs a distributed file system to store input data and results.

**HDFS (Hadoop Distributed File System)** — open-source distributed storage:
- Splits files into 128MB blocks
- Replicates each block across 3 machines
- MapReduce reads input from HDFS, writes output back to HDFS

Hadoop = HDFS + MapReduce. The open-source implementation of Google's original paper.

---

## The Core Limitation

Between every phase, data is **written to and read from disk**:

```
Map → disk → Shuffle → disk → Reduce → disk
```

Expanded:
```
Map output    → written to local disk
Shuffle       → read from disk, transferred over network, written to disk
Reduce input  → read from disk
Reduce output → written to HDFS
```

For a 5-step pipeline, that's 10 disk reads/writes. Disk I/O is slow — this is why MapReduce jobs take **minutes to hours**, not seconds.

This limitation is exactly what Spark was built to solve.
