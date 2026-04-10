# Background Jobs — Release Expired Holds

A background process runs every minute. Its job is to find `PENDING` reservations whose 15-minute window has passed, restore the inventory, and mark them as `EXPIRED`.

---

## Why This Job Exists

When a user clicks Reserve, we immediately deduct from inventory and create a `PENDING` reservation. The room is held for 15 minutes.

If the user:
- Closes the browser
- Lets the timer expire
- Has their payment declined and gives up

...the hold must be released. Without this job, those rooms would be **permanently lost from inventory** — nobody booked them, nobody paid, but they'd never show as available again.

---

## Tables Before the Job Runs

### `reservations`

| reservation_id | room_type_id | check_in | check_out | status | expires_at |
|---|---|---|---|---|---|
| RES900123 | RT007 | 2026-02-10 | 2026-02-13 | CONFIRMED | null |
| RES900456 | RT007 | 2026-02-10 | 2026-02-13 | **PENDING** | **2026-02-01 14:00:00** ← expired |
| RES900789 | RT008 | 2026-02-10 | 2026-02-13 | **PENDING** | **2026-02-01 13:45:00** ← expired |

### `room_inventory`

| room_type_id | date | available_count |
|---|---|---|
| RT007 | 2026-02-10 | 6 |
| RT007 | 2026-02-11 | 6 |
| RT007 | 2026-02-12 | 0 |
| RT008 | 2026-02-10 | 4 |
| RT008 | 2026-02-11 | 4 |
| RT008 | 2026-02-12 | 4 |

> RT007 on Feb 12 shows 0 — that deducted count belongs to RES900456 which was never paid for.
> The job will restore it.

---

## The Transaction

```sql
BEGIN;

  -- Step 1: Restore inventory for every expired PENDING reservation
  UPDATE room_inventory ri
  SET available_count = available_count + 1
  FROM reservations r
  WHERE r.status        = 'PENDING'
    AND r.expires_at    < NOW()
    AND ri.room_type_id = r.room_type_id
    AND ri.date         BETWEEN r.check_in AND r.check_out - INTERVAL '1 day';

  -- Step 2: Mark those reservations as EXPIRED
  UPDATE reservations
  SET status = 'EXPIRED'
  WHERE status     = 'PENDING'
    AND expires_at < NOW();

COMMIT;
```

---

## Tables After the Job Runs

### `reservations`

| reservation_id | room_type_id | status | expires_at |
|---|---|---|---|
| RES900123 | RT007 | CONFIRMED | null |
| RES900456 | RT007 | **EXPIRED** | 2026-02-01 14:00:00 |
| RES900789 | RT008 | **EXPIRED** | 2026-02-01 13:45:00 |

### `room_inventory` — after

| room_type_id | date | available_count |
|---|---|---|
| RT007 | 2026-02-10 | **7** |
| RT007 | 2026-02-11 | **7** |
| RT007 | 2026-02-12 | **1** |
| RT008 | 2026-02-10 | **5** |
| RT008 | 2026-02-11 | **5** |
| RT008 | 2026-02-12 | **5** |

> The inventory is restored. The rooms are available again for new bookings.

---

> [!note] Why `check_out - INTERVAL '1 day'`?
> If a guest checks in Feb 10 and checks out Feb 13, they occupy the room on nights Feb 10, 11, and 12.
> Feb 13 is the departure date — they are not sleeping there that night.
> So we only restore inventory for Feb 10, 11, 12 — which is `check_in` to `check_out - 1 day`.

> [!tip] How often should this job run?
> Every 1 minute is a reasonable default.
> Running it too rarely means rooms sit "ghost-held" and unavailable for too long.
> Running it every second is unnecessary overhead for a booking system at this scale.
