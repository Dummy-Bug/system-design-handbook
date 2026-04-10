# Geospatial Indexing — Overview

> [!info] The core problem
> "Find all drivers within 2km of this user." A standard B+ Tree index cannot answer this without a full table scan — because location is 2D (lat/lng) and a B+ Tree is 1D. Geospatial indexing solves this by encoding 2D location into a single value that a normal index can handle.

---

## The key insight

Every location on Earth is described by two numbers — latitude (north/south) and longitude (east/west). To find nearby locations, you need to filter on both simultaneously. A B+ Tree can only sort and range-scan one dimension efficiently.

The solution: **encode (lat, lng) into a single value** — either a string (Geohash) or an integer (S2) — index that value, and use prefix or range queries to find nearby locations.

---

## Two approaches

| | Geohash | S2 Cells |
|---|---|---|
| Encoding | String prefix | 64-bit integer |
| Query type | Prefix match (`LIKE 'bab12%'`) | Integer range (`BETWEEN x AND y`) |
| Grid shape | Rectangular | Cube-projected |
| Used by | Most systems | Google Maps, Uber |
| Interview use | General systems | Google interviews specifically |

---

## Files in this folder

| File | What it covers |
|---|---|
| `01-The-Problem.md` | Why naive full table scan fails, why lat/lng filtering is expensive |
| `02-Why-Composite-Index-Fails.md` | Why indexing lat and lng separately or together still doesn't work |
| `03-Geohash.md` | How Geohash works, prefix matching, boundary edge case, 8 neighbour fix |
| `04-S2-Cells.md` | Google's approach, integer IDs, when to mention in interviews |
| `05-Interview-Cheatsheet.md` | Quick reference for revision |
