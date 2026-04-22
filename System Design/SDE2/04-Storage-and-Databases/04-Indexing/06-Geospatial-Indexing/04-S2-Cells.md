# S2 Cells — Google's Approach to Geospatial Indexing

## Same concept, different encoding

S2 is Google's geospatial indexing library. The core idea is identical to Geohash — divide the Earth into cells, encode each cell as a single value, index that value, use range queries to find nearby locations.

The difference is in how the encoding works.

---

## Geohash uses strings — S2 uses 64-bit integers

Geohash encodes a location as a string like `"bab123"`. Proximity becomes a string prefix query.

S2 encodes a location as a **64-bit integer**. Proximity becomes an **integer range query**:

```sql
-- Geohash approach
SELECT * FROM drivers WHERE geohash LIKE 'bab12%';

-- S2 approach
SELECT * FROM drivers WHERE s2_cell_id BETWEEN 123456789 AND 123567890;
```

**Integer range queries on a B+ Tree are fast** — integers compare in a single CPU instruction. This is slightly more efficient than string prefix matching at very large scale.

---

## Why a cube, not a rectangle

Geohash divides the Earth using a rectangular grid projected flat. Near the equator, cells are roughly square and equal in size. But near the poles, longitude lines compress together — the same rectangular grid produces tiny distorted slivers at high latitudes.

This means a Geohash cell at the equator and a Geohash cell near the poles at the same precision level cover **very different physical areas**. Your "2km radius" search becomes inconsistent depending on where on Earth the user is.

S2 solves this by projecting the sphere onto a **cube** first, then dividing each face of the cube into a grid. The cube projection distributes cells much more uniformly across the Earth's surface — consistent cell sizes everywhere, no distortion at the poles.

> [!tip] For interviews — one line is enough
> "Geohash uses a rectangular grid which distorts near the poles. S2 projects the sphere onto a cube first, giving uniform cell sizes everywhere on Earth."

You don't need to know the mathematics. Just know it exists and why it's better for global systems.

---

## Where S2 is used

- **Google Maps** — internally for all proximity queries
- **Google Earth** — cell-based spatial indexing
- **Uber** — switched from Geohash to S2 for more accurate global coverage

---

## When to mention S2 in an interview

> [!tip] Google interview signal
> Mentioning S2 in a Google interview is a strong positive signal. It shows you know what Google actually uses internally.

For any other company interview, Geohash is perfectly sufficient. Lead with Geohash, then mention S2 as "Google's more accurate approach used in Google Maps."

For a Google interview specifically:
- Lead with the problem (2D location, B+ Tree is 1D)
- Explain Geohash as the general approach
- Then say: "Google uses S2 cells internally — same concept but encodes location as a 64-bit integer instead of a string, with better uniformity near the poles due to cube projection. This is what Google Maps and Uber use."

---

## Summary — Geohash vs S2

| | Geohash | S2 |
|---|---|---|
| Encoding | String (`"bab123"`) | 64-bit integer |
| Query | Prefix match | Integer range |
| Grid | Rectangular (distorts at poles) | Cube-projected (uniform globally) |
| Library | `python-geohash`, built into PostGIS | Google's S2 library |
| Use | Most systems | Google Maps, Uber, Google interviews |
