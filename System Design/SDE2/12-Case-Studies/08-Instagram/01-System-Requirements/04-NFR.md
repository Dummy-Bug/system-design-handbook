# Instagram Non-Functional Requirements

## Availability over Consistency

Instagram prioritises **availability**. If a user opens the app to scroll their feed or upload a post and the system is down, that is a direct product failure. People notice. They churn.

Consistency, on the other hand, can be relaxed. If a user posts a photo and their friend sees it 2 seconds later instead of instantly — nobody notices. If the feed shows posts from 30 seconds ago instead of the absolute latest — that is fine. The system should aim for **eventual consistency**: data will converge to the correct state, just not instantly.

The one exception is **read-your-own-writes**. After you upload a post, you must see it on your own profile immediately. Seeing a blank where your post should be feels like a bug even if it would resolve in seconds. Every other user can wait — you cannot.

---

## Latency

Instagram is a user-facing product. Latency is directly felt.

- **Feed load — under 200ms.** Beyond 200ms users perceive lag. Scrolling should feel instant.
- **Post upload — confirmation within 2-3 seconds.** The actual processing (compression, storage, fan-out) can be async. The user just needs to see "post uploaded" quickly. The post propagating to all followers can happen in the background.
- **Story view — under 200ms.** Same as feed load.

---

## Durability

Once a post is successfully uploaded it must never be lost — not from a server crash, not from a disk failure, not from a network blip. The user hit upload, the system confirmed it, the data is now the system's responsibility.

This is different from availability. Availability is about the system being reachable. Durability is about data surviving once it arrives.

---

## Fault Isolation

The feed service going down must not take down post uploads. The Explore feed failing must not affect the home feed. Services must fail independently.

At Instagram's scale, something is always broken somewhere. The design must assume component failures are normal and isolate blast radius so a single failure degrades one feature — not the whole product.

---

## Scalability

The system must handle **1M reads/sec and 1,000 writes/sec** today and scale horizontally as the user base grows — without a redesign. No single server, no single database, no single point of contention.

---

## Summary

| NFR | Target |
|---|---|
| Availability | High — prioritised over consistency |
| Consistency | Eventual — stale feeds are acceptable |
| Read-your-own-writes | Required — you must see your own post immediately |
| Feed load latency | < 200ms |
| Upload confirmation | < 2-3 seconds |
| Durability | Uploads must never be lost once confirmed |
| Fault isolation | Service failures must not cascade |
| Scalability | Horizontal scale to handle 1M rps |
