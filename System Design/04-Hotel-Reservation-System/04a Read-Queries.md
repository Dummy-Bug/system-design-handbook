# Read Queries

These are the read-only queries — no data is changed. They can be served from a **read replica** or **cache** since slightly stale results are acceptable.

---

## Tables Involved

### `hotels`

| hotel_id | name | city | rating | is_featured | thumbnail_url | check_in_time | check_out_time |
|---|---|---|---|---|---|---|---|
| H1001 | Marriott Times Square | New York | 4.5 | true | https://... | 15:00 | 11:00 |
| H1002 | Hilton Midtown | New York | 4.2 | false | https://... | 14:00 | 12:00 |
| H1003 | Park Hyatt | New York | 4.8 | true | https://... | 15:00 | 11:00 |

### `room_types`

| room_type_id | hotel_id | name | price_per_night | capacity | total_rooms |
|---|---|---|---|---|---|
| RT007 | H1001 | Deluxe King | 180 | 2 | 50 |
| RT008 | H1001 | Suite | 350 | 4 | 10 |
| RT009 | H1002 | Standard Double | 150 | 2 | 80 |

### `room_inventory` — one row per room type per date

| room_type_id | date | available_count |
|---|---|---|
| RT007 | 2026-02-10 | 8 |
| RT007 | 2026-02-11 | 8 |
| RT007 | 2026-02-12 | 2 |
| RT008 | 2026-02-10 | 5 |
| RT008 | 2026-02-11 | 5 |
| RT008 | 2026-02-12 | 5 |
| RT009 | 2026-02-10 | 12 |
| RT009 | 2026-02-11 | 0 |
| RT009 | 2026-02-12 | 10 |

> [!note] RT009 on Feb 11 has 0 rooms
> This will become important in the Search query — H1002 should be excluded from results for a Feb 10–13 stay even though it has rooms on Feb 10 and 12.

---

## Query 1 — Homepage (Featured Hotels)

User lands on Booking.com. Show a curated list of featured hotels.

```sql
SELECT hotel_id, name, city, rating, thumbnail_url
FROM hotels
WHERE is_featured = true
LIMIT 8;
```

**Result from the sample data above:**

| hotel_id | name | city | rating | thumbnail_url |
|---|---|---|---|---|
| H1001 | Marriott Times Square | New York | 4.5 | https://... |
| H1003 | Park Hyatt | New York | 4.8 | https://... |

> H1002 is excluded because `is_featured = false`.
> Simple read — no joins, no date filters. Can be fully cached.

---

## Query 2 — Search Results

User enters city, dates (Feb 10–13 = 3 nights), and 2 guests.

```sql
SELECT
    h.hotel_id,
    h.name,
    h.city,
    h.rating,
    h.thumbnail_url,
    MIN(rt.price_per_night) AS starting_from_price
FROM hotels h
JOIN room_types rt     ON h.hotel_id      = rt.hotel_id
JOIN room_inventory ri ON rt.room_type_id = ri.room_type_id
WHERE h.city           = 'New York'
  AND ri.date          BETWEEN '2026-02-10' AND '2026-02-12'
  AND rt.capacity      >= 2
  AND ri.available_count > 0
GROUP BY h.hotel_id
HAVING COUNT(DISTINCT ri.date) = 3
LIMIT 20 OFFSET 0;
```

**Tracing through the sample data:**

After the JOINs and WHERE filters, only rows with `available_count > 0` survive:

| hotel_id | room_type_id | date | available_count |
|---|---|---|---|
| H1001 | RT007 | 2026-02-10 | 8 |
| H1001 | RT007 | 2026-02-11 | 8 |
| H1001 | RT007 | 2026-02-12 | 2 |
| H1001 | RT008 | 2026-02-10 | 5 |
| H1001 | RT008 | 2026-02-11 | 5 |
| H1001 | RT008 | 2026-02-12 | 5 |
| H1002 | RT009 | 2026-02-10 | 12 |
| ~~H1002~~ | ~~RT009~~ | ~~2026-02-11~~ | ~~0~~ | ← filtered out (available_count = 0)
| H1002 | RT009 | 2026-02-12 | 10 |

After `GROUP BY h.hotel_id` and `HAVING COUNT(DISTINCT ri.date) = 3`:

- **H1001** → has rows for all 3 dates → ✅ included, `starting_from_price = 180`
- **H1002** → only has rows for 2 dates (Feb 11 was filtered out) → ❌ excluded

**Final result:**

| hotel_id | name | city | rating | starting_from_price |
|---|---|---|---|---|
| H1001 | Marriott Times Square | New York | 4.5 | 180 |

> [!note] Why `HAVING COUNT(DISTINCT ri.date) = 3`?
> H1002 has rooms on Feb 10 and 12 but is **sold out on Feb 11**.
> A guest staying 3 nights needs availability on all 3 nights — not just some.
> The `HAVING` clause catches this and correctly excludes H1002 from results.

---

## Query 3 — Hotel Detail Page

User clicks on H1001. Two queries fire on the same page load.

### Query 3a — Hotel Info

```sql
SELECT hotel_id, name, city, address, rating, amenities, check_in_time, check_out_time, cancellation_policy
FROM hotels
WHERE hotel_id = 'H1001';
```

**Result:**

| hotel_id | name | city | rating | check_in_time | check_out_time |
|---|---|---|---|---|---|
| H1001 | Marriott Times Square | New York | 4.5 | 15:00 | 11:00 |

---

### Query 3b — Available Room Types for the Selected Dates

```sql
SELECT
    rt.room_type_id,
    rt.name,
    rt.price_per_night,
    rt.price_per_night * 3  AS total_price,
    rt.capacity,
    rt.amenities,
    MIN(ri.available_count) AS rooms_left
FROM room_types rt
JOIN room_inventory ri ON rt.room_type_id = ri.room_type_id
WHERE rt.hotel_id  = 'H1001'
  AND ri.date      BETWEEN '2026-02-10' AND '2026-02-12'
  AND rt.capacity  >= 2
GROUP BY rt.room_type_id
HAVING MIN(ri.available_count) > 0;
```

**Tracing through the sample data:**

For RT007 (Deluxe King), `MIN(available_count)` across Feb 10, 11, 12 = `MIN(8, 8, 2)` = **2**
For RT008 (Suite), `MIN(available_count)` across Feb 10, 11, 12 = `MIN(5, 5, 5)` = **5**

**Final result:**

| room_type_id | name | price_per_night | total_price | capacity | rooms_left |
|---|---|---|---|---|---|
| RT007 | Deluxe King | 180 | 540 | 2 | 2 |
| RT008 | Suite | 350 | 1050 | 4 | 5 |

> [!note] Why `MIN(available_count)`?
> RT007 has 8 rooms free on Feb 10 and 11, but only 2 on Feb 12.
> The guest is staying all 3 nights — so the true available count is the **tightest night**: 2.
> `MIN()` finds that bottleneck automatically.
> If any night had 0, this room type would be excluded entirely by the `HAVING` clause.
