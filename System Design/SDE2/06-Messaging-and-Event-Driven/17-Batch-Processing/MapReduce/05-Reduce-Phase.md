## What Reduce Does

After Shuffle, each reducer machine has all pairs for its assigned keys, grouped into lists:

```
Reducer A:  (ERROR_404, [1, 1, 1, 1, 1, 1, 1])
Reducer B:  (ERROR_500, [1, 1, 1, 1])
Reducer C:  (ERROR_503, [1, 1, 1])
```

Reduce sums each list and writes the final result to HDFS:

```
Reducer A:  ERROR_404 → 7
Reducer B:  ERROR_500 → 4
Reducer C:  ERROR_503 → 3
```

---

## The Reduce Function (Code)

```python
def reduce(key, values):
    emit(key, sum(values))
```

You write this. The framework calls it once per key, passing the full list of values collected during Shuffle.

---

## Full End-to-End Flow

```mermaid
flowchart TD
    subgraph Input
        F1[Machine 1\nERROR_404\nERROR_500\nERROR_404]
        F2[Machine 2\nERROR_500\nERROR_404\nERROR_503]
        F3[Machine 3\nERROR_404\nERROR_503\nERROR_500]
    end

    subgraph Map Phase
        M1["(ERROR_404,1)\n(ERROR_500,1)\n(ERROR_404,1)"]
        M2["(ERROR_500,1)\n(ERROR_404,1)\n(ERROR_503,1)"]
        M3["(ERROR_404,1)\n(ERROR_503,1)\n(ERROR_500,1)"]
    end

    subgraph Shuffle Phase
        S1["Reducer A\nERROR_404 → [1,1,1]"]
        S2["Reducer B\nERROR_500 → [1,1,1]"]
        S3["Reducer C\nERROR_503 → [1,1]"]
    end

    subgraph Reduce Phase
        R1[ERROR_404 → 3]
        R2[ERROR_500 → 3]
        R3[ERROR_503 → 2]
    end

    F1 --> M1
    F2 --> M2
    F3 --> M3
    M1 & M2 & M3 --> S1
    M1 & M2 & M3 --> S2
    M1 & M2 & M3 --> S3
    S1 --> R1
    S2 --> R2
    S3 --> R3
```

---

## Summary: Each Phase's Job

| Phase | Input | Job | Output |
|-------|-------|-----|--------|
| **Map** | Raw lines | Label each line as `(key, 1)` | `(key, value)` pairs on local disk |
| **Shuffle** | Pairs scattered across machines | Group by key, route to reducer | Grouped lists per reducer |
| **Reduce** | `(key, [1,1,1,...])` per reducer | Sum the list | Final counts written to HDFS |

---

## You Only Write Two Functions

```python
def map(line):
    emit(line.strip(), 1)

def reduce(key, values):
    emit(key, sum(values))
```

The framework handles everything else: parallelism, data transfer, fault tolerance, disk I/O.
