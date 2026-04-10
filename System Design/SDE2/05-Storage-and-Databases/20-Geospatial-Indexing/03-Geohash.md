# Geohash — Encoding 2D Location as a String

## The core idea

What if we divide the entire world into a grid, give each cell a name, and store that name as an indexed column? Nearby locations would share the same cell name — or at least a common prefix — and finding nearby drivers becomes a simple prefix query on a B+ Tree index.

That's exactly what Geohash does.

---

## How Geohash works — recursive splitting

Start with a box representing the entire Earth. Split it in half vertically. Left half = "a", right half = "b":

```
+---------+---------+
|         |         |
|   "a"   |   "b"   |
|         |         |
+---------+---------+
```

Mumbai is on the right side → **"b"**

Split "b" in half horizontally. Top = "ba", bottom = "bb":

```
+---------+---------+
|         |  "ba"   |
|         +---------+
|         |  "bb"   |
+---------+---------+
```

Mumbai is in the top half → **"ba"**

Split "ba" in half vertically again:

```
         +----+----+
         |"baa"|"bab"|
         +----+----+
```

Mumbai is on the right → **"bab"**

Keep splitting. Every split makes the cell smaller and more precise. After 10-12 splits, a cell covers roughly a city block. Mumbai ends up with a code like `"bab123"` — a short string that encodes its precise location on Earth.

---

## Why prefix matching works

Two drivers both in Mumbai will both start with `"bab..."`. A driver in Delhi will start with something completely different — `"cde..."`. A driver in New York will start with `"xyz..."`.

The longer the shared prefix, the closer the locations:

```
"bab"     → somewhere in Mumbai region  (large area)
"bab1"    → narrower area within Mumbai
"bab12"   → neighbourhood level
"bab123"  → city block level
```

So instead of computing distance against all 1 million drivers, you:

1. Compute the user's Geohash → `"bab12"`
2. Run a prefix query:

```sql
SELECT * FROM drivers WHERE geohash LIKE 'bab12%';
```

This hits a normal **B+ Tree index** on the geohash column. O(log n). Only drivers in the same cell are returned — maybe 50-100 instead of 1 million.

---

## The boundary edge case

There's one problem. Two drivers can be physically 10 metres apart but sit on opposite sides of a cell boundary — giving them completely different Geohash prefixes:

```
+----------+----------+
|          |    d2    |
|   "ba"   |   "bb"  |
|    d1    |          |
+----------+----------+
```

d1 and d2 are right next to each other. But a prefix query on `"ba"` misses d2 entirely.

---

## The fix — always query 8 neighbouring cells

You don't just query your own cell. You query **your cell + all 8 surrounding cells**:

```
+-----+-----+-----+
| ba1 | ba2 | bb1 |
+-----+-----+-----+
| ba3 | YOU | bb2 |
+-----+-----+-----+
| ba4 | ba5 | bb3 |
+-----+-----+-----+
```

Geohash libraries expose a `neighbors()` function that returns the 8 surrounding cell codes in O(1):

```python
import geohash

center = geohash.encode(19.08, 72.86, precision=5)
# → "bab12"

neighbours = geohash.neighbors("bab12")
# → ["bab13", "bab11", "bab09", "bab15", "bab0f", "bab0g", "bab18", "bab19"]
```

You don't need to know how the math works — the library handles it. You just query all 9 cells:

```sql
SELECT * FROM drivers 
WHERE geohash IN ('bab12', 'bab13', 'bab11', 'bab09', 'bab15', 'bab0f', 'bab0g', 'bab18', 'bab19');
```

9 index lookups on the B+ Tree. Fast.

---

## The full Uber query flow

```
User opens app at (19.08, 72.86)
    ↓
Compute user's Geohash → "bab12"
    ↓
Get 8 neighbouring cell codes via geohash.neighbors()
    ↓
Query: WHERE geohash IN (9 cells) → hits B+ Tree index → returns ~50-100 drivers
    ↓
For those 50-100 drivers, compute exact distance
    ↓
Filter to drivers within 2km
    ↓
Return results to user
```

The expensive distance calculation only runs on ~50-100 candidates, not 1 million. That's the win.

> [!important] Store both raw lat/lng and Geohash
> Store raw `lat` and `lng` for display and exact distance calculation. Store the Geohash for proximity indexing. Both are needed.

```
driver_id | lat   | lng   | geohash
----------|-------|-------|--------
d1        | 19.07 | 72.87 | bab123
d2        | 19.09 | 72.85 | bab124
d3        | 40.71 | -74.00| xyz987
```
