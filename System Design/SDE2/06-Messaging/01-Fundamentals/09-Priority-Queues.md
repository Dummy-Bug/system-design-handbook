
> [!info] A priority queue breaks the normal FIFO rule — messages with higher priority are processed before lower priority messages, regardless of when they arrived.


## The problem

You're building a hospital notification system. Two alerts arrive simultaneously:

```
→ priority: LOW  "Dr. Smith, your lunch is ready"
→ priority: HIGH "Patient in Room 4 is flatlining"
```

In a normal FIFO queue, whichever arrived first gets processed first. That's wrong — the flatline alert must always go first, no matter what.

---

## How it works

The **producer** sets the priority when dropping the message. The producer knows the context — the hospital monitoring system knows a flatline is critical, the cafeteria system knows lunch is low priority. The queue doesn't decide what's urgent, the producer does.

```
Hospital monitor  → publishes { message: "flatline alert", priority: HIGH }
Cafeteria system  → publishes { message: "lunch ready", priority: LOW }
```

The queue internally uses a heap data structure — every inserted message gets placed in the right position by priority. The consumer always picks from the front, which is always the highest priority message. The consumer doesn't need to know about priorities at all — it just picks from the front.

```
Queue internally (sorted by priority):
[HIGH: flatline, HIGH: cardiac arrest, MEDIUM: meeting in 5 mins, LOW: lunch ready]

Consumer picks: flatline → cardiac arrest → meeting → lunch ready
```

---

## The starvation problem

If HIGH priority messages keep flooding in constantly, LOW priority messages never get picked up. They wait forever. This is called **starvation**.

```
HIGH: alert1 arrives → picked up
HIGH: alert2 arrives → picked up
HIGH: alert3 arrives → picked up
LOW: lunch ready (arrived 20 mins ago) → still waiting...
HIGH: alert4 arrives → picked up
...
```

### The fix — aging

The longer a message sits in the queue unprocessed, the higher its priority gets bumped automatically.

```
LOW priority "lunch ready" arrives
→ sits for 10 minutes → bumped to MEDIUM
→ sits for 20 minutes → bumped to HIGH
→ now gets picked up before newer LOW priority messages
```

No message waits forever, no matter how busy the high priority lane is.

---

## Real use cases

```
Hospital systems     → critical alerts > routine notifications
Customer support     → paying customers > free tier users
Food delivery        → orders expiring soon > fresh orders
Payment processing   → high-value transactions > low-value ones
```

> [!tip] **Interview framing:** "I'd use a priority queue here because not all messages have equal urgency. The producer stamps each message with a priority level — the queue handles the ordering internally using a heap. To prevent starvation of low-priority messages, I'd configure aging so messages get their priority bumped up after sitting for too long."
