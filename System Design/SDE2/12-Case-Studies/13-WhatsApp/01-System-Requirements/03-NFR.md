
> [!info] What NFRs actually do
> Functional requirements tell you *what* the system does. Non-functional requirements tell you *how well* it must do it. Every major design decision in the deep dives — connection protocol, storage engine, consistency model — will be justified by one of these NFRs.

---

## Availability

The system must be highly available. WhatsApp is daily communication infrastructure — people use it to coordinate work, family, emergencies. When it goes down, it's not a minor inconvenience like a URL shortener being unavailable. At 100M DAU, even 10 minutes of downtime affects millions of people mid-conversation.

```
Target: 99.9% initially (as product matures → 99.99%)

99.9%  = ~8.7 hours downtime/year
99.99% = ~52 minutes downtime/year
```

Starting at 99.9% is a pragmatic call — early in a product's life, infrastructure is still stabilising, failure modes aren't fully understood, and the engineering cost of 99.99% is significantly higher. Once the system is battle-tested, you tighten the target.

> [!important] What does "down" mean for a chat system?
> For a URL shortener, "down" is binary — redirects fail or they don't. For a chat system it's more nuanced. The system could be partially degraded: new messages can't be sent but existing ones are still readable, or delivery is delayed but not lost. Defining the availability SLO requires agreeing on what "unavailable" means — typically it's "users cannot send or receive messages."

---

## Latency

```
Target: p99 < 200ms end-to-end for message delivery
```

End-to-end means: message leaves sender's device → hits server → gets stored → arrives at recipient's device. All of that under 200ms for 99% of messages.

This is an aggressive target. WhatsApp's real-world p99 is closer to 200-500ms. Hitting 200ms means:

- The connection between client and server must be persistent (no connection setup overhead on every message — that alone costs 100ms+ for a fresh TCP + TLS handshake)
- Message routing must be fast — the server receiving the message needs to know immediately which server holds the recipient's connection
- Storage writes must be low-latency — you can't do a synchronous multi-hop database write in the hot path

> [!danger] 10ms is not realistic end-to-end
> 10ms is barely enough for one network round trip within the same data center. Across a city, network latency alone is 5-20ms. Across continents it's 100-200ms. End-to-end delivery to a different region will always exceed 10ms. 100-200ms is the realistic target for same-region delivery.

---

## Consistency

**Eventual consistency is acceptable** — with one important nuance.

Within a single conversation, messages must appear in the **correct order**. If Alice sends "hello" and then "how are you?", Bob cannot see them arrive as "how are you?" then "hello". This is ordering consistency within a conversation, not global strong consistency.

Across conversations, and for things like the inbox preview, slight staleness is fine. If the inbox shows a message arrived 2 seconds ago instead of 1 second ago, nobody notices or cares.

```
Within a conversation  → ordering must be preserved
Across conversations   → eventual consistency is fine
Inbox preview          → slight staleness acceptable
```

This is why chat systems are not the place for SERIALIZABLE isolation or global ordering — the cost is too high and the benefit is invisible to users.

---

## Durability

Once the server acknowledges a message as received, **it must not be lost**. This is a hard requirement.

The user experience contract is: when you see the single tick (message sent to server), you trust that message will eventually reach the recipient. If the server loses it after acknowledging, that's a broken promise and users lose trust in the system entirely.

```
Durability guarantee: if server sends ACK → message is persisted and will be delivered
```

This means: write to durable storage before sending the ACK back to the sender. You cannot ACK first and write later — that creates a window where a crash loses the message.

---

## Message Ordering

Messages within a conversation must be delivered in the order they were sent.

This sounds obvious but is genuinely hard in a distributed system. If two servers are both handling messages for the same conversation, they could deliver messages in different orders to different clients. The fix is to either route all messages for a conversation through the same server, or use sequence numbers per conversation that the client uses to reorder on arrival.

```
Requirement: messages in a conversation appear in sent order for all participants
```

---

## Scalability

The system must scale horizontally. Adding more servers should linearly increase capacity — both for connection handling (more users online simultaneously) and for message throughput (more messages per second).

This rules out any single-threaded bottleneck in the hot path. Every component — connection servers, message routers, storage — must be horizontally scalable.

---

## Summary

| NFR | Target |
|---|---|
| Availability | 99.9% initially → 99.99% at maturity |
| Message delivery latency (p99) | < 200ms end-to-end |
| Consistency | Eventual (ordering preserved within conversation) |
| Durability | No message loss after server ACK |
| Message ordering | Preserved within each conversation |
| Scalability | Horizontally scalable across all components |
