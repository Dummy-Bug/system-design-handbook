
> [!info] What happens to messages when DynamoDB is down
> When the circuit is open, new message writes fail fast. The question is: are messages lost, and what does the user see?

---

## New messages — fail fast, tell the user

When the circuit breaker is open, any attempt to send a new message returns immediately without touching DynamoDB. The app server returns a 503 Service Unavailable to the connection server, which sends a WebSocket error back to the client.

```
Alice tries to send Bob a message
→ App server: circuit is OPEN
→ Returns 503 immediately (no DB call made)
→ Connection server: sends WS error to Alice

{
  "type": "ERROR",
  "code": "SERVICE_UNAVAILABLE",
  "message": "Unable to send message. Please try again shortly.",
  "retry_after_ms": 5000
}

→ Alice's UI: message marked as failed, "tap to retry"
```

Alice knows her message wasn't sent. She can retry once DynamoDB recovers. No message is silently dropped.

---

## In-flight messages — no partial state

A concern is messages that were mid-write when DynamoDB went down. Could a message be partially written — consumed from the client but not persisted?

DynamoDB writes are atomic. A write either commits fully or fails. There is no partial state. If the write failed, the message was never recorded in the system.

```
Message never written to DB = message never sent (from system's perspective)
Message written to DB       = message will be delivered (delivery worker picks it up)
```

The client receives an error for the failed write and the user sees the message as unsent. They retry when the service recovers.

---

## Messages already in DB — unaffected

Messages that were successfully written to DynamoDB before the outage are safe. They sit in the messages table and pending_deliveries table. When DynamoDB recovers and the circuit closes, the delivery worker resumes and delivers them.

```
DynamoDB recovers
→ Circuit moves to HALF-OPEN → test request succeeds → CLOSED
→ Delivery workers resume reading pending_deliveries
→ All queued messages delivered
→ Users receive messages with a delay but nothing is lost
```

> [!important] The system's durability guarantee
> A message is either in DynamoDB (safe, will be delivered) or never written (client received an error). There is no third state. Durability is guaranteed for anything that made it into the DB — the outage only affects new writes during the downtime window.

> [!tip] Interview framing
> "When the circuit is open, new writes fail fast with a 503. The client sees the message as unsent and can retry. There's no message loss — DynamoDB writes are atomic, so a failed write means the message was never recorded and the client is notified. Messages already in DB are delivered once the circuit closes."
