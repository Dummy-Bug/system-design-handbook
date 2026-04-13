
> [!info] The core idea
> Instead of comparing every row, split the data into buckets and compute a hash for each bucket. A hash is a single number that represents all the data inside — if even one byte changes, the hash changes completely. Compare hashes first. Only drill into buckets where hashes differ.

---

## Splitting into buckets

Take 1 billion rows. Split them into 4 buckets of equal size:

```
Bucket 1: rows 1     – 250M
Bucket 2: rows 250M  – 500M
Bucket 3: rows 500M  – 750M
Bucket 4: rows 750M  – 1B
```

Now compute a hash of all the data inside each bucket — one single number per bucket:

```
Bucket 1 hash → a3f9
Bucket 2 hash → 7c21
Bucket 3 hash → b841
Bucket 4 hash → 2d67
```

---

## Comparing replicas using hashes

Now instead of sending 1 billion rows over the network, you exchange just 4 hashes between the two replicas and compare:

```
         Replica1   Replica2
Bucket1:  a3f9   ==  a3f9  ✓ same — skip entirely
Bucket2:  7c21   ==  7c21  ✓ same — skip entirely
Bucket3:  b841   ≠   f392  ✗ different — investigate
Bucket4:  2d67   ==  2d67  ✓ same — skip entirely
```

With 4 hash comparisons you have eliminated 750 million rows from consideration. Only Bucket 3 needs further investigation.

> [!important] Key property of hashes
> If the data inside a bucket is identical on both replicas — the hash is identical. If even a single byte differs — the hash is completely different. This makes hashes a perfect fingerprint for detecting divergence without revealing the actual data.
