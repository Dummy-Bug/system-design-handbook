> [!question] Before sharding, JOINs were free — all your tables were on one server. After sharding, related data might be on different servers. The database can't JOIN across servers. Now what?


## Why JOINs break across shards

Before sharding — users and tweets on the same server, JOIN is straightforward:

```
Single Server:
┌─────────────────────────────────┐
│  Users table                    │
│  user_id │ username             │
│  1       │ alice                │
│  2       │ bob                  │
│                                 │
│  Tweets table                   │
│  tweet_id │ user_id │ text      │
│  101      │ 1       │ "hello"   │
│  102      │ 2       │ "world"   │
└─────────────────────────────────┘

SELECT users.username, tweets.text
FROM tweets JOIN users ON tweets.user_id = users.user_id
→ both tables on same server → easy ✓
```

After sharding by user_id:

```
Shard 1 (user_id 1-500M):          Shard 2 (user_id 500M-1B):
┌──────────────────────┐           ┌──────────────────────┐
│  alice (user_id 1)   │           │  charlie (600M)       │
│  her tweets          │           │  his tweets           │
└──────────────────────┘           └──────────────────────┘
```

Alice retweets charlie. Alice is on Shard 1, charlie is on Shard 2:

```
Tweet on Shard 1:
  tweet_id │ user_id │ retweet_of_user_id
  103      │ 1       │ 600M   ← charlie is on Shard 2!

SELECT users.username, tweets.text
FROM tweets JOIN users ON tweets.user_id = users.user_id
→ alice's tweets on Shard 1, charlie's user data on Shard 2
→ database engine cannot JOIN across two different servers ✗
```

**The database engine can only JOIN tables on the same server**. It has no concept of reaching out to another server mid-query.

---

## Fix 1 — Application-level JOIN

Your app server queries each shard separately and joins the results in memory:

```
App server:
  Step 1 → query Shard 1 → fetch alice's tweets (including retweet_of_user_id 600M)
  Step 2 → query Shard 2 → fetch charlie's username and profile
  Step 3 → join results in memory on app server

Database JOIN    → optimised, uses indexes, runs inside one server — fast
Application JOIN → two network round trips + join in application memory → more latency ✗
```

Works but is slower and more complex. The app must now understand shard topology, which bleeds infrastructure concerns into your business logic.

---

## Fix 2 — Co-location (better)

Design your shard key and data model so related data always lands on the same shard. You eliminate the cross-shard join at the design stage rather than patching it at query time.

For Twitter, shard by `user_id` and store the user's profile, tweets, and follows all on the same shard:

```
Shard 1:
  alice → her profile
        → all her tweets
        → all her follows/followers

Shard 2:
  charlie → his profile
           → all his tweets
           → all his follows/followers
```

Alice's feed query only needs her own data — it stays on Shard 1 entirely. Cross-shard only happens when viewing charlie's profile from alice's session — handled in the app layer for that specific case.

```
Co-location rule:
  Store data that is queried together → on the same shard
  The primary entity (user) and all its owned entities (tweets, follows)
  → same shard key → same shard
```

> [!important] Co-location is a design decision, not an afterthought
> You make this choice when you design the data model, before you write any queries. Sharding an existing relational schema that wasn't designed for co-location is painful — cross-shard joins will be everywhere and fixing them requires restructuring the schema.

---

## The general rule

```
Avoid cross-shard joins by:
  1. Co-locating related data under the same shard key (preferred)
  2. Denormalising — store a copy of the data you'd JOIN on the same shard
  3. Application-level join for unavoidable cases (two network hops, more latency)
```

Denormalisation in this context means intentionally duplicating data to avoid the join:

```
Instead of:
  tweets table: tweet_id | user_id | text
  → JOIN users table to get username

Denormalise:
  tweets table: tweet_id | user_id | username | text
  → username stored directly on the tweet row
  → no JOIN needed, username always available on the same shard
  → downside: if username changes, must update all tweet rows
```
