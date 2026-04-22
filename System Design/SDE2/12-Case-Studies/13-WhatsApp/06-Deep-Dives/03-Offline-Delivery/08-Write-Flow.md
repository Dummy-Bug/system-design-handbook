
> [!info] The complete write flow — from Alice sending a message to Bob being offline
> Every step from Alice hitting send to the pending delivery entry being created.

---

## The full offline write flow

```
1. Alice hits send: "hey"
   → WebSocket sends to WS-Server-1

2. WS-Server-1 receives the message
   → calls INCR seq:conv_abc123 on Redis → gets seq=42

3. WS-Server-1 writes to DynamoDB messages table:
   PK=conv_abc123, SK=42
   content="hey", sender=alice, receiver=bob
   timestamp=4:20:00, s3_ref=null

4. WS-Server-1 attempts delivery to Bob:
   → GET ws:bob from Redis registry
   → No entry found → Bob is offline

5. WS-Server-1 checks pending_deliveries:
   → GET {receiver_id=bob, conversation_id=conv_abc123}
   → No entry exists

6. WS-Server-1 writes to pending_deliveries:
   { receiver_id: bob, conversation_id: conv_abc123, first_undelivered_seq: 42 }

7. WS-Server-1 calls Notification Service:
   → "Send push notification to Bob: Alice sent you a message"

8. Notification Service calls APNs/FCM:
   → delivers banner to Bob's phone
```

Steps 3, 6, and 7 happen in parallel — DynamoDB write, pending_deliveries write, and push notification are independent.

---

## What if Alice sends another message while Bob is still offline

```
Alice sends seq=43 "where are you?"

→ WS-Server-1 writes seq=43 to DynamoDB messages table ✓

→ Checks pending_deliveries: GET {bob, conv_abc123}
→ Entry already exists with first_undelivered_seq=42
→ Do nothing — no update needed

→ Calls APNs/FCM again:
  → New notification replaces previous one on Bob's phone
  → Bob sees: "Alice: where are you?" (latest message preview)
```

The pending_deliveries entry is written once. DynamoDB stores every message. APNs/FCM always shows the latest notification. Clean separation.

---

## What if Bob is offline across multiple conversations simultaneously

```
Alice sends to conv_abc123 → pending_deliveries: {bob, conv_abc123, seq=42}
Carol sends to conv_def456 → pending_deliveries: {bob, conv_def456, seq=17}
Dave sends to conv_ghi789  → pending_deliveries: {bob, conv_ghi789, seq=8}
```

Three separate rows in pending_deliveries, one per conversation. When Bob reconnects, a single query `PK=bob` returns all three — and the server fetches the catch-up messages for each conversation in parallel from DynamoDB.
