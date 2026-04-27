# Instagram Feed Generation — The Core Problem

The Instagram home feed looks simple from the outside. You open the app and see photos and videos from the people you follow, newest first. But at 500M daily active users, generating that feed is one of the hardest read problems in social media engineering.

To understand why, start with what the feed actually is.

---

## What is the feed, really?

Think about it for a second. What data structure is the Instagram feed?

It's a mapping:

```
user_id → [list of posts to show them]
```

That list is personalised — it contains posts from the specific set of accounts this user follows, sorted by recency. For every one of Instagram's 500M daily users, that list is different.

So the question becomes: **how and when do you build that list?**

---

## The first instinct — build it when they ask

The obvious answer is: when a user opens the feed, go figure it out on the spot. The steps would be:

```
1. Query the follow table  → find all accounts this user follows
2. Query the posts table   → get recent posts from each of those accounts
3. Merge and sort by time  → return the result
```

This works fine for one user. But what's the problem with step 2?

If the user follows 500 people, that's 500 separate DB queries just to load one feed. This is the classic **N+1 problem** — one query to find N followees, then N more queries to fetch their posts.

This approach is called **fan-out on read** — you fan out across all your followees at the moment the feed is requested.

---

## Does it hold at scale?

From the estimation, Instagram has **1M feed loads per second**. The average user follows around 500 accounts. So:

```
1M reads/sec × 500 followees = 500M DB queries/sec
```

A single database instance handles around 50K read queries per second. That means:

```
500M ÷ 50K = 10,000 DB instances
```

Ten thousand database instances — just to serve the feed. That's clearly not acceptable.

At this point, caching feels like the natural fix. But think about it more carefully: before you can cache a user's feed, you have to assemble it first. And assembling it still requires those 500 queries. Caching doesn't eliminate the work — it just means you do it once and store the result.

Which is actually the right idea. But it points you toward a completely different design.

---

## The key insight — look at write QPS

Step back and look at the numbers from the other direction.

Instagram's **write QPS is only ~1,000 posts per second**. Read QPS is 1M/sec. That's a 1,000x gap.

Writes are rare. Reads are constant.

If reads are the expensive path, can we shift the work to writes instead? Writes happen 1,000x less often — they're a far cheaper place to do heavy computation.

This is the idea behind **fan-out on write**: instead of assembling a user's feed when they ask for it, build it in advance. The moment someone posts a photo, immediately push that post into every follower's pre-built feed list. By the time a follower opens the app, their feed is already sitting there, ready to serve.

---

> [!info] Where this is going
> Fan-out on write sounds like the clear winner — and for most users it is. But it introduces a new problem: what happens when a celebrity with 50 million followers posts a photo? That single write fans out into 50 million feed updates. The next section covers how Instagram handles this, and why the real answer ends up being a hybrid of both approaches.
