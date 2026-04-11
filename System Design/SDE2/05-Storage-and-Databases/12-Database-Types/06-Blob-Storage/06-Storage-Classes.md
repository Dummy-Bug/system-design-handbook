## Not all files are accessed equally

Think about YouTube. A video uploaded today might get a million views in its first week. A video uploaded five years ago might get 10 views a month. Both files take up the same storage space — but one is being served constantly while the other is sitting untouched nearly all the time.

Should both cost the same to store? No. Charging the same rate for hot, constantly-accessed data and cold, rarely-accessed data would be wasteful and expensive.

This is the problem storage classes solve.

---

## The three tiers

S3 has different storage classes based on how frequently the data is accessed:

```
Access pattern        Storage class              Cost            Retrieval
─────────────────────────────────────────────────────────────────────────────
Accessed frequently   S3 Standard                Expensive        Instant
Accessed occasionally S3 Infrequent Access (IA)  Cheaper          Instant (small fee)
Rarely accessed       S3 Glacier                 Very cheap       Minutes to hours
```

The trade-off is simple: the less you pay to store, the longer you wait to retrieve.

- **S3 Standard** — your hot data. Videos getting millions of views, profile pictures, active documents. Instant access, highest cost per GB.
- **S3 Infrequent Access** — warm data. Files you still need but don't access daily. Cheaper storage, but you pay a small per-retrieval fee. If you access it rarely, you save money overall.
- **S3 Glacier** — cold data. Backups, archives, old videos with almost no traffic. Extremely cheap storage, but retrieval takes minutes to hours. You'd never use this for real-time serving — it's for compliance, archival, disaster recovery.

---

## Lifecycle policies — automatic tiering

You don't have to manually move files between storage classes. S3 supports **lifecycle policies** — rules that automatically transition objects based on age or access patterns.

```
Day 0:    Video uploaded → S3 Standard (hot)
Day 30:   If fewer than 100 views → move to S3 Infrequent Access
Day 365:  If fewer than 10 views → move to S3 Glacier
```

YouTube could implement exactly this — recent viral content stays in Standard, older unpopular content gets automatically archived to Glacier. If an old video suddenly goes viral (someone shares it), you move it back to Standard programmatically.

---

## Why this matters in interviews

Any time you're designing a system that stores files long-term — Dropbox, Google Photos, YouTube, a backup system — storage costs are a real concern at scale. Storing petabytes of cold data in S3 Standard when it's barely accessed is throwing money away.

Mentioning storage classes and lifecycle policies shows you're thinking about operational cost alongside functional correctness.

> [!tip] Interview framing
> "For media storage I'd use S3 with lifecycle policies — recent content stays in Standard for instant access, content older than 30 days with low view counts gets moved to Infrequent Access, and anything archived for compliance goes to Glacier. This keeps storage costs proportional to actual usage."
