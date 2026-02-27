
# Hotel APIs

---

## Get Hotel Details (Public)

Request:

`GET /api/v1/hotels/H1001`

Response:
```json
{
  "hotelId": "H1001",
  "name": "Marriott Times Square",
  "city": "New York",
  "rating": 4.5,
  "amenities": [
    "wifi",
    "pool",
    "gym"
  ],
  "address": "Manhattan, NY"
}
```

## Create Hotel (Admin Only)

Request:

`POST /api/v2/hotels`

Body:
```json
{
  "name": "Marriott Downtown",
  "city": "San Francisco",
  "rating": 4.3,
  "amenities": [
    "wifi",
    "spa"
  ],
  "address": "Market Street"
}

```

Response
```json
{
  "hotelId": "H2002"
}

```

## Update Hotel (Admin Only)

Request:

`PUT /api/v2/hotels/H2002`

Body:
```json
{
  "rating": 4.6,
  "amenities": [
    "wifi",
    "spa",
    "gym"
  ]
}
```

## Delete Hotel (Admin Only)

Request:

`DELETE /api/v2/hotels/H2002`

Response:
```json
{
  "status": "DELETED"
}

```

# Room APIs

---

## Get Room Details

Request:

`GET /api/v1/hotels/H1001/rooms/R301`

Response:
```json
{
  "roomId": "R301",
  "roomTypeId":"007", 
  "type": "DELUXE",
  "pricePerNight": 180,
  "capacity": 2,
  "status": "ACTIVE"
}
```

## Create Room (Admin Only)

Request:

`POST /api/v1/hotels/H1001/rooms`

Body:
```json
{
  "type": "SUITE",
  "pricePerNight": 350,
  "capacity": 4
}
```

Response:
```json
{   "roomId": "R450" }
```

## Update Room (Admin Only)

Request:

`PUT /api/v1/hotels/H1001/rooms/R450`

Body:
```json
{
  "pricePerNight": 375
}
```

## Delete Room (Admin Only)

Request:

`DELETE /api/v1/hotels/H1001/rooms/R450`

Response:
```json
{   "status": "DELETED" }
```

# Reservation APIs

## Create Reservation (Booking)

Request:
```http
POST /api/v1/reservations
```

Headers:
```http
Idempotency-Key: 82ks92jdks8s
```

Body:
```json
{
  "hotelId": "H1001",
  "roomTypeId":"007",
  "startDate": "2026-02-10",
  "endDate": "2026-02-13",
  "guestCount": 2,
  "userId": "U5001"
}
```
Reponse:
```json
{
  "reservationId": "RES900123",
  "roomtype":"Deluxe",
  "status": "CONFIRMED",
  "totalPrice": 540
}
```

## Get Reservation By ID

Request:

`GET /api/v1/reservations/RES900123`

Response:
```json
{
  "reservationId": "RES900123",
  "hotelId": "H1001",
  "roomId": "R301",
  "startDate": "2026-02-10",
  "endDate": "2026-02-13",
  "status": "CONFIRMED"
}
```

## List Reservations By User

Request:

`GET /api/v1/reservations?userId=U5001`

Response:
```json
[
  {
    "reservationId": "RES900123",
    "hotelId": "H1001",
    "status": "CONFIRMED"
  },
  {
    "reservationId": "RES900456",
    "hotelId": "H2002",
    "status": "CANCELLED"
  }
]

```

## Cancel Reservation

Request:

`DELETE /api/v1/reservations/RES900123`

Response:
```Json
{
  "reservationId": "RES900123",
  "status": "CANCELLED",
  "refundAmount": 360
}
```

 