
> [!info] SLO is the target. SLI is the measurement. Writing a number in the NFR is easy — knowing whether you're actually hitting it in production requires instrumentation.

---

## The gap between design and reality

When you design WhatsApp, you calculate: Redis inbox read ~1ms, message write to DynamoDB ~5ms, delivery worker flush ~10ms. You conclude p99 message delivery latency should be well under 500ms.

But those are estimates. Production is not a whiteboard.

Maybe the Kafka consumer for registry writes is lagging — users appear offline longer than expected. Maybe DynamoDB hot partitions are spiking write latency during peak. Maybe the connection server is dropping WebSocket connections under load and clients aren't reconnecting fast enough.

None of this shows up in your estimates. It only shows up when you measure.

---

## What SLI actually means

SLI stands for Service Level Indicator. It is the actual measured value of the thing your SLO is about.

```
SLO (target):   p99 message delivery latency < 500ms
SLI (reality):  actual measured p99 = 320ms  ← this is what you observe in production
```

The SLO tells you what you promised. The SLI tells you what you delivered. The only way to know if you're meeting your SLO is to continuously measure the SLI and compare.

---

## WhatsApp's SLOs and their SLIs

From the NFR:

```
SLO 1:  p99 message delivery latency < 500ms
SLI 1:  time from message send to delivery ack, measured on every message

SLO 2:  99.99% message delivery success rate
SLI 2:  messages delivered / messages sent, measured continuously

SLO 3:  99.9% connection success rate
SLI 3:  successful WebSocket connections / total connection attempts
```

Message delivery and connection success are separate SLOs because they are independent paths. A connection server failure can tank connection success rate while message delivery for already-connected users is fine. Measuring separately means separate alerting — a connection storm pages someone even while delivery is healthy.

---

## Measuring delivery latency end-to-end

Delivery latency is the time from when the sender's app server receives the message to when the recipient's connection server delivers it.

```
T1: app server receives message from Alice → records timestamp
T2: connection server delivers message to Bob → records timestamp
Delivery latency = T2 - T1
```

Both timestamps are recorded server-side — no client clock involved, no clock skew. The delivery ack that Bob's device sends back carries the T2 timestamp, which the app server matches to the original message.

> [!tip] Interview framing
> "Three SLOs: delivery latency p99 < 500ms, delivery success rate 99.99%, connection success rate 99.9%. Measured separately — a connection storm shouldn't dilute delivery metrics. Latency is measured server-to-server to avoid client clock skew."
