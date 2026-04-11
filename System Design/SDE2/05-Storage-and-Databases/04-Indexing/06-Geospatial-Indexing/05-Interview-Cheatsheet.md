
> [!question] How would you find all drivers within 2km of a user?
>> [!success]-
>> The naive approach — computing distance against every driver in the database — is a full table scan (O(n)). At 1 million drivers, this is too slow.
>>
>> A composite index on (lat, lng) doesn't help — the leftmost prefix rule means you can filter by lat efficiently, but within any lat band, lng values are unsorted and must be scanned linearly. The lat band at any given latitude wraps the entire Earth — hundreds of thousands of drivers.
>>
>> The solution is **Geohash** — encode (lat, lng) into a single indexed string. Divide the world into a recursive grid, assign each cell a string code. Nearby locations share a common prefix. Store the Geohash as an indexed column and query with prefix matching.
>>
>> > [!tip] Interview framing
>> > "I'd use Geohash to encode each driver's location as a string. The world is recursively divided into a grid — nearby locations share a prefix. I'd store the Geohash as an indexed column and query the user's cell plus 8 neighbouring cells to handle boundary cases. That reduces the candidate set from 1M drivers to ~50-100, then I compute exact distance on those."

---

> [!question] Why does a composite index on (lat, lng) fail for proximity queries?
>> [!success]-
>> A composite index sorts by lat first, then lng within that. You can range-scan on lat efficiently — but within any lat range, lng values are scattered. The lat band wraps the entire Earth horizontally, potentially returning hundreds of thousands of rows that all need their lng checked one by one. The B+ Tree is 1D — it cannot filter two dimensions simultaneously.

---

> [!question] What is Geohash and how does it work?
>> [!success]-
>> Geohash recursively divides the world into a grid. Start with the whole Earth as a box, split it in half, assign each half a letter. Keep splitting — each split adds a character to the code. After enough splits, each cell covers a city block. A location encodes to a short string like "bab123". Nearby locations share a common prefix. Store this string as an indexed column — proximity becomes a prefix query on a B+ Tree, which is O(log n).

---

> [!question] What is the boundary edge case in Geohash and how do you fix it?
>> [!success]-
>> Two locations physically 10 metres apart can sit on opposite sides of a cell boundary — giving them completely different Geohash prefixes. A prefix query on your cell would miss the neighbour entirely.
>>
>> Fix: always query your cell plus all 8 surrounding cells. Geohash libraries expose a `neighbors()` function that returns the 8 surrounding cell codes in O(1). Query all 9 cells, get ~50-100 candidates, then compute exact distance to filter to the true 2km radius.

---

> [!question] What is S2 and when do you mention it?
>> [!success]-
>> S2 is Google's geospatial library. Same concept as Geohash — divide the Earth into cells, encode each cell as a single indexed value. The difference: S2 uses a 64-bit integer instead of a string (integer range query instead of prefix match), and projects the sphere onto a cube for uniform cell sizes globally — Geohash cells distort near the poles.
>>
>> Mention S2 in Google interviews. For all other interviews, Geohash is sufficient.
>>
>> > [!tip] Interview framing
>> > "Google uses S2 cells internally — same concept as Geohash but encodes location as a 64-bit integer with better uniformity near the poles. This is what Google Maps and Uber use."

---

## The full flow

```
User at (19.08, 72.86)
    ↓
Compute Geohash → "bab12"
    ↓
Get 8 neighbours via geohash.neighbors()
    ↓
SELECT * FROM drivers WHERE geohash IN (9 cells)  ← hits B+ Tree index
    ↓
~50-100 candidates returned
    ↓
Compute exact distance for each candidate
    ↓
Return drivers within 2km
```

## Schema

```
driver_id | lat   | lng   | geohash
----------|-------|-------|--------
d1        | 19.07 | 72.87 | bab123    ← store both raw coords + geohash
d2        | 19.09 | 72.85 | bab124
d3        | 40.71 | -74.00| xyz987
```

> [!important] Always store raw lat/lng alongside Geohash
> Raw coords for display and exact distance calculation. Geohash for proximity indexing. Both are needed.
