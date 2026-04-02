# Initiate Reservation — Click Reserve

This is triggered when the user clicks **Reserve** on a room type. It is the most critical write operation in the system.

---

## What Happens at This Step

The system must do three things **atomically** (all or nothing):

1. **Check and deduct** inventory for every night of the stay — using optimistic locking
2. **Create** a `PENDING` reservation with a 15-minute expiry timer

This is a **transaction** — if any step fails, all steps are rolled back.

---

## Tables Involved

### `room_inventory` — before the transaction

| room_type_id | date | available_count |
|---|---|---|
| RT007 | 2026-02-10 | 8 |
| RT007 | 2026-02-11 | 8 |
| RT007 | 2026-02-12 | 2 |

### `reservations` — before the transaction

| reservation_id | reservation_token | user_id | room_type_id | check_in | check_out | status | expires_at |
|---|---|---|---|---|---|---|---|
| *(empty)* | | | | | | | |

---

## The Transaction

```sql
BEGIN;

  -- Step 1: Deduct inventory — but ONLY for nights that still have availability
  -- No lock held upfront — this is optimistic locking
  UPDATE room_inventory
  SET available_count = available_count - 1
  WHERE room_type_id    = 'RT007'
    AND date            BETWEEN '2026-02-10' AND '2026-02-12'
    AND available_count > 0;    -- ← optimistic check: only deduct if still available

  -- Application checks: rows_affected must equal 3 (one per night of the stay)
  -- If any night had available_count = 0, that row was skipped → rows_affected < 3 → ROLLBACK

  -- Step 2: Create the PENDING reservation with a 15-minute expiry
  INSERT INTO reservations
    (reservation_id, reservation_token, user_id, hotel_id, room_type_id, check_in, check_out, status, expires_at)
  VALUES
    ('RES900456', 'tok_9g4m03ne', 'U5002', 'H1001', 'RT007', '2026-02-10', '2026-02-13', 'PENDING', NOW() + INTERVAL '15 minutes');

COMMIT;
```

---

## Tables After the Transaction

### `room_inventory` — after

| room_type_id | date | available_count |
|---|---|---|
| RT007 | 2026-02-10 | **7** |
| RT007 | 2026-02-11 | **7** |
| RT007 | 2026-02-12 | **1** |

> Each night dropped by 1. The room is now held.

### `reservations` — after

| reservation_id | reservation_token | user_id | room_type_id | status | expires_at |
|---|---|---|---|---|---|
| RES900456 | tok_9g4m03ne | U5002 | RT007 | **PENDING** | 2026-02-01 15:30:00 |

---

> [!important] How optimistic locking prevents double booking here
> Alice and Bob both click Reserve on the last Deluxe King room at the same moment.
> Neither holds a lock — both transactions proceed simultaneously.
>
> Alice's UPDATE runs first:
> - `available_count = 2`, condition `> 0` passes → deducts → `available_count = 1`
>
> Bob's UPDATE runs a moment later:
> - `available_count = 1`, condition `> 0` still passes → deducts → `available_count = 0`
>
> Both succeed in this case — because there were 2 rooms left.
>
> If only 1 room was left:
> - Alice deducts → `available_count = 0`
> - Bob's UPDATE: `available_count = 0`, condition `> 0` **fails** → 0 rows affected → ROLLBACK
> - Bob gets "Room unavailable"
>
> The `CHECK (available_count >= 0)` constraint in the schema is the final safety net — it prevents the count ever going negative even if two transactions somehow slip through simultaneously.

> [!tip] Status is `PENDING`, not `CONFIRMED`
> The room is held but the user hasn't paid yet.
> If they close the browser or payment fails, the hold must be released — see [[04d Background-Jobs]].
> The reservation only becomes `CONFIRMED` after payment — see [[04c Confirm-Reservation]].
