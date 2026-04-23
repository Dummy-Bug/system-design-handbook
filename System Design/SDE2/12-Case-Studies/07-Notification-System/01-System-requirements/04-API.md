## Who Calls This API?

There are two distinct callers with two distinct needs:

1. **Internal backend services** — the Instagram like service, Uber trip service, bank fraud detector. They call the send endpoint when an event happens that should notify a user.
2. **Users** — managing their own channel preferences, opting out of channels or notification types.

---

## Endpoint 1 — Send a Notification

```
POST /api/v1/notifications/send

Body:
{
  "notification_id":    "uuid-v4",          // idempotency key
  "receiver_id":        "user_123",         // who gets the notification
  "template_data":      {                   // content — title, body, sender info, deep link
    "title":            "John liked your photo",
    "body":             "Tap to view",
    "deep_link":        "instagram://post/abc123",
    "sender_name":      "John"
  },
  "preferred_channels": ["PUSH", "EMAIL"],  // caller's suggestion — not a mandate
  "scheduled_at":       "2024-01-15T09:00:00Z"  // optional — null means send now
}

Response: 201 Created
{
  "notification_id": "uuid-v4",
  "status": "accepted"
}
```

> [!info] "Accepted" not "Delivered"
> The response says `accepted`, not `delivered`. The system has persisted the request to a durable queue and guaranteed it will be processed. Actual delivery is async — the caller does not wait for the notification to land on the device.

---

## Why `notification_id` as an Idempotency Key

The calling service might retry on a timeout. Without an idempotency key, the system processes the request twice and the user gets two "John liked your photo" notifications. With `notification_id`, the system checks "have I seen this ID before?" before processing. If yes — drop it, return the original response. If no — process it.

The caller generates `notification_id` before sending. If it retries with the same `notification_id`, the system recognises it as a duplicate and does nothing.

```
Caller sends POST with notification_id = "abc-123"
  → System processes, stores status for "abc-123"
  → Network timeout — caller doesn't receive 201

Caller retries with same notification_id = "abc-123"
  → System checks: "abc-123" already processed
  → Returns 201 without reprocessing
  → User gets exactly one notification
```

---

## Why `preferred_channels` is a Suggestion, Not a Mandate

The caller says which channels it prefers — push, SMS, email, or a combination. But the system filters these against the user's stored preferences before dispatching. If the user has opted out of SMS, the system drops SMS from the list even if the caller requested it.

This keeps the decision of "what channels does this user want" centralised in the notification system — the caller doesn't need to know each user's preferences.

```
Caller requests: ["PUSH", "SMS"]
User preference: SMS opted out
System dispatches: ["PUSH"] only
```

---

## Why `sender_id` is NOT a Top-Level Field

An early instinct is to include `sender_id` as a top-level routing field. But the notification system doesn't need to know who sent it — it only needs to know who receives it and what content to show. Sender information (name, avatar) belongs inside `template_data` as content, not as a routing field.

> [!danger] Don't leak domain logic into the notification system
> The notification system is infrastructure — it delivers messages. It should not understand Instagram's social graph or Uber's trip model. All domain-specific data (sender name, trip details, transaction amount) belongs in `template_data` as opaque content.

---

## Endpoint 2 — Update User Preferences

```
PATCH /api/v1/preferences/{user_id}

Body:
{
  "opted_out_channels":    ["SMS"],               // channels to disable
  "notification_types":    ["MARKETING", "LIKES"] // which types this applies to
}

Response: 200 OK
{
  "user_id": "user_123",
  "updated_at": "2024-01-15T09:00:00Z"
}
```

---

## Why PATCH and Not PUT or POST

**Not POST** — preference records are bootstrapped for every user at signup with all channels enabled. The record already exists. POST would imply creating a new resource.

**Not PUT** — PUT replaces the entire resource. If the user sends `opted_out_channels: ["SMS"]`, a PUT would wipe out all their other preferences and replace with just this. That's destructive.

**PATCH** — updates only the fields sent. The user changes SMS opt-out; everything else stays as-is. Also idempotent — calling PATCH twice with the same body produces the same result.

> [!important] Preference reads must be strongly consistent
> When the system checks user preferences before dispatching, it must read the latest value — not a stale cached copy. If a user opts out of SMS and the cache hasn't refreshed, they'll receive an unwanted SMS. User preferences are the one place in this system where eventual consistency is not acceptable.

---

## API Summary

| Endpoint | Method | Caller | Purpose |
|---|---|---|---|
| `/api/v1/notifications/send` | POST | Internal services | Register a notification for delivery |
| `/api/v1/preferences/{user_id}` | PATCH | Users | Update channel/type preferences |
