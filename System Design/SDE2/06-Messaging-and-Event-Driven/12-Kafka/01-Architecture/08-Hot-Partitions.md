
> [!info] A hot partition happens when your partition key distributes data unevenly — one partition receives a disproportionate share of traffic because the underlying data is naturally skewed. Consistent hashing doesn't help when the data itself is uneven.

---

## The problem

You partition the `ad_clicks` topic by `advertiser_id`. The logic is sound — all clicks for the same advertiser land in the same partition, guaranteeing order per advertiser. But the data doesn't cooperate:

```
Partition 0 (Nike):   80,000 clicks/sec  ← one broker melting
Partition 1 (Adidas):  8,000 clicks/sec
Partition 2 (Puma):   12,000 clicks/sec
```

Nike is the biggest advertiser on the platform. 80% of all traffic hashes to Partition 0. One broker is doing almost all the work. Adding more partitions doesn't help — Nike's clicks still all hash to the same one.

This is the same hotspot problem you'd hit in any sharded system. The fix is always the same: increase the granularity of your key so traffic spreads more evenly.

---

## Option 1 — Compound key

Instead of just `advertiser_id`, add another dimension to the key — for example `advertiser_id + user_id`:

```
hash("nike_user_abc") % 3 = Partition 0
hash("nike_user_xyz") % 3 = Partition 1
hash("nike_user_def") % 3 = Partition 2
```

Nike's traffic now spreads across all three partitions because different users hash to different partitions. The hotspot is gone.

But ordering changes. With just `advertiser_id`, all Nike clicks arrived in one ordered stream. With `advertiser_id + user_id`, Nike's clicks are scattered across partitions — and ordering is only guaranteed within a partition, not across them:

```
Partition 0: nike_user_abc click 1 → nike_user_abc click 3
Partition 1: nike_user_xyz click 1 → nike_user_xyz click 2
Partition 2: nike_user_abc click 2 → nike_user_xyz click 3
```

nike_user_abc's clicks are split between Partition 0 and Partition 2. Globally, click 2 arrives after click 3.

Whether this matters depends entirely on what the consumer needs. Billing just needs a correct count — it doesn't care which click came first. For billing, the compound key is fine. If you needed strict global ordering per advertiser, it isn't.

---

## Adding more dimensions

If Nike is so large that even spreading by `user_id` isn't enough — say Nike runs a Super Bowl campaign and millions of users click simultaneously — you add another dimension:

```
advertiser_id + user_id + country_id

hash("nike_user_abc_US") % 3 = Partition 0
hash("nike_user_abc_UK") % 3 = Partition 1
hash("nike_user_xyz_IN") % 3 = Partition 2
```

Now Nike's traffic splits by user and by country. The granularity is fine enough that no single partition gets buried.

But every dimension you add narrows the ordering guarantee:

```
advertiser_id only                   → ordering per advertiser  |  worst spread
advertiser_id + user_id              → ordering per user        |  better spread
advertiser_id + user_id + country_id → ordering per user per country  |  best spread
```

At some point the key becomes so granular that ordering is essentially meaningless. At that point you might as well use no key at all and let the producer round-robin across partitions — maximum spread, zero ordering guarantee.

The compound key is a direct trade-off: **every dimension you add gives you better load distribution but coarser ordering guarantees.**

---

---

## Option 2 — Dedicated topic for hot advertisers

When you've exhausted the compound key options and one advertiser is still so large that it saturates a partition regardless of how you hash it, the last resort is giving that advertiser its own topic with more partitions:

```
topic: ad_clicks_nike    → 20 partitions  ← Nike gets its own lane
topic: ad_clicks_general → 3 partitions   ← everyone else
```

Nike now has 20 partitions absorbing its traffic. The general topic stays lean for smaller advertisers. This actually makes operational sense too — an advertiser spending hundreds of millions of dollars a year probably warrants dedicated infrastructure.

But the consumer side gets complicated. Before, the billing service subscribed to one topic and got everything. Now it has to know which advertisers have dedicated topics and which don't:

```
Before:
  billing service → subscribes to ad_clicks → done

After:
  billing service → is this advertiser in the hot list?
                 → yes: read from ad_clicks_nike
                 → no: read from ad_clicks_general
```

Every time you onboard a new massive advertiser you update that list. Every time one scales down you clean it up. That's operational complexity — a config to maintain, a deployment to do, consumers to update — that didn't exist before.

This is why dedicated topics are the last resort. You only reach for them when you've genuinely exhausted the key granularity options.

---

## The decision ladder

```
1. Simple key (advertiser_id)
   → still hot? → go to 2

2. Compound key (advertiser_id + user_id)
   → still hot? → go to 3

3. More dimensions (+ country_id, + timestamp_bucket)
   → still hot? → go to 4

4. Dedicated topic for that advertiser
   → accept the operational complexity — no other option left
```

In practice, most hotspot problems are solved at step 2 or 3. Dedicated topics appear at truly extreme scale — where one tenant generates orders of magnitude more traffic than anyone else and no amount of key spreading is enough.

---

> [!important] The right partition key is determined by what your consumer actually needs. Ask: does my consumer need strict ordering, or does it just need correct aggregation? Billing needs correct counts — compound key is fine. A stream processor that detects click sequences per user needs per-user ordering — simpler key required.

> [!tip] **Interview framing:** "Hot partitions happen when data is naturally skewed — one advertiser drives 80% of clicks. I'd first try a compound key: advertiser_id + user_id spreads Nike's traffic while keeping per-user ordering. If still hot, add country_id. Each dimension gives better spread but coarser ordering — the right choice depends on what the consumer needs. If key granularity is exhausted, the last resort is a dedicated topic for that advertiser with more partitions — but that adds operational complexity: consumers now need to know which topic to read from per advertiser."
