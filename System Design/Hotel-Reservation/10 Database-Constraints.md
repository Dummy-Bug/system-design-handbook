### Core Idea

Do not “prevent” conflicts in application code.

Let the database **reject invalid states**.

You design rules at schema level so **illegal data cannot exist**.

The database becomes the final authority.

---

## Example: Room Booking Problem

Wrong design:

```
rooms:
id
total_reserved_count
```

This invites race conditions.

Correct design:

```
bookings:
booking_id
room_id
date
```

Now add constraint:

```sql
UNIQUE(room_id, date)
```

Meaning:

One room can be booked only once per date.

---

## What Happens During Race Condition

Two users try booking same room.

Both send insert:

```sql
INSERT INTO bookings(room_id, date)
VALUES (10, '2026-01-21');
```

---

### Database Behavior

Transaction A → succeeds  
Transaction B → fails with:

```
duplicate key value violates unique constraint
```

Result:

- No double booking
    
- No race condition
    
- No custom locking logic
    
- No version column
    

Database enforces correctness atomically.

---

# Why This Is Powerful

Because:

- Constraint checks are atomic
    
- Done inside storage engine
    
- Protected by internal locks
    
- Impossible to bypass accidentally
    

This is stronger than app-level optimistic locking.

---

# Types of Useful Constraints

---

## 1) UNIQUE Constraint

Prevents duplicates.

Used for:

- Seat booking
    
- Email uniqueness
    
- Order idempotency
    
- Payment reference IDs
    

Example:

```sql
UNIQUE(seat_id, show_id)
```

---

## 2) CHECK Constraint

Prevents invalid values.

Example:

```sql
CHECK (available_rooms >= 0)
```

Stops negative inventory bugs.

---

## 3) FOREIGN KEY Constraint

Prevents orphan records.

Example:

```sql
booking.room_id REFERENCES rooms(id)
```

Guarantees room exists.

---

## 4) EXCLUSION Constraint (PostgreSQL)

Prevents overlapping ranges.

Used for:

- Hotel room date ranges
    
- Meeting room schedules
    

Example:

```sql
EXCLUDE USING gist (
  room_id WITH =,
  daterange(start_date, end_date) WITH &&
)
```

Prevents overlapping bookings.

This is extremely powerful.

---

# Comparison With Other Methods

|Approach|Reliability|Complexity|Performance|
|---|---|---|---|
|Pessimistic Lock|High|High|Lower|
|Optimistic Lock|High|Medium|High|
|DB Constraint|Highest|Low|Highest|

Database constraints win for correctness.

---

# Brutal Truth

If your correctness depends on application code:

You already failed.

Because:

- Bugs happen
    
- Retries fail
    
- Services crash
    
- Network retries duplicate requests
    

Database constraints are the last safety net.

---

# Real Production Pattern

Strong systems combine:

1. Database constraints
    
2. Optimistic locking
    
3. Idempotency keys
    

Not just one.

Example flow:

- Try insert booking
    
- Unique constraint enforces exclusivity
    
- Version column handles concurrent updates
    
- Idempotency prevents duplicate API retries
    

Defense in depth.

---

# When NOT To Rely Only On Constraints

Constraints do NOT solve:

- Partial availability logic
    
- Business rules across multiple tables
    
- Soft reservations with timeouts
    
- Temporary seat holds
    

Those need application logic + locks.