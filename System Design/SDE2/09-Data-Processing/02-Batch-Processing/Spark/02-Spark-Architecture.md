## Two Types of Nodes

```
┌─────────────────────────────────────────────┐
│  Driver Node                                │
│  - stores the recipe (lineage)              │
│  - coordinates all workers                  │
│  - detects worker failures                  │
│  - triggers recomputation on failure        │
└───────────────────┬─────────────────────────┘
                    │ sends recipe + instructions
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      Worker 1   Worker 2   Worker 3
      (RAM)      (RAM)      (RAM)
      chunk 1    chunk 2    chunk 3
```

**Driver node** — the master. Holds the lineage (recipe of all transformations). Coordinates which worker handles which partition. Detects failures and triggers recovery.

**Worker nodes** — the compute. Each loads its data partition into RAM, executes transformations, and passes results directly to the next step in RAM — no disk involved.

---

## Full Flow With Example

1TB error logs, 3 worker nodes, job: filter errors → count per type → sort.

**Step 1 — Driver splits data:**
```
Worker 1 → loads chunk 1 into RAM
Worker 2 → loads chunk 2 into RAM
Worker 3 → loads chunk 3 into RAM
```

**Step 2 — Driver sends recipe to all workers:**
```
"filter lines starting with ERROR, then count per type, then sort by count"
```

**Step 3 — Workers execute in RAM:**
```
Worker 1 RAM:  filter → [ERROR_404, ERROR_500, ERROR_404] → count → {ERROR_404:2, ERROR_500:1}

Worker 2 RAM:  filter → [ERROR_500, ERROR_404]            → count → {ERROR_500:1, ERROR_404:1}

Worker 3 RAM:  filter → [ERROR_503, ERROR_404, ERROR_500] → count → {ERROR_503:1, ERROR_404:1, ERROR_500:1}
```

No disk between steps — all in RAM.

**Step 4 — Shuffle (in RAM):**
```
All ERROR_404 counts → Worker 1 → sums → 4
All ERROR_500 counts → Worker 2 → sums → 3
All ERROR_503 counts → Worker 3 → sums → 1
```

**Step 5 — Write final output to HDFS/S3.**

---

## Lineage: Fault Tolerance Without Replication

Instead of replicating intermediate data across nodes, Spark stores the **recipe** on the driver — the exact sequence of transformations applied to produce each result.

```
Driver lineage:
  chunk 1 → filter(ERROR) → count → {ERROR_404:2, ERROR_500:1}
  chunk 2 → filter(ERROR) → count → {ERROR_500:1, ERROR_404:1}
  chunk 3 → filter(ERROR) → count → {ERROR_503:1, ERROR_404:1, ERROR_500:1}
```

The recipe is just metadata — kilobytes, not gigabytes. Cheap to store.

**Worker 1 crashes:**
```
Driver detects failure
Driver: "Worker 1 lost its result — recipe says filter + count on chunk 1"
New worker: re-reads chunk 1 from HDFS/S3, reruns filter + count in RAM
Result restored
```

Only the lost partition is recomputed — not the whole job.

---

## What If The Driver Crashes?

The entire job fails — the driver holds the lineage. This is a known limitation.

Solution: **checkpointing** — periodically save lineage + intermediate results to disk (S3/HDFS). If driver crashes, resume from last checkpoint instead of restarting from scratch.
