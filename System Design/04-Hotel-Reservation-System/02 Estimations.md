
## Hotel Chain Size

Assume Marriott-scale system:

`Number of hotels = 5,000 Total rooms across all hotels = 1,000,000`

---

## Overbooking Policy

Industry practice allows controlled overbooking.

Assumption:

`10% overbooking allowed`

So effective sellable inventory:

`1,000,000 × 1.1 = 1,100,000 rooms`

---

## Occupancy Rate

Average industry occupancy:

`70%`

Occupied rooms at any time:

`1,100,000 × 0.7 = 770,000 rooms`

---

## Average Stay Duration

Assume:

`Average stay = 3 days`

---

# Booking Throughput Calculation

Rooms turning over per day:

`Daily check-ins ≈ Occupied rooms / Average stay`

Substitute values:

`770,000 / 3 ≈ 256,666 bookings per day`

Rounded:

`≈ 250,000 bookings per day`

---

# Convert To QPS

Seconds per day:

`24 × 60 × 60 = 86,400 seconds`

Now compute QPS:

`256,666 / 86,400 ≈ 2.97`

Rounded:

`≈ 3 booking requests per second (average)`

---
### PeakLoad
`10x ~ 30 bookings per second`
