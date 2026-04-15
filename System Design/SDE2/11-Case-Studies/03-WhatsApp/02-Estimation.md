
> [!info] The goal of estimation
> Estimation is not about getting exact numbers. It is about understanding the scale of the system so every design decision that follows is justified. One server or hundreds? Do we need sharding? Is bandwidth even a concern? Estimation answers all of that before you draw a single box.

---

## Assumptions — always state these out loud

```
MAU              → 500M users
DAU              → 20% of MAU = 100M DAU   (80/20 principle)
Messages per day → 10 messages per user per day

Total writes/day → 100M × 10 = 1B messages/day
```

> [!important] Why 20% DAU for a chat app?
> The 80/20 principle says roughly 20% of users are active on any given day. For a social/messaging app this is a reasonable floor — WhatsApp's actual DAU/MAU ratio is closer to 60-70% because messaging apps have very high daily engagement. Using 20% here is conservative and safe for an interview. If pushed, you can say "this is a lower bound — real engagement is likely higher."

---

## Write QPS

```
Messages per day = 1B
Seconds in a day = 86,400 ≈ 10^5

Write QPS (avg)  = 1B / 100,000 = 10,000 writes/sec = 10k/sec
Write QPS (peak) = 2× average   = 20k/sec
```

---

## Read QPS

Chat is one of the rare systems where **read:write ratio is close to 1:1**. Every message that is written is read exactly once by the recipient in the real-time delivery path. There's an additional read load from users scrolling through history, but the primary read path mirrors the write path.

```
Read QPS (avg)  ≈ 10k/sec
Read QPS (peak) ≈ 20k/sec
```

This is fundamentally different from a URL shortener (100:1 reads to writes) or a news feed (10:1). Chat is balanced because delivery is symmetric — every send has a corresponding receive.

---

## Storage

Each message stores:

```
Message text    →  ~100 bytes  (average text message)
Metadata        →  ~100 bytes  (sender, receiver, timestamp, conversation ID)
Message ID      →  ~16 bytes   (UUID or Snowflake ID)

Total per message → ~250 bytes (round up to account for overhead)
```

```
Messages per day  = 1B
Storage per day   = 1B × 250 bytes = 250 GB/day

Storage per year  = 250 GB × 365 ≈ 90 TB/year ≈ 100 TB/year
Storage (10 years) = 100 TB × 10  = 1 PB
```

> [!danger] Common mistake
> Do not forget to convert properly. 1B messages × 250 bytes is 250 *gigabytes*, not terabytes. The mistake usually happens when you confuse daily message count with per-second count — 1B per day is very different from 1B per second.

1 PB over 10 years is well beyond a single machine. The database will need to be sharded. You don't design that now — but you flag it so the interviewer knows you see it coming.

---

## Bandwidth

```
Write QPS       = 10,000 messages/sec
Payload per msg = 250 bytes

Write bandwidth = 10,000 × 250 bytes = 2.5 MB/s
```

2.5 MB/s is essentially nothing — a single commodity NIC handles this easily. **Text is tiny.** This is why WhatsApp could run on minimal infrastructure for years. The moment you add images or video, this number multiplies by thousands and bandwidth becomes the first constraint you hit.

---

## Summary

| Metric | Value |
|---|---|
| DAU | 100M |
| Write QPS | ~10k/sec (avg), ~20k/sec (peak) |
| Read QPS | ~10k/sec (avg), ~20k/sec (peak) |
| Storage | ~250 GB/day |
| Storage (1 year) | ~100 TB |
| Storage (10 years) | ~1 PB |
| Write Bandwidth | ~2.5 MB/s |

**Key implications:**
- Balanced read/write ratio → caching helps but is not as critical as in read-heavy systems
- 1 PB over 10 years → database sharding is required
- 2.5 MB/s bandwidth → bandwidth is not a bottleneck for text; changes dramatically if media is added

