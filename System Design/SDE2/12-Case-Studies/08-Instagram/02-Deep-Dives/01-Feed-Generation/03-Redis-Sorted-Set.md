# Instagram Feed Generation — Redis Sorted Sets and Feed Pagination

Fan-out on write pre-builds each user's feed as a list of posts sorted by time. Now think about what serving that feed actually requires.

A user opens Instagram and sees 10 posts. They scroll down — they need the next 10. Then the next 10 after that. The feed is paginated, it's ordered by recency, and new posts are constantly arriving at the top while the user is scrolling.

A plain list stored in a key-value cache gets you the first page easily. But the moment the user scrolls, you need to fetch a specific slice of the list — posts 11 to 20, then 21 to 30. With a plain list, you'd have to pull the entire feed into application memory and slice it yourself. That's wasteful — a user with 500 posts in their feed shouldn't require a full 500-entry fetch just to show them items 200 to 210.

What you actually need is a data structure that lets you jump directly to any position in a sorted list without scanning everything before it. Redis sorted sets do exactly this.

---

## How sorted sets work

A Redis sorted set stores elements in order by a numeric **score**. Every element has a score attached, and Redis keeps the set sorted by that score automatically. You can fetch elements by position (rank) or by score range — both in O(log N) time, without scanning the whole set.

For an Instagram feed, the mapping is natural:

```
Element  →  post metadata (post_id, author, caption, media_url, ...)
Score    →  timestamp of the post
```

The sorted set for a user's feed looks like this:

```
feed:user_456
  score: 1714200900  →  { post_id: 9, author: "alice", ... }
  score: 1714197300  →  { post_id: 7, author: "bob", ... }
  score: 1714193700  →  { post_id: 5, author: "alice", ... }
  score: 1714190100  →  { post_id: 3, author: "carol", ... }
  ...
```

Highest timestamp at the top, oldest at the bottom.

---

## Pagination — offset vs cursor

There are two ways to page through this sorted set.

**Offset pagination** fetches by rank — position in the list:

```
Page 1  →  ZRANGE feed:user_456 0 9 REV      (positions 0 to 9, newest first)
Page 2  →  ZRANGE feed:user_456 10 19 REV    (positions 10 to 19)
Page 3  →  ZRANGE feed:user_456 20 29 REV    (positions 20 to 29)
```

Simple — just multiply the page number by the page size to get the offset. The problem is what happens while the user is scrolling. New posts arrive and get pushed into the sorted set at the top. Every existing post shifts down by one position. The post that was at rank 10 is now at rank 11. When the user requests page 2 starting at position 10, they get a post they already saw on page 1 — a duplicate.

**Cursor pagination** fixes this by anchoring to a timestamp instead of a position:

```
Page 1  →  ZRANGEBYSCORE feed:user_456 +inf -inf LIMIT 0 10 REV
           (10 newest posts)

Page 2  →  ZRANGEBYSCORE feed:user_456 (last_seen_timestamp -inf LIMIT 0 10 REV
           (10 posts older than the last one seen — ( means exclusive)
```

New posts arriving at the top don't affect this query at all. The cursor is anchored to a timestamp, so the scroll position is stable regardless of what's being added above. No duplicates, no skipped posts.

The only addition to the API contract is that the client sends back the timestamp of the last post it received. That's a small price for a scroll experience that doesn't break.

---

> [!tip] Interview framing
> When asked about feed pagination, the failure mode is what makes the answer strong — not just naming cursor-based pagination. Offset pagination breaks because new posts shift positions while the user scrolls, causing duplicates. Cursor pagination fixes it by anchoring to a timestamp. Show the examiner you understand why one breaks before presenting the fix.
