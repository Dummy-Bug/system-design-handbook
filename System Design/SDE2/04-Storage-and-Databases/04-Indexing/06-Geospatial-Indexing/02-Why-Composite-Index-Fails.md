# Why a Composite Index on (lat, lng) Doesn't Work

## The instinct

The first instinct is: "put an index on `lat` and `lng` — that should let us filter by both."

A single index on `lat` helps a little. A composite index on `(lat, lng)` feels like it should solve it. But neither actually works at scale. Here's why.

---

## Single index on lat

An index on `lat` sorts all drivers by latitude:

```
...
19.05 → driver d9
19.06 → driver d4
19.07 → driver d1
19.08 → driver d6   ← user is here
19.09 → driver d2
19.10 → driver d7
19.11 → driver d3
...
40.71 → driver d4   ← New York
```

2km in latitude terms is roughly 0.02 degrees. So you filter:

```sql
WHERE lat BETWEEN 19.06 AND 19.10
```

This hits the index efficiently. But look at what that latitude band actually covers — it's a **horizontal strip wrapping the entire Earth** at that latitude. From Mumbai, across the Arabian Sea, across Africa, across the Atlantic, across South America, across the Pacific.

Out of 1 million drivers, hundreds of thousands could fall in this band. Now you have to check `lng` for all of them — one by one. You reduced the scan but it's still massive.

---

## Composite index on (lat, lng)

A composite index on `(lat, lng)` stores data sorted like this:

```
(19.05, 72.80)
(19.05, 72.90)
(19.06, 72.70)
(19.07, 72.85)
(19.08, 72.86)  ← our user
(19.08, 150.00) ← Pacific Ocean driver, same lat band
(19.09, 72.83)
```

Remember the **leftmost prefix rule** — a composite index sorts by the first column first, then the second column within that. So you can efficiently range-scan on `lat`. But once you fix the lat range, the `lng` values within that range are scattered everywhere — `72.70`, `72.85`, `150.00` all mixed together.

The index narrows by `lat` efficiently. But within that lat band, it has to scan all the rows and check `lng` one by one. You're back to a partial scan — better than a full table scan, but still unacceptably slow at scale.

> [!important] The fundamental limitation
> A B+ Tree sorts data in one dimension. A composite index on (lat, lng) sorts by lat first — it can't filter both dimensions simultaneously. Within any lat range, lng values are unsorted and must be scanned linearly.

---

## Why this is a fundamental problem, not a query optimization

This isn't a matter of writing a better query or adding more indexes. The B+ Tree data structure simply cannot understand 2D space. It's built for 1D sorted data.

To solve this, you need to **encode the 2D location (lat, lng) into a single 1D value** that captures spatial proximity — so that nearby locations produce similar values, and a normal B+ Tree index can find them with a range query.
