# Point-to-Point Queue

> [!info] A point-to-point queue distributes work across multiple consumers. One message goes to exactly one consumer. No two consumers ever process the same message.

---

## The problem it solves

You have 10,000 photos that need thumbnail generation. You have 50 worker servers. How do you distribute the work without two workers resizing the same photo?

You drop all 10,000 jobs into a queue. Each worker picks one message at a time, processes it, picks the next.

```
Queue: [photo_1, photo_2, photo_3 ... photo_10000]

Worker A picks photo_1 → resizes it → done
Worker B picks photo_2 → resizes it → done
Worker C picks photo_3 → resizes it → done
```

Each message goes to exactly one worker. The queue distributes the work automatically.

---

## How the queue prevents two workers from getting the same message — Visibility Timeout

When Worker A picks up photo_1, the queue doesn't delete it immediately. Instead it makes photo_1 **invisible** to all other workers for a set time window — say 30 seconds.

```
Worker A requests a message
→ Queue gives photo_1 to Worker A AND hides it from everyone else (atomic operation)
→ Worker B requests a message → only sees photo_2, photo_3... photo_1 doesn't exist for it
→ Worker A finishes → sends ACK → queue deletes photo_1 permanently
```

The "give and hide" is one **atomic operation** — there is no gap between them where another worker could sneak in and grab the same message.

> [!important] The queue only deletes a message after receiving an ACK from the consumer. Until then, the message is just hidden — not gone.

---

## What happens if the worker crashes mid-task?

```
Worker A picks photo_1 → visibility timeout starts (30 seconds)
Worker A crashes at 15 seconds → never sends ACK
30 seconds pass → photo_1 becomes visible again
Worker B picks photo_1 → processes it → ACKs → deleted
```

The job doesn't get lost. It reappears after the timeout and another worker picks it up.

> [!danger] The visibility timeout must be longer than the expected task time. If resizing takes 45 seconds and your timeout is 30 seconds, the queue assumes Worker A crashed and hands photo_1 to Worker B — while Worker A is still working on it. Now two workers are resizing the same photo. Set timeout to at least 2x expected task time to be safe.

---

## What if two workers request the same message simultaneously?

The queue handles it atomically — only one worker wins.

```
Worker A and Worker B both request a message at the same time
Queue picks one atomically — gives photo_1 to Worker A, hides it
Worker B gets back: "nothing available"
```

The tie-breaking is first-come-first-served (or random in some implementations like SQS). It doesn't matter which worker wins — what matters is exactly one worker gets the message.

---

## When to use point-to-point

Use it when you're **distributing work** — you have a pool of tasks and a pool of workers, and each task should be done exactly once.

```
Image resizing       → drop resize jobs in queue, 50 workers drain it
Email sending        → drop email jobs in queue, workers send them
Video transcoding    → drop video jobs in queue, workers transcode
Payment processing   → drop payment jobs in queue, workers process them
```

> [!tip] The mental model: point-to-point is a **task queue**. Think of it as a to-do list that multiple workers share. Each item gets crossed off exactly once.
