
> [!info] RabbitMQ stands out for broker-side routing. SQS is a simple queue and usually relies on SNS or application-side routing for fanout. Kafka fanout happens through topic subscription and multiple consumer groups.

---

## The same event, multiple services

Suppose one event arrives:

```text
ad.click
```

And three services want it:

- billing
- fraud
- analytics

How the event reaches all three is very different across the systems.

---

## SQS

Plain SQS is just a queue:

```text
Producer -> one queue -> one worker flow
```

If multiple services all need the same event, one queue is wrong because the consumers would compete for the same message.

So AWS usually adds SNS:

```text
Producer -> SNS topic -> billing SQS queue
                     -> fraud SQS queue
                     -> analytics SQS queue
```

That means SQS alone is not the fanout layer.

---

## RabbitMQ

RabbitMQ has routing built in:

```text
Producer -> exchange -> billing.queue
                     -> fraud.queue
                     -> analytics.queue
```

The exchange can broadcast, do exact-key routing, or pattern-based routing depending on exchange type and bindings.

This is why RabbitMQ is called routing-first.

---

## Kafka

Kafka handles fanout differently:

```text
Producer -> ad-events topic
Billing consumer group reads
Fraud consumer group reads
Analytics consumer group reads
```

The event sits once in the log, and each consumer group independently reads it.

So Kafka fanout is not "copy to many queues." It is "many groups independently read the same retained event stream."

---

## The clean contrast

```text
SQS       -> simple queue, fanout usually via SNS or app logic

RabbitMQ  -> exchange routes to one or many queues

Kafka     -> topic is shared history, fanout via multiple consumer groups
```

---

> [!important] What it guarantees
> RabbitMQ provides first-class broker-side routing. Kafka provides shared stream subscription. AWS typically uses SNS with SQS for pub/sub fanout.

> [!danger] What it doesn't guarantee
> Putting many consumers on one SQS queue does not create fanout. They compete; they do not each get a copy.


> [!tip] Interview framing
> "If I need rich broker-side routing, RabbitMQ is strongest. If I'm on AWS and just need fanout to worker queues, I'd typically use SNS plus SQS. If I need multiple services to independently read the same retained stream, Kafka is the better fit."
