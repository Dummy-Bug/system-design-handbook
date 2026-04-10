# What Is a Message Broker

> [!info] A message broker is the middle system between producers and consumers.  
> Producers send messages to the broker. Consumers receive messages from the broker.  
> A queue is one pattern a broker can provide.

---

## The problem before brokers

Imagine an order service in an e-commerce app. After an order is placed, several things must happen:

```
1. Send confirmation email
2. Trigger warehouse packing
3. Update analytics
4. Run fraud checks
```

If the order service calls all of these systems directly in the user request path, request latency grows and failures cascade.

```
Order API
→ Email service is slow
→ Warehouse service times out
→ Analytics has a retry storm
→ User request becomes slow or fails
```

Now scale it:

```
10,000 orders/sec
4 downstream actions per order
=> 40,000 downstream operations/sec
```

One slow dependency can back up everything.

---

## The broker model

Instead of direct calls, the producer writes a message to the broker and returns quickly.

```
Order Service (producer)
→ publish { event: "order_placed", order_id: 123 }
→ broker stores message durably
→ Email worker consumes
→ Warehouse worker consumes
→ Analytics worker consumes
```

This creates decoupling:

- Producer and consumer can run at different speeds
- Temporary traffic spikes get buffered
- Consumer failures do not immediately fail producer requests

---

## Broker vs Queue

A broker and a queue are not the same thing.

- Broker = the system that stores/routes/delivers messages
- Queue = one delivery structure (work waiting in line)

Think of it this way:

```
Broker = post office
Queue  = one mailbox or one delivery line inside that post office
```

---

## Where Kafka fits

Kafka is a broker-based system, but its core storage model is an append-only log.

- A Kafka broker = one Kafka server node
- A Kafka cluster = many brokers
- Kafka can provide queue-like processing using consumer groups

But Kafka semantics differ from classic task queues:

```
SQS/RabbitMQ task queue:
consumer picks message
→ message becomes invisible (visibility timeout / lease)
→ ACK deletes it

Kafka:
consumer reads by offset
→ message stays in the log
→ another consumer group can still read it
```

So Kafka is not "just a queue." It can do queue-style work, but it is fundamentally a retained event log.

---

> [!important] What it guarantees
> Using a broker gives decoupling, buffering, and asynchronous processing boundaries.

> [!danger] What it doesn't guarantee
> A broker by itself does not guarantee exactly-once processing, strict global ordering, or zero data loss. Those depend on broker type and configuration.

---

> [!tip] Interview framing
> "A message broker is middleware between producers and consumers. Producers publish once; consumers process asynchronously. A queue is one delivery pattern inside a broker. Kafka is broker-based and can act like a queue with consumer groups, but unlike classic queues, messages are read by offset and retained for replay."
