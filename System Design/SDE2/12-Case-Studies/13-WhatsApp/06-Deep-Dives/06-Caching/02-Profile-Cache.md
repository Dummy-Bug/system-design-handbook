
> [!info] The better cache target — user profiles
> Profile data is read on every inbox load, every chat open, every group message render. It almost never changes. This is the ideal cache candidate.

---

## The problem

When Alice opens her inbox, she sees 20 conversations. Each row shows a name and an avatar. Those names and avatars come from the users table — one DB read per contact.

```
Alice opens inbox
→ fetch top 20 conversations from conversations table      (1 read)
→ fetch profile for Bob                                    (1 read)
→ fetch profile for Charlie                                (1 read)
→ fetch profile for Dave                                   (1 read)
→ ... × 20 contacts
= 21 DB reads for one inbox load
```

At 100M DAU, if even a fraction open the app at peak hour, this is tens of millions of profile reads per hour — all for data that barely changes.

Bob changes his WhatsApp display name maybe once a month. His avatar maybe once every few months. Yet every time anyone who knows Bob opens their inbox, the system fetches his profile from the database.

This is the textbook cache candidate: **high read frequency, near-zero write frequency.**

---

## What to cache

```
Cache:  user profiles
Key:    user:<user_id>
Value:  { name, avatar_s3_url, status }
TTL:    1 hour (with jitter — explained below)
```

Size check:

```
500M users × (name ~50B + avatar S3 URL ~100B + status ~100B)
= 500M × 250 bytes
= ~125GB
```

125GB is one medium Redis instance. In return, you eliminate K DB reads on every single inbox load across 500M users.

---

## How it works — cache-aside pattern

The app server is responsible for populating and reading the cache. The DB is always the source of truth.

```
Alice opens inbox — needs Bob's profile:
→ App server: GET user:bob from Redis
→ Hit: return cached profile, done
→ Miss: fetch from DynamoDB → store in Redis → return to Alice
```

The first request for Bob's profile always hits DynamoDB. Every subsequent request within the TTL window hits Redis.

---

## TTL and jitter

TTL of 1 hour means a profile stays cached for an hour after it's first loaded. After expiry, the next request re-fetches from DB and re-caches.

**The jitter problem:** if you set TTL = 3600 for everyone, all entries cached at the same moment expire at the same moment. On cold start, you fill the cache — then exactly 1 hour later, everything expires simultaneously, and you get a DB storm.

Fix: add random jitter to TTL.

```
TTL = 3600 + random(0, 600)   // between 1 hour and 1 hour 10 minutes
```

Now entries expire at different times, spreading the DB load evenly instead of spiking it.

> [!important] Jitter is not optional at scale
> Without TTL jitter, you trade a cold-start problem for a scheduled thundering herd problem. Every hour, your DB gets hammered. Add jitter — it costs nothing and prevents a real operational incident.
