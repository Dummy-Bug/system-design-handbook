# Capacity Estimation

## Starting assumptions

World population is ~10 billion. Assume 1 billion of them are active users who each perform ~100 actions per day that need to be recorded in a database — a tweet, a message, a purchase, a like, anything that needs a unique ID.

```
Daily IDs needed = 1B users × 100 actions = 100B IDs/day
```

## IDs per second

There are ~86,400 seconds in a day, approximated to 100,000 for easier math:

```
Sustained throughput = 100B / 100,000 = 1M IDs/second
```

For peak traffic (viral events, flash sales, etc.), assume 10x spike:

```
Peak throughput = 10M IDs/second
```

## IDs over 10 years

To verify the ID space is large enough for the long term:

```
365 days × 10 years ≈ 400 × 10 years (rounded up)
400 × 10 × 100B = 400 trillion IDs over 10 years
             = 4 × 10^14 total IDs
```

## Storage

If each ID is 8 bytes:

```
400 trillion × 8 bytes = 3,200 PB = 3.2 EB over 10 years
```

> [!important] The ID generator doesn't store IDs
> This service generates and returns IDs — it doesn't persist them. The caller's database stores them. So 3.2 EB is the storage burden on the *calling systems*, not on this service. Storage is not a design constraint for the generator itself.

The 10x peak factor applies only to **throughput**, not storage. Traffic spikes mean more IDs per second — not more total IDs over 10 years.

## Summary

| Metric | Value |
|---|---|
| Daily IDs | 100 billion |
| Sustained throughput | ~1M IDs/sec |
| Peak throughput | ~10M IDs/sec |
| Total IDs over 10 years | ~400 trillion |
| Storage (caller side) | ~3.2 EB |
| Storage (this service) | negligible |
