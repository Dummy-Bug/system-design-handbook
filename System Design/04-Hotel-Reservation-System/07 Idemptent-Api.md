An idempotent API guarantees:

> Multiple identical requests result in **one logical operation** and **one final state**, without creating duplicates.

It does NOT mean the response payload is always identical at every step. It means side effects happen once. 

[[Idempotency.pdf]]

## Idempotency Table

`idempotency ----------- key (PK) request_hash response_payload status   -- IN_PROGRESS, COMPLETED created_at expires_at`

Purpose:

- Deduplicate Reserve API calls
    
- Handle retries and refreshes
    

---

## Reservation Table

`reservation ----------- id (PK) user_id hotel_id room_type_id start_date end_date status price_snapshot created_at expires_at`

Purpose:

- Track booking lifecycle
    
- Drive UI workflow
    
- Enforce state machine
    

---

# STEP 1 — User Clicks "Reserve"

Browser:
`bookingKey = UUID() sessionStorage["booking_key"] = bookingKey`
Request:
`POST /reservations Headers: Idempotency-Key: bookingKey`

---

# STEP 2 — Reservation Service Receives Request

### 2.1 Check Idempotency Table

SQL:

`SELECT response_payload, status FROM idempotency WHERE key = :bookingKey;`

---

### Case A — Already Exists (Retry / Refresh)

If found:

Return:

`response_payload`

STOP.

No DB mutation.

---

### Case B — New Request

Insert placeholder row:

`INSERT INTO idempotency (key, status, created_at, expires_at) VALUES (:bookingKey, 'IN_PROGRESS', now(), now() + interval '24 hours');`

---

# STEP 3 — Create Reservation Draft

Insert reservation:

`INSERT INTO reservation (id, user_id, hotel_id, room_type_id, start_date, end_date, status, created_at, expires_at) VALUES ('R001', :userId, :hotelId, :roomTypeId, :startDate, :endDate, 'STARTED', now(), now() + interval '15 minutes');`

Important:

- This is NOT confirmed booking.
    
- Inventory not yet locked permanently.
    
- Expiry protects abandoned carts.
    

---

# STEP 4 — Store Idempotency Result

Update idempotency row:

`UPDATE idempotency SET status = 'COMPLETED',     response_payload = '{ "reservation_id": "R001" }' WHERE key = :bookingKey;`

---

# STEP 5 — Return Reservation Page

Response:

`reservation_id = R001`

Browser renders review page.

---

# STEP 6 — Page Refresh Happens

Browser reuses:

`sessionStorage["booking_key"]`

Sends same request again.

Backend:

Runs:

`SELECT response_payload FROM idempotency WHERE key = :bookingKey;`

Returns:

`R001`

No new reservation row created.

---

# STEP 7 — User Clicks "Next Final Details"

Request:

`POST /reservations/R001/confirm-details`

---

## Backend Logic

Fetch state:

`SELECT status FROM reservation WHERE id = 'R001';`

---

### If status = STARTED

Update:

`UPDATE reservation SET status = 'DETAILS_CONFIRMED' WHERE id = 'R001';`

---

### If status already progressed

Return current UI state.

No duplicate effect.

---

# STEP 8 — User Clicks "Complete Booking"

Request:

`POST /reservations/R001/complete Headers: Payment-Idempotency-Key: pay-uuid`

---

# STEP 9 — Final Booking Transaction

Single DB transaction.

---

### 9.1 Lock Inventory Rows

`SELECT booked_rooms, total_rooms, overbooking_limit FROM room_type_inventory WHERE hotel_id = :hotelId AND room_type_id = :roomTypeId AND date BETWEEN :start AND :end FOR UPDATE;`

---

### 9.2 Validate Availability

Application logic:

`available = total + overbooking - booked`

If any day sold out:

ROLLBACK.

---

### 9.3 Increment Inventory

`UPDATE room_type_inventory SET booked_rooms = booked_rooms + 1 WHERE hotel_id = :hotelId AND room_type_id = :roomTypeId AND date BETWEEN :start AND :end;`

---

### 9.4 Update Reservation Status

`UPDATE reservation SET status = 'CONFIRMED' WHERE id = 'R001';`

---

### 9.5 Commit Transaction

Booking is now final.

---

# STEP 10 — Duplicate "Complete Booking" Click Happens

Backend checks:

`SELECT status FROM reservation WHERE id = 'R001';`

Finds:

`CONFIRMED`

Returns success response.

No inventory update.  
No payment retry.  
No duplicate row.

---

# What This Guarantees

---

## Duplicate Reserve Click

Blocked by:

- Idempotency table
    

---

## Page Refresh

Handled by:

- sessionStorage reuse
    
- Idempotency replay
    

---

## Double Complete Booking Click

Blocked by:

- Reservation state machine
    
- Payment idempotency
    

---

## Overselling

Blocked by:

- Inventory row locking