## The Network Bottleneck

In basic MapReduce, Map emits one pair per line:

```
1000 machines × 1M lines each = 1,000,000,000 pairs going to Shuffle
```

All 1 billion pairs get transferred over the network to reducer machines. This is the most expensive part of a MapReduce job — network I/O at scale is slow and costly.

The question: **can we reduce the number of pairs before they hit the network?**

---

## The Combiner: Local Sum First

Instead of emitting `(key, 1)` per line, each mapper machine builds a local frequency map first, then emits one pair per unique key:

**Without Combiner — Machine 1:**
```
(ERROR_404, 1)
(ERROR_500, 1)
(ERROR_404, 1)
(ERROR_404, 1)
(ERROR_500, 1)
→ 5 pairs sent over network
```

**With Combiner — Machine 1:**
```
local count: { ERROR_404: 3, ERROR_500: 2 }
→ (ERROR_404, 3)
→ (ERROR_500, 2)
→ 2 pairs sent over network
```

---

## At Scale

```
Without Combiner:  1000 machines × 1M pairs  =  1,000,000,000 pairs to shuffle
With Combiner:     1000 machines × ~3 pairs   =  ~3,000 pairs to shuffle
```

~333,000x reduction in network traffic. Shuffle becomes almost free.

---

## Early Filtering: Don't Emit What You Don't Need

Another Map-phase optimization — filter out irrelevant lines before emitting anything:

```python
def map(line):
    if not line.startswith("ERROR"):
        return          # skip non-error lines, emit nothing
    emit(line.strip(), 1)
```

No pair emitted → nothing sent to Shuffle → Reducer never sees it.

Combined with Combiner:

```python
def map(lines):
    counts = {}
    for line in lines:
        if not line.startswith("ERROR"):
            continue                          # filter early
        key = line.strip()
        counts[key] = counts.get(key, 0) + 1
    for key, count in counts.items():
        emit(key, count)                      # emit local count, not 1
```

---

## Rule of Thumb

> Filter early. Aggregate locally. The less data that hits the network, the faster the job.

Both optimizations happen on the mapper machine — before any network transfer. This is always the best place to reduce data volume.

---

## Important Note

Combiner only works when the aggregation function is **associative and commutative** — meaning the order doesn't matter and partial results can be combined.

- Sum ✅ — `(3 + 2) + 4 = 3 + (2 + 4)`
- Count ✅
- Average ❌ — `avg(3,2) + avg(4)` ≠ `avg(3,2,4)` — can't pre-average
