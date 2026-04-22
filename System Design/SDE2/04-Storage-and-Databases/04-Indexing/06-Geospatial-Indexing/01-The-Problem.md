> [!info] Find all drivers within 2km of this user.
>  A standard B+ Tree index cannot answer this without a full table scan — because location is 2D (lat/lng) and a B+ Tree is 1D. Geospatial indexing solves this by encoding 2D location into a single value that a normal index can handle.

## The scenario

You're building Uber. A user opens the app and the system needs to answer one question instantly:

**"Show me all drivers within 2km of this user."**

Every driver has a latitude and longitude stored in the database. You have 1 million active drivers worldwide right now.

---

## What is latitude and longitude?

The Earth is a sphere. To pinpoint any location on it, we use two numbers:

- **Latitude** — how far north or south you are. The equator is 0°, North Pole is 90°, South Pole is -90°.
- **Longitude** — how far east or west you are. 0° runs through London, goes to 180° east or west.

Every point on Earth has a unique (latitude, longitude) pair:

```
Mumbai   → (19.07,  72.87)
New York → (40.71, -74.00)
London   → (51.50,  -0.12)
```

In your Uber database, every driver has a row like:

```
driver_id | lat   | lng
----------|-------|-------
d1        | 19.07 | 72.87
d2        | 19.09 | 72.85
d3        | 19.11 | 72.90
d4        | 40.71 | -74.00   ← New York, nowhere near Mumbai
```

---

## The naive approach — full table scan

The obvious query:

```sql
SELECT * FROM drivers
WHERE distance(user_lat, user_lng, driver_lat, driver_lng) < 2km;
```

To answer this, the database computes the distance formula for **every single driver** — all 1 million of them — one by one. There is no shortcut. This is a full table scan — O(n).

At 1 million drivers, this is slow. At 10 million drivers, it's unacceptable. A user opening Uber cannot wait seconds for nearby drivers to load.

> [!danger] Full table scan at scale
> Computing distance against every row in the table is O(n). At millions of rows, this query takes seconds — completely unacceptable for a real-time "find nearby drivers" feature.

---

## Why you need a smarter approach

The fundamental issue: **location is 2D**. You need to filter on both latitude and longitude simultaneously to determine proximity. Standard database indexes are built for 1D data — they sort values in a line and do range scans. They have no native understanding of 2D space.

This is not a query optimization problem — it's a data modeling problem. You need to encode 2D location into a form that a 1D index can handle efficiently.
