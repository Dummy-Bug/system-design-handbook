when someone likes a tweet we can have an event
`{tweet_id,user_id,timestamp}` 

> client would be interacting with application server for creating a `Like` then that application server would be making an entry into the DB and then application server will send use the Like event `{tweet_id,user_id,timestamp}` to top k heavy system.

so we do not have to care about how the event is been creating , our agenda is when somebody gives us the event we process the event and create the top K heavy hitters.

Let's first solve for 1M tweets per day an under engineered solution.

> 1M or 10M tweets and and we are getting likes count on these and we have to find the top K trending tweets in a day.


![[Excalidraw/Drawing 2026-03-25 07.33.54.excalidraw]]
- Normal frequency map cum Heap problem solving top K.
```Java
// Step 1: Maintain frequency map
HashMap<tweet_id, like_count>

// Step 2: On every like event:
map.put(tweet_id, map.getOrDefault(tweet_id, 0) + 1)

// Step 3: To get Top K at any point:
MinHeap of size K
→ iterate map
→ maintain K largest like counts
→ O(N log K) time
```

This solution works because we have only 1M tweets and we can keep them in-memory as 1M means around 10^6 entries and HashMap can be declared of size 10^8 or 10^9.

LeetCode gives each solution *256MB* of memory and a *time limit of ~1-2 seconds.* So constraints like `N <= 10^5` are set to ensure your solution fits within those sandbox limits. It has nothing to do with real HashMap capabilities.

Real world HashMap limits are just RAM:

```
// How many entries can a HashMap hold?
Answer: as many as fit in available RAM

1M entries × 50 Bytes = 50MB   → fits easily ✅
10M entries × 50 Bytes = 500MB → still fine on most machines ✅
```

## Current setup failures

- We cannot answer topK trendings tweets for last 1 hour and if we keep a map of last one hour still we cannot asnwer trending tweets of last 5 minutes.
- If we create a frequency map for 5 minutes then what ? then it would work but still it cannot cater to sliding window properties . e.g let's say we create a frequency map for 5 to 5.5pm then after 5 minutes we destroy this map and create a new map from 5.5 to 5.10 but if we see clearly we missed the window of 5.1 to 5.6 , 5.2 to 5.7 and so on.. This is called a **Tumbling Window** — fixed, non-overlapping buckets. No bucket shares data with another.

```
Event at 5:04 → in bucket 1
Event at 5:06 → in bucket 2

Query at 5:07 "top K in last 5 mins" → 5:02 to 5:07
→ needs partial bucket 1 + partial bucket 2
→ tumbling window has NO way to answer this ❌
```

**The fix — Sliding Window with fine-grained buckets:**

Instead of 5 min buckets, use **very small buckets** (e.g. 10 seconds each):

```Java
// 5 min window = 30 buckets of 10 seconds each
[5:00-5:10][5:10-5:20][5:20-5:30]...[5:50-6:00]

// At any point, top K = merge last 30 buckets
// Every 10 seconds → drop oldest bucket, add new one
```

**The tradeoff:**

- **Larger buckets** → fewer buckets, less memory, but sliding window is less precise
- **Smaller buckets** → more buckets, more memory, but sliding window is more precise

This is how **Apache Flink, Kafka Streams, and Spark Streaming** all solve this problem under the hood.


