# Load Balancing Algorithms

> [!question] You have multiple servers. Which one gets the next request?
> The algorithm determines that — and the wrong choice creates hotspots even with perfectly healthy servers.

---

## Round Robin

Send to Server A, then B, then C, then A again. Simple rotation.

```
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A
```

**Works well when:** all requests are roughly equal in cost — same processing time, same resource usage.

**Breaks when:** requests have very different costs. A request that takes 10 seconds and a request that takes 1ms both count as "one request" to round robin. Server A could be drowning under 10 heavy requests while Server B is idle after finishing 10 fast ones — but round robin keeps sending to both equally.

---

## Weighted Round Robin

Same as round robin, but servers get traffic proportional to their capacity.

```
Server A — 16 cores → gets 2x traffic
Server B — 8 cores  → gets 1x traffic
```

**Works well when:** your servers aren't identical — some are more powerful than others. Useful during scaling events when a new, larger server is added mid-deployment.

**Breaks when:** request cost varies wildly. Same problem as round robin — weight is based on capacity, not on how busy the server actually is right now.

---

## Least Connections

Always send the next request to whichever server has the fewest active connections right now.

```
Server A — 10 active connections
Server B — 2 active connections  ← next request goes here
Server C — 7 active connections
```

**Works well when:** requests have uneven processing times. Slow requests pile up on one server — least connections notices the pile-up and routes around it automatically.

**Breaks when:** connection count is a bad proxy for load. A server could have 2 connections but both are doing heavy video transcoding. Another has 20 connections but all are trivial 1ms reads. Least connections would incorrectly prefer the transcoding server.

> [!info] Least connections is the default choice for most production systems
> It handles uneven workloads naturally without any configuration.

---

## IP Hashing

Hash the user's IP address → always route that user to the same server.

```
User IP 192.168.1.1 → hash → always Server A
User IP 192.168.1.2 → hash → always Server B
```

**Works well when:** you have session state stored on your servers (sticky sessions). The user always lands on the server that holds their session data.

**Breaks when:** that server dies — all users hashed to it lose their session. Also breaks with uneven traffic distribution — if many users share the same IP (corporate NAT, university network), they all hash to the same server, creating a hotspot.

> [!warning] IP hashing is a band-aid, not a real solution
> The real fix is making your servers stateless — move sessions to Redis or a database. Then any server can handle any request and you don't need sticky routing at all.

---

## Comparison

| Algorithm | Best for | Breaks when |
|---|---|---|
| Round Robin | Uniform requests, identical servers | Requests have very different costs |
| Weighted Round Robin | Mixed server capacities | Request cost varies wildly |
| Least Connections | Uneven request processing times | Connection count doesn't reflect true load |
| IP Hashing | Stateful servers (sticky sessions) | Server dies, uneven IP distribution |

---

## What most real systems use

Stateless app servers → **Least Connections**
Stateful legacy servers that can't be refactored → **IP Hashing** (short term fix)
Mixed server sizes → **Weighted Round Robin**

> [!tip] In an interview
> *"I'd use least connections — requests to this system vary in processing time, so round robin would create hotspots. Servers with slow requests would pile up while others sit idle."*
