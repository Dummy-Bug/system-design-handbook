
> [!info] Availability is not "is the server running?" — it is "did the message get delivered?" A connection server can be alive and dropping every message it handles. That is not available.

---

## The health check trap

The instinct when monitoring availability is to ping the server — send a heartbeat every few seconds and check if it responds. If it responds, it's up.

Consider this scenario:

```
App server is running ✓
Health check endpoint returns 200 ✓
But: DynamoDB circuit breaker is OPEN
Result: every message write returns 503
```

From the health check perspective: server is healthy. From the user's perspective: no messages are being sent. The health check missed the actual failure entirely.

Availability must be measured on real user requests, not synthetic pings.

---

## The availability SLI formula

```
Availability = successful operations / total operations
```

**Message delivery availability:**

Each app server tracks two counters:
- `messages_attempted` — incremented on every message received
- `messages_delivered` — incremented when delivery ack received from recipient

```
Delivery availability = messages_delivered / messages_attempted
Target: 99.99%
```

**Connection success availability:**

Each connection server tracks:
- `connection_attempts` — incremented on every WebSocket upgrade request
- `connection_successes` — incremented on successful WebSocket establishment

```
Connection availability = connection_successes / connection_attempts
Target: 99.9%
```

---

## What counts as success for message delivery

```
Message sent → delivery ack received within 30s     ✓ success
Message sent → recipient offline → pending_deliveries → delivered on reconnect  ✓ success
Message sent → DynamoDB circuit OPEN → 503 returned  ✗ failure
Message sent → app server timeout                    ✗ failure
Message sent → rate limited (429)                    ✓ success (system worked correctly)
```

Rate limited messages count as successes — the system responded correctly to an abusive client. A 503 from a DynamoDB outage counts as a failure — the system broke.

Pending delivery (offline recipient) counts as a success — the message is durably stored and will be delivered. The system fulfilled its contract.

---

## What counts as success for connections

```
WebSocket upgrade → connection established → authenticated  ✓ success
WebSocket upgrade → server overloaded → 503               ✗ failure
WebSocket upgrade → invalid auth token → 401              ✓ success (system worked correctly)
WebSocket upgrade → timeout                                ✗ failure
```

401 is a success — the system correctly rejected a bad token. 503 under load is a failure — the system couldn't serve the request.

---

## Separate availability per path

Message delivery and connection success run on different infrastructure and have different failure modes. Measuring them separately means a connection storm pages immediately even while delivery metrics look healthy.

```
Connection availability SLI:  connection_successes / connection_attempts  → target 99.9%
Delivery availability SLI:    messages_delivered / messages_attempted     → target 99.99%
```

> [!tip] Interview framing
> "Availability is measured on real traffic — successful operations divided by total. Rate limiting and 401s count as successes. 503s and timeouts count as failures. Pending delivery counts as success — message is durable. Connection and delivery are tracked separately so a connection server failure alerts independently of delivery health."
