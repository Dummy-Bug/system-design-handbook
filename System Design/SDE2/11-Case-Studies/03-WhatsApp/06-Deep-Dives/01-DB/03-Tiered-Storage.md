
> [!info] Not all data is equal
> Messages from 5 years ago are almost never read. Storing them in DynamoDB — fast, expensive, in-memory indexed — is wasteful. Tiered storage means keeping recent messages in fast storage and moving old messages to cheap cold storage automatically.

---

## The problem with storing everything in DynamoDB

DynamoDB charges for storage and for the data it keeps indexed and accessible at low latency. Storing 1 PB of messages in DynamoDB would cost a fortune — and most of that data would never be accessed.

```
Total data over 10 years  → 1 PB
Messages older than 1 year → accessed by maybe 1% of users, rarely
Messages older than 5 years → essentially never accessed
```

Paying DynamoDB prices for data that nobody reads is the wrong trade-off.

---

## The access pattern for old messages

Think about your own WhatsApp usage. When did you last scroll back to messages from 3 years ago? Almost never. The access pattern for chat history is heavily recency-biased:

```
Last 7 days     → accessed constantly (active conversations)
Last 30 days    → accessed occasionally (checking something recent)
Last 90 days    → accessed rarely (looking something up)
Older than 90 days → almost never
```

This is the classic 80/20 rule applied to time:

```
~90 days of messages = ~80% of all reads
~10 years of messages = ~100% of storage cost
```

---

## The math — hot vs cold split

```
Total data (10 years)         → 1 PB
Storage per day               → 250 GB/day

Hot data (last 90 days):
  250 GB/day × 90 days        → 22.5 TB in DynamoDB

Cold data (older than 90 days):
  1 PB - 22.5 TB              → ~977 TB in S3
```

22.5 TB in DynamoDB is manageable. 977 TB in S3 at a fraction of the cost.

```
DynamoDB storage cost  → ~$0.25/GB/month
S3 storage cost        → ~$0.023/GB/month  (10× cheaper)
S3 Glacier             → ~$0.004/GB/month  (60× cheaper than DynamoDB)

Saving on 977 TB:
  DynamoDB: 977,000 GB × $0.25 = $244,250/month
  S3:       977,000 GB × $0.023 = $22,471/month
  Savings:  ~$220,000/month
```

---

## How archival works

A background job runs daily, scanning for messages older than 90 days:

```
Step 1 — Scan DynamoDB for messages WHERE timestamp < (now - 90 days)
Step 2 — Write message content to S3:
          s3://whatsapp-archive/conv_abc123/msg_xyz789.json
Step 3 — Update DynamoDB row:
          SET content = null, s3_ref = "s3://whatsapp-archive/..."
Step 4 — (optionally) Delete original content column to reclaim DynamoDB space
```

The DynamoDB row stays — it's the index. Only the content moves to S3.

---

## How reads work for archived messages

When a client loads chat history and the app server encounters a row with `s3_ref` set:

```
Normal message (hot):
  App Server reads DynamoDB row → content is there → return immediately

Archived message (cold):
  App Server reads DynamoDB row → content is null, s3_ref is set
  App Server fetches from S3 → s3://whatsapp-archive/conv_abc123/msg_xyz789.json
  App Server returns content to client
```

The client sees no difference in the response format — just the message content. The only difference is latency: DynamoDB reads take ~1-5ms, S3 fetches take ~50-200ms. For messages from years ago, this is completely acceptable.

---

## The 90-day threshold — why not shorter?

90 days is a balance between storage cost and read latency. You could archive after 30 days and save more money, but you'd be pushing to S3 reads for messages that are still occasionally accessed (checking something from last month). 90 days covers the "I need to look up something from last quarter" use case while still moving the vast majority of data to cold storage.

In practice, this threshold should be configurable — a business decision based on cost vs user experience trade-off.

---

> [!tip] Interview framing
> "1 PB over 10 years is too much for DynamoDB. But access is heavily recency-biased — 90% of reads are on the last 90 days of messages. So I'd keep 90 days hot in DynamoDB (~22.5 TB) and archive everything older to S3. The DynamoDB row stays as an index pointer — content moves to S3. Cold reads take ~200ms instead of ~5ms, which is fine for messages from years ago. Cost saving is roughly 10× on the archived data."
