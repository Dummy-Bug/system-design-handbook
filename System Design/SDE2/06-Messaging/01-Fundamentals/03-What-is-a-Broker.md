
> [!info] A message broker is the infrastructure that sits between producers and consumers. Producers hand their messages to the broker. Consumers pull messages from the broker. Neither side talks to the other directly — the broker is the middle system that owns the queue, guarantees delivery, and handles all the distributed systems complexity in between.

---

## Why you need a broker at all

You've already seen the task queue concept — producer drops a message, a worker picks it up. So why not have the producer call the consumer directly?

```
Without broker:
Order Service → HTTP call → Email Service

Problems:
→ Email Service is down → Order Service call fails → user sees error
→ Email Service is slow → Order Service request takes longer
→ Add a new service? → Order Service code needs to change every time
```

Every new consumer you add means the producer needs to know about it. Every time a consumer is slow or down, the producer feels it. This is **tight coupling** — and it breaks at scale.

---

## The broker model

The broker decouples producers from consumers completely. The producer publishes to the broker and walks away. The broker holds the message. The consumers pull from the broker whenever they're ready.

```
Without broker:
Order Service → HTTP → Email Service
Order Service → HTTP → Inventory Service
Order Service → HTTP → Analytics Service
(Order Service knows about everyone)

With broker:
Order Service → Broker → Email Service
                       → Inventory Service
                       → Analytics Service
(Order Service knows about nobody)
```

Order Service doesn't know how many consumers exist, which ones are up, or how fast they process. It just publishes and moves on.

---

## What the broker actually does

The broker is responsible for everything that happens after the producer publishes:

**1. Durability** — the message is written to disk. If the broker crashes and restarts, the message is still there. The producer doesn't need to retry.

**2. Delivery tracking** — the broker knows which messages have been ACKed and which haven't. If a consumer crashes mid-processing, the message reappears automatically.

**3. Distribution** — multiple consumers can connect to the same broker. The broker distributes work across them.

**4. Routing** — the broker can route the same message to different queues based on rules. One message in, multiple queues out.

**5. Buffering** — the broker absorbs traffic spikes. If 100,000 messages arrive in a second and the consumer can only process 10,000/sec, the broker holds the other 90,000. The consumer drains at its own pace.

---

## Broker vs Queue

A queue is one delivery structure inside the broker — a list of messages waiting for a consumer. The broker is the entire system that hosts and manages those queues.

```
Broker = the post office
Queue  = one mailbox inside the post office

The post office (broker) can have many mailboxes (queues).
It manages routing, delivery, and retry for all of them.
```

One broker can host many queues with different routing rules and different consumers. The producer doesn't interact with queues directly — it hands messages to the broker, and the broker decides which queue they go into.

---

> [!important] The broker you pick determines what delivery semantics are possible, whether consumers can replay history, and how routing works. That's a design decision — not just an infrastructure choice. The next files cover the three brokers you'll use in system design interviews and exactly when to reach for each one.
