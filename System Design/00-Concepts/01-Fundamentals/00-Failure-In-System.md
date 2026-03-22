# Failure Modes in Distributed Systems

A distributed system is not one program. It's dozens of programs, 
running on dozens of machines, talking over a network.
Any of those pieces can fail, at any time, independently.

---

## Part 1 — Root Causes (What caused the failure?)

### 1. Hardware Failures
Physical machines are unreliable. Not "if" — "when".

**Disk failures**
- Every disk has an MTTF (Mean Time To Failure) — typically 3-5 years.
- Sounds fine for one disk. Google runs millions of disks.
- At that scale, multiple disks die every single day. 
  It's a daily reality, not an edge case.

**Network failures**
- The wire between two machines can go down.
- A switch, router, or entire datacenter uplink can fail.
- Most dangerous scenario: two machines can't talk to each other,
  but BOTH are still running and BOTH think they are the source of truth.
  (This is called a network partition — covered later.)

**Power failures**
- Entire racks lose power.
- Datacenters have backup generators — but even generators fail.
- AWS had a real outage because a generator TEST went wrong.

**Memory corruption**
- RAM can silently flip bits. Cosmic rays actually cause this at scale.
- A value stored as 100 gets read back as 132.
- No crash, no error log — just silently wrong data.

---

### 2. Software Failures
Hardware fails loudly — machine goes down, you know it.
Software fails quietly — which makes it far more dangerous.

**Bugs**
- Off-by-one error in a payment service → same transaction processed twice.
- Missing null check → one service crashes → three others go down.
- Code behaves differently under production load than in local testing.

**Memory leaks**
- Service slowly eats more RAM over days.
- Looks fine Monday. Crashes Thursday.
- Extremely common in long-running backend services.

**Cascading failures** ← most important one
- Service A calls Service B.
- Service B is slow (not dead, just slow).
- Service A's threads all pile up waiting for B.
- Service A stops responding entirely.
- Service C depends on A — now C is also down.
- One slow service took down the whole system.
- This is how most major real-world outages actually happen.

**Bad deployments**
- New code pushed to 10% of servers.
- Bug only appears with certain data patterns.
- 10% of requests silently fail.
- Hard to catch, especially at 3am.

---

### 3. Human Failures
\#1 cause of production outages. Not hardware. Not software. Humans.

**Accidental deletion**
- Migration script runs on prod instead of staging.
- DELETE FROM users WHERE ... with a slightly wrong WHERE clause.
- Data is gone.

**Misconfiguration**
- Engineer changes a config value (timeout, pool size, feature flag).
- Doesn't test it properly. Deploys.
- System behaves unexpectedly in ways nobody predicted.
- Dangerous because the bug only surfaces under specific 
  traffic conditions — not immediately.

**The Friday deploy**
- Engineer pushes at 5pm Friday. Looks fine. Leaves.
- Problem surfaces at midnight.
- On-call engineer debugs all weekend.

**Capacity mistakes**
- Team doesn't anticipate a traffic spike (sale, viral moment, IPO).
- No autoscaling configured.
- Servers fall over under load.

---

## Part 2 — Failure Behaviour (How does it manifest?)

> Note: Part 1 and Part 2 are two different lenses on the same thing.
> Part 1 = what caused it. Part 2 = what you observe from outside.
> A hardware disk failure can manifest as a crash.
> A network issue can manifest as omission.
> Memory corruption can manifest as byzantine.

**Crash failure**
- Node stops working completely.
- Simplest to handle — other nodes detect it via heartbeat timeout.
- Example: server runs out of memory and the process dies.

**Omission failure**
- Node is running but stops sending or receiving some messages.
- Hard to detect — is it dead or just slow?
- Example: a service is alive but its outbound queue is full, 
  so it silently drops responses.

**Byzantine failure**
- Node is running, responding, but sending WRONG or MALICIOUS data.
- Hardest failure type — node looks perfectly healthy from outside.
- Example: memory corruption causes a node to return wrong values
  while passing all health checks.
- Most everyday systems only handle crash and omission failures.
- Byzantine tolerance is reserved for systems where wrong data 
  is catastrophic — payments, blockchain, financial systems.
  The only way to handle it is having multiple nodes 
  cross-verify each other's responses.

---

## Practice Questions

---

**Q1.**
Your order service calls the restaurant service to confirm an order.
The restaurant service is running fine but responding in 10 seconds 
instead of the usual 100ms due to a DB slowdown.
Within 2 minutes your entire order service is down even though 
the restaurant service never crashed.
What failure type is this and why did the order service go down?

**Answer:**
This is a cascading failure (software failure).
The restaurant service was slow, not dead.
The order service had a fixed thread pool — each thread blocked 
waiting 10 seconds for a response.
New requests kept arriving, all needing a thread, but no threads 
were free. Eventually all threads were exhausted and the order 
service stopped responding entirely — even for unrelated requests.
One slow dependency took down the whole service.

---

**Q2.**
AWS has 10 million disks running across all datacenters.
A typical disk fails once every 4 years.
Roughly how many disks fail per day?
What does this tell you about how AWS architecturally thinks 
about disk failure?

**Answer:**
10,000,000 / (4 × 365) = ~6,850 disks per day.
This means disk failure is not an edge case — it is a daily 
operational routine.
AWS cannot react to disk failures, it has to design for them upfront.
Data is always replicated across multiple disks, multiple machines, 
and multiple datacenters.
When a disk dies, a replica takes over automatically.
This is why S3 replicates data across at least 3 availability 
zones by default.

---

**Q3.**
You push a config change that reduces the DB connection pool 
size from 100 to 10 on a Friday evening.
Everything looks fine for 20 minutes. Then the service starts 
throwing errors.
What failure category is this?
Why did it take 20 minutes to surface instead of being instant?

**Answer:**
This is a human failure — misconfiguration.
The software had no bug. The code worked exactly as designed.
An engineer made a wrong decision during configuration.
It took 20 minutes because at 5pm traffic was low — 10 connections 
were enough to handle it.
As traffic increased or background jobs kicked in, demand for 
connections exceeded 10, requests started queuing, and the 
service fell over.
Bad configs can silently lurk and only surface under specific 
traffic conditions.

---

**Q4.**
A node in your cluster is responding to all health checks perfectly.
Heartbeat is normal, it looks alive.
But it is returning wrong data to 30% of requests due to 
memory corruption.
Which failure type is this?
Why is it harder to handle than a node that simply crashes?

**Answer:**
This is a byzantine failure.
A crashed node is easy — heartbeat stops, you mark it dead, 
route traffic away.
A byzantine node passes all health checks, looks alive, but is 
poisoning your data.
Your monitoring sees nothing wrong.
Other nodes receive corrupted responses and may act on them.
The only way to handle it is cross-verification — multiple nodes 
must agree on the same answer before trusting it.
This is expensive, which is why most systems don't bother and 
only handle crash and omission failures.

---

**Q5.**
Your service has 3 replicas.
Replica A and Replica B can talk to each other.
Replica C cannot talk to A or B due to a network switch failure 
but C is still running and still receiving user traffic.
What failure type caused this?
What is the dangerous situation you are now in?

**Answer:**
This is a hardware failure — network failure causing a 
network partition.
The dangerous situation is split brain.
C is live, receiving writes, and thinks it is the source of truth.
A and B are also receiving writes and think they are the 
source of truth.
When the partition heals, you have two conflicting versions 
of data with no clear way to know which one is correct.
This is the core problem behind the CAP theorem — covered later.

---

**Q6.**
A junior engineer says:
"We don't need to worry about byzantine failures, 
we are not a blockchain company."
Is he right or wrong and why?

**Answer:**
Wrong.
Byzantine failures are not exclusive to blockchain.
They can emerge from software bugs that cause a service to return 
wrong data to some requests while appearing healthy.
They can emerge from memory corruption in any production system.
They can emerge from a malicious actor who has compromised a node.
Any system where wrong data is worse than no data needs to 
think about this — payments and financial systems being the 
most obvious examples outside blockchain.