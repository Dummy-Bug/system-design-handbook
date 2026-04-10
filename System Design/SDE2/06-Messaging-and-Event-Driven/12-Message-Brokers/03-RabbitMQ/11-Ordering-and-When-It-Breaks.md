# Ordering and When It Breaks

> [!info] RabbitMQ can preserve queue order only in the simplest setup. Once you add multiple consumers, retries, redelivery, or parallel processing, end-to-end processing order becomes fragile.

---

## The simple case

If you have:

```text
one queue
one producer
one consumer
no redelivery
```

then messages are generally consumed in queue order.

That is the cleanest case for ordered processing.

---

## Why order breaks with multiple consumers

Suppose the queue contains:

```text
M1, M2, M3
```

Now two consumers process in parallel:

```text
Worker A gets M1
Worker B gets M2
Worker B finishes first
```

So business completion order becomes:

```text
M2 before M1
```

Even though queue delivery started in order, processing completion did not remain ordered.

---

## Why redelivery breaks order

Now add failure:

```text
Worker A gets M1
Worker A crashes before ACK
Worker B processes M2 and M3
RabbitMQ redelivers M1 later
```

Now the final business order may be:

```text
M2, M3, M1
```

So retries and crashes can reorder work significantly.

---

## The real lesson

RabbitMQ queue order is not the same as guaranteed business processing order.

If strict order matters for a workflow, you usually have to give up some concurrency:

```text
one queue
one active consumer
careful failure handling
```

That reduces throughput but protects sequence.

---

> [!important] What it guarantees
> RabbitMQ preserves queue order most clearly only in very constrained single-consumer flows.

> [!danger] What it doesn't guarantee
> RabbitMQ does not guarantee ordered completion once multiple consumers, retries, or redelivery enter the picture.

---

> [!tip] Interview framing
> "I treat RabbitMQ ordering as fragile under parallelism. If a workflow truly needs strict sequencing, I keep one active consumer per ordered queue and accept lower throughput as the cost of preserving order."
