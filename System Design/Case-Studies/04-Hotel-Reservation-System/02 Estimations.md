## Scale Assumptions

We are designing for a Marriott-scale hotel chain.

| Parameter                     | Value     |
| ----------------------------- | --------- |
| Number of hotels              | 5,000     |
| Total rooms across all hotels | 1,000,000 |
|                               |           |

---

## Step 1 — Overbooking Policy

Hotels intentionally sell slightly more rooms than they have. This is standard industry practice — based on the fact that a predictable percentage of bookings always get cancelled before check-in.

**Assumption: 10% overbooking allowed**

So the effective number of rooms we can sell is:

```
1,000,000 rooms × 1.1 = 1,100,000 sellable rooms
```

> [!note] Why overbooking exists
> Airlines and hotels know from historical data that roughly 5–15% of bookings cancel. Rather than leaving those rooms empty (lost revenue), they sell a few extra slots. If more people show up than expected, they compensate — this is why hotels sometimes "walk" a guest to a nearby property.

---

## Step 2 — Occupancy Rate

Not every sellable room is occupied at any given moment. Industry average occupancy is around 70%.

**Occupied rooms at any time:**

```
1,100,000 × 0.70 = 770,000 rooms occupied
```

Think of it like a parking lot with 1,100 spots — at any given hour, about 770 of them have cars in them.

---

## Step 3 — Average Stay Duration

**Assumption: guests stay an average of 3 nights**

---

## Step 4 — Daily Bookings

### Step 4a — Find the rate for 1 room

1 room, average stay 3 nights → that room gets a new guest once every 3 days.

So per day, 1 room generates:

```
1 ÷ 3 = 1/3 of a booking per day
```

### Step 4b — Scale to all rooms

```
770,000 rooms × (1/3 booking per day) = 256,666 bookings per day
```

Which is the same as:

```
770,000 ÷ 3 ≈ 256,666 bookings per day
```

Rounded: **≈ 250,000 bookings per day**

> [!tip] The intuition
> The longer guests stay, the slower rooms turn over, and the fewer new bookings happen per day.
> 10-night average → 770,000 ÷ 10 = 77,000 bookings/day
> 1-night average  → 770,000 ÷ 1  = 770,000 bookings/day

> [!note] Why divide by average stay?
> If everyone stayed 1 night, you'd need 770,000 new bookings every single day — full turnover.
> If everyone stayed 10 nights, you'd only need 77,000 new bookings per day — slow turnover.
> Dividing by the stay length tells you the *rate* at which rooms cycle through new guests.

---

## Step 5 — Convert to QPS (Queries Per Second)

There are 86,400 seconds in a day:

```
24 hours × 60 minutes × 60 seconds = 86,400 seconds/day
```

Average booking QPS:

```
256,666 bookings ÷ 86,400 seconds ≈ 2.97 ≈ 3 bookings/second
```

---

## Step 6 — Peak Load

Traffic is never evenly distributed. Bookings cluster around lunch hours, evenings, and popular travel dates. A standard assumption is **10× peak over average**:

```
3 bookings/second × 10 = ~30 bookings/second at peak
```

---

## Summary

| Metric | Value |
|---|---|
| Total rooms | 1,000,000 |
| Sellable rooms (with overbooking) | 1,100,000 |
| Occupied rooms | 770,000 |
| Average stay | 3 nights |
| Daily check-ins | ~250,000 / day |
| Average QPS | ~3 bookings / second |
| Peak QPS | ~30 bookings / second |

> [!tip] Is 30 bookings/second a lot?
> Not really — this is a very manageable write throughput. The harder problem in hotel reservation is not raw QPS, but **concurrent users trying to book the same room at the same time** (the consistency problem from the requirements). A single popular room on New Year's Eve might get hundreds of simultaneous attempts.
