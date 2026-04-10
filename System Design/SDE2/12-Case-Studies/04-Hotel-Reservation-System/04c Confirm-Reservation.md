# Confirm Reservation — After OTP Verified

This is the last step in the checkout flow. Before this API fires, the user has gone through:

| Page | What happens | Our server involved? |
|---|---|---|
| Page 1 — Personal Details | User fills name, phone, email | No — client-side form |
| Page 2 — Card Details | Card sent to Stripe → `paymentToken` returned | No — Stripe handles it |
| Page 3 — OTP | Bank sends OTP to phone, user verifies (3DS) | No — bank handles it |
| **After OTP verified** | **`POST /reservations/confirm` fires** | **Yes** |

Only after all 3 pages are done does our server get involved again. The reservation has been `PENDING` this entire time.

---

## What Happens at This Step

Two things must happen **atomically**:

1. **Upgrade** the reservation from `PENDING` → `CONFIRMED`
2. **Record** the payment

---

## Tables Before the Transaction

### `reservations`

| reservation_id | reservation_token | user_id | room_type_id | status | total_price | expires_at | confirmed_at |
|---|---|---|---|---|---|---|---|
| RES900456 | tok_9g4m03ne | U5002 | RT007 | **PENDING** | null | 2026-02-01 15:30:00 | null |

### `payments`

| payment_id | reservation_id | amount | status | paid_at |
|---|---|---|---|---|
| *(empty)* | | | | |

---

## The Transaction

```sql
BEGIN;

  -- Step 1: Upgrade the reservation to CONFIRMED
  -- The AND status = 'PENDING' check is a safety guard (explained below)
  UPDATE reservations
  SET status       = 'CONFIRMED',
      total_price  = 540,
      expires_at   = NULL,
      confirmed_at = NOW()
  WHERE reservation_id = 'RES900456'
    AND status         = 'PENDING';

  -- Step 2: Record the payment
  INSERT INTO payments
    (payment_id, reservation_id, amount, status, payment_token, paid_at)
  VALUES
    ('PAY001', 'RES900456', 540, 'SUCCESS', 'pay_tok_stripe_4xYz', NOW());

COMMIT;
```

---

## Tables After the Transaction

### `reservations`

| reservation_id | reservation_token | user_id | room_type_id | status | total_price | expires_at | confirmed_at |
|---|---|---|---|---|---|---|---|
| RES900456 | tok_9g4m03ne | U5002 | RT007 | **CONFIRMED** | **540** | **null** | **2026-02-01 15:20:00** |

> `expires_at` is cleared — the reservation is permanent now.
> `total_price` is set — it was null during PENDING because we hadn't confirmed the amount yet.

### `payments`

| payment_id | reservation_id | amount | status | payment_token | paid_at |
|---|---|---|---|---|---|
| PAY001 | RES900456 | 540 | SUCCESS | pay_tok_stripe_4xYz | 2026-02-01 15:20:00 |

---

> [!important] Why `AND status = 'PENDING'` in the UPDATE?
> This is a safety guard for a specific race condition:
>
> What if the user takes exactly 15 minutes to fill in card details — and the background job expires their hold at the same moment they hit "Pay"?
>
> Without the check:
> - Background job marks reservation as `EXPIRED` and restores inventory
> - Confirm transaction still runs → sets status to `CONFIRMED`
> - Someone else may have already booked that room → **double booking**
>
> With `AND status = 'PENDING'`:
> - If background job already set status to `EXPIRED`, this UPDATE affects **0 rows**
> - We detect that (rows affected = 0) and return a `409 RESERVATION_EXPIRED` error to the user
> - No double booking

> [!note] What about the payment — was the card charged?
> Yes — the charge to Stripe happens **before** this transaction.
> If the reservation was already expired, we must issue a refund to the card.
> This is why payment systems have a refund API — this exact scenario is a known edge case every booking platform handles.
