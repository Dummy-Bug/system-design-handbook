**Authentication Note** All APIs assume JWT-based authentication. `user_id` is always extracted from the JWT token server-side — never sent explicitly in request body.

---

**1. Create Auction**

```http
POST /api/v1/auctions
Authorization: Bearer <token>

Request:
{
    "item_id": "string",
    "item_name": "string",
    "number_of_items": "int",
    "starting_bid_price": "decimal",
    "auction_start_time": "epoch_ms",
    "auction_end_time": "epoch_ms"    // optional
}

Response 201 Created:
{
    "auction_id": "string",           // server generated
    "success": true,
    "message": "Auction created successfully",
    "error": null
}
```

---

**2. View Single Auction**

```http
GET /api/v1/auctions/:auction_id
Authorization: Bearer <token>

Response 200:
{
    "auction_id": "string",
    "item_id": "string",
    "item_name": "string",
    "number_of_items": "int",
    "starting_bid_price": "decimal",
    "current_highest_bid": "decimal",
    "auction_start_time": "epoch_ms",
    "auction_end_time": "epoch_ms",
    "status": "active" / "closed" / "upcoming"
}
```

---

**3. View All Auctions (Cursor-based Pagination)**

```http
GET /api/v1/auctions?cursor=<auction_id>&limit=20&status=active
Authorization: Bearer <token>

Response 200:
{
    "auctions": [...],
    "next_cursor": "string",    // null if no more results
    "limit": 20
}
```

**Why cursor over offset:**

- Auctions are time-sensitive — new auctions appear constantly
- Offset pagination gives inconsistent results when data shifts (e.g. page 2 might repeat or skip items)
- Cursor always gives stable, consistent results regardless of new data coming in

---

**4. Create Bid**

```http
POST /api/v1/auctions/:auction_id/bids
Authorization: Bearer <token>

Request:
{
    "bid_amount": "decimal"
}

Response 201 Created:
{
    "bid_id": "string",             // server generated
    "auction_id": "string",
    "bid_amount": "decimal",
    "bid_timestamp": "epoch_ms",
    "status": "accepted" / "rejected"   // rejected if bid is too low or auction closed
}
```

---

**5. Get Bid History for Auction**

```http
GET /api/v1/auctions/:auction_id/bids?cursor=<bid_id>&limit=20
Authorization: Bearer <token>

Response 200:
{
    "bids": [
        {
            "bid_id": "string",
            "bid_amount": "decimal",
            "bid_timestamp": "epoch_ms",
            "status": "accepted" / "rejected"
        }
    ],
    "next_cursor": "string" / null
}
```

---

**6. Get Current Highest Bid**

```http
GET /api/v1/auctions/:auction_id/bids/highest
Authorization: Bearer <token>

Response 200:
{
    "bid_id": "string",
    "bid_amount": "decimal",
    "bid_timestamp": "epoch_ms"
}
```

---

**7. Close Auction (Admin)**

```http
PATCH /api/v1/auctions/:auction_id
Authorization: Bearer <token>

Request:
{
    "status": "closed"
}

Response 200:
{
    "auction_id": "string",
    "status": "closed",
    "winning_bid_id": "string",
    "winning_bid_amount": "decimal"
}
```

---

**Real-time Bid Updates**

Pull-based APIs alone are not sufficient for auctions. Users need to know immediately when they are outbid.

```Java
// WebSocket connection per user:
WS /api/v1/auctions/:auction_id/live
Authorization: Bearer <token>

// Server pushes on every new bid:
{
    "event": "new_bid",
    "bid_amount": "decimal",
    "bid_timestamp": "epoch_ms",
    "outbid": true / false // tells current user if they were                                 outbid
}
```

**Why WebSocket over SSE:**

- Bids flow server → client (new bid notifications) ✅
- But client also sends bids server → same connection handles both
- SSE would need a separate HTTP connection for sending bids → wasteful
- WebSocket handles both directions on a single persistent connection ✅