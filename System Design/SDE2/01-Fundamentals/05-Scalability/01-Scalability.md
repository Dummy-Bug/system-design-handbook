# Scalability

> [!question] Your system works fine with 100 users. What happens when 1 million show up?
> That's scalability — the ability to handle growing load without breaking or requiring a complete redesign.

---

## The two ways to scale

When your server can't handle the load anymore, you have exactly two options:

**Vertical Scaling — make the machine bigger**

Upgrade your existing server. More CPU, more RAM, faster disk. Same machine, more power.

- Simple — no code changes, no architecture changes
- Has a hard ceiling — the biggest server money can buy still has limits
- Single point of failure — one big machine is still one machine
- Expensive — high-end hardware costs disproportionately more

**Horizontal Scaling — add more machines**

Run many average servers in parallel with a load balancer distributing traffic between them.

- No ceiling — add as many servers as you need
- No single point of failure — one dies, the others keep serving
- Cheaper — commodity hardware scales linearly with cost
- Complex — now you have a distributed system with all its problems

> [!info] The industry default is horizontal scaling
> Vertical scaling buys you time. Horizontal scaling is the real answer.

---

## What makes horizontal scaling hard — state

If your servers are **stateless** — no memory between requests — horizontal scaling is trivial. Add more servers, put them behind a load balancer, done. Any server can handle any request.

The problem starts when servers are **stateful** — when they remember things. If user A's session is stored on Server 1 and the next request goes to Server 2 — Server 2 has no idea who they are.

The core challenge of scalability: **move state out of your servers and into dedicated systems** (databases, caches, message queues) so the servers themselves stay stateless and horizontally scalable.

---

## The three bottlenecks you'll hit

As traffic grows, bottlenecks appear in a predictable order:

**1. CPU / App servers**
Too many requests, threads exhausted. Fix: add more app servers horizontally.

**2. Database**
App servers scaled fine, but now they're all hammering one database. The DB becomes the bottleneck. Fix: read replicas, caching, sharding.

**3. Network / Bandwidth**
Data volume grows so large that network throughput becomes the limit. Fix: CDNs, compression, smarter data transfer.

Each bottleneck requires a different solution. Scaling is not one decision — it's a sequence of decisions as each layer hits its limit.

---

## Scaling is not just about traffic volume

Load comes in different shapes:

| Load type | Example | Scaling approach |
|---|---|---|
| More users, read-heavy | Social media, news feed | Read replicas, caching, CDN |
| Write-heavy | Logging, metrics, financial transactions | Sharding, message queues |
| Larger data | File hosting, video streaming | Object storage, CDN |
| Spiky traffic | Ticket sales, product launches | Auto-scaling, pre-warming |

The scaling strategy depends on which type of load you're dealing with. A system handling 1M steady reads scales very differently from one handling 100k sudden writes.

---

## The scalability moment in every interview

After you draw the initial architecture, the interviewer will ask:

*"Now what if this needs to handle 10x the traffic?"*

Walk through it systematically:
1. Which component breaks first?
2. What do you do to it?
3. What breaks next?

> [!tip] Scalability is a sequence of bottleneck → fix → next bottleneck
> Never say "I'd scale the whole system." Always identify the specific bottleneck first.
