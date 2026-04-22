
> [!info] RabbitMQ is a message broker — a server that sits between producers and consumers, accepting messages from one side and routing them to the other. The producer never talks to the consumer directly. Everything goes through RabbitMQ.

---

## The problem RabbitMQ solves

Imagine your e-commerce platform needs to do three things every time an order is placed: update inventory, send a confirmation email, and notify the fraud detection service. The naive approach is to call all three services directly from the order service.

```
Order Service → inventoryService.reserve()
             → emailService.sendConfirmation()
             → fraudService.check()
```

This works until it doesn't. If the email service is slow, the order response waits. If fraud detection crashes, the whole order fails. And every time you add a new downstream service, you change the order service.

RabbitMQ puts a broker in the middle. The order service publishes one message — "order placed" — and walks away. RabbitMQ takes it from there.

```
Order Service → RabbitMQ → inventory.queue   → Inventory Worker
                         → email.queue       → Email Worker
                         → fraud.queue       → Fraud Worker
```

The order service doesn't know how many consumers exist. It doesn't care if email is slow or if fraud detection restarts. It just publishes and moves on.

---

## Exchanges — the routing layer SQS doesn't have

In SQS, the producer writes directly to a queue by name. You know the queue, you publish to it. Simple — but if three services need the same message, the producer has to send it three times to three different queues. The producer is now coupled to every downstream consumer.

RabbitMQ puts an **exchange** between the producer and the queues. The producer sends to the exchange with a routing key. The exchange applies rules to decide which queue(s) the message lands in — one queue, multiple queues, or none.

```
SQS:
  Producer → queue_name → Queue

RabbitMQ:
  Producer → exchange + routing_key → [ routing rules ] → Queue A
                                                         → Queue B
                                                         → Queue C
```

The producer never names a queue. It just says "here is the message, here is the key" — the exchange handles distribution. Add a new consumer queue, bind it to the exchange, and it starts receiving messages without any change to the producer.

There are four exchange types (direct, fanout, topic, headers) — each with different routing behaviour. They're covered in depth in the exchange files.

---

> [!important] RabbitMQ deletes messages after they are acknowledged. There is no replay. Once a message is ACKed, it's gone. If you need to re-process historical events, RabbitMQ is the wrong tool.

> [!tip] **Interview framing:** "I'd use RabbitMQ when I need per-message routing and guaranteed task delivery — for example, order processing where each order needs to reach inventory, email, and fraud services based on routing rules. The broker tracks ACKs and redelivers on consumer crash. If I needed to replay events or handle millions of events per second, I'd use Kafka instead — but for task queues where each message is a unit of work, RabbitMQ is the right fit."
