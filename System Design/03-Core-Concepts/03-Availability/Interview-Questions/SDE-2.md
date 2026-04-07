# Availability — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around failover, multi-region deployments, SPOF elimination, and the subtle gap between availability and reliability. Expected at SDE-2 level — not just definitions, but understanding when and why decisions matter.

---

> [!question] Your service runs across two data centres — primary and replica. The primary goes down. Your replica promotes to primary. You measured 30 seconds of downtime during this failover. What caused those 30 seconds, and how would you reduce it?

> [!success]- Answer
>
> **What caused the 30 seconds:**
>
> Failover downtime comes from three stages — each adds latency:
> ```
> 1. Detection lag    → health checks run every N seconds
>                       if check interval = 10s, you may detect failure after 10s
>
> 2. Replication lag  → if replica was async, it may be behind primary
>                       data written to primary but not yet replicated = lost or stale
>
> 3. Leader election  → Sentinel / Patroni / Zookeeper must agree on new primary
>                       quorum takes time, especially under network stress
> ```
>
> **How to reduce it:**
>
> **Reduce detection lag:**
> ```
> Health check interval: 30s → 5s
> Multiple checks before declaring dead (avoid false positives)
> ```
>
> **Reduce replication lag:**
> ```
> Async replication → replica may be seconds behind primary
>                     switch to sync replication for critical data
>
> Sync replication  → primary waits for replica to acknowledge write
>                     0 replication lag, but higher write latency
> ```
>
> **Multi-master as an alternative:**
> Instead of one primary and one replica, both nodes accept writes simultaneously. No failover needed — if one goes down, the other already has all writes.
>
> But multi-master introduces **split-brain**:
> ```
> Network partition: Node A and Node B both think they're primary
> Both accept conflicting writes
> Partition heals → conflict resolution required
> Last-write-wins? Merge? → business-specific, often lossy
> ```
>
> **The severity of 30 seconds depends entirely on the system:**
> - Payment checkout: 30 seconds = significant revenue loss
> - Internal analytics dashboard: 30 seconds = acceptable
>
> > [!important] Async replication is fast but loses data on failover. Sync replication eliminates data loss but increases write latency. Multi-master eliminates failover but introduces split-brain. There is no free option.
>
> > [!tip] Interview framing
> > *"30 seconds comes from detection lag, replication lag, and leader election. To reduce: tighter health checks, sync replication to eliminate data loss, and pre-warming the replica to handle traffic. Multi-master removes failover entirely but introduces split-brain — conflict resolution becomes a hard business problem."*

---

> [!question] Your service is deployed in a single region. You're expanding to multiple regions. Walk me through the availability and consistency trade-offs your users will experience.

> [!success]- Answer
>
> **Availability improvement:**
> ```
> Single region → region goes down → everyone affected
> Multi-region  → region goes down → users route to nearest healthy region
>                 availability improves significantly at the cost of complexity
> ```
>
> **What users may experience negatively:**
>
> **Higher latency for cross-region writes:**
> ```
> User in EU writes data
> → write must replicate to US region
> → speed of light: ~70ms EU → US
> → write acknowledgment delayed if using sync replication
> ```
>
> **Consistency violations:**
> Multi-region usually means eventual consistency. Specific guarantees that may break:
>
> ```
> Causal consistency     → "you liked a post, then commented"
>                          in another region, comment may appear before like
>
> Monotonic read         → user refreshes page, may see older state from different region
>
> Read-your-own-writes   → user posts a photo, immediately sees their profile
>                          photo may not yet have replicated → user sees stale profile
> ```
>
> **Read-your-own-writes is the most visible user-facing violation:**
> ```
> User updates username → write goes to EU
> User reloads page    → request routes to US
> US replica not yet synced → user sees old username
> → user thinks the change failed and does it again
> ```
>
> **Mitigation strategies:**
> ```
> Sticky sessions       → route same user to same region consistently
> Session tokens        → carry write version in token, region checks before serving
> Read-your-write SLO   → guarantee user sees their own writes within N seconds
> ```
>
> > [!important] Multi-region improves availability but weakens consistency guarantees. Read-your-own-writes violations are the most visible to end users and must be explicitly designed for.
>
> > [!tip] Interview framing
> > *"Multi-region improves availability but breaks consistency guarantees — causal, monotonic reads, and read-your-own-writes may all fail. Read-your-own-writes is the most user-visible: user updates something and immediately sees the old value. Mitigate with sticky sessions or version tokens so writes and reads hit the same replica until sync completes."*

---

> [!question] You're tasked with getting your service from 99.9% to 99.99% availability. Walk me through how you systematically find and eliminate SPOFs.

> [!success]- Answer
>
> **The approach — work layer by layer from the outside in:**
>
> ```
> DNS / CDN → Load Balancers → App Servers → Cache → Database → Network
> ```
>
> **Layer 1 — App servers:**
> ```
> Single app server → add horizontal scaling
> Multiple app servers behind a load balancer
> → any one server going down = no impact
> → auto-scaling handles traffic spikes
> ```
>
> **Layer 2 — Cache:**
> ```
> Single cache node → add Redis Sentinel or Redis Cluster
> Sentinel: automatic failover for primary cache
> Cluster: sharded + replicated, no single cache node is a SPOF
> ```
>
> **Layer 3 — Database:**
> ```
> Single DB → replicas + automatic failover (Patroni, RDS Multi-AZ)
> Primary goes down → replica promotes automatically
> → manual intervention eliminated
> ```
>
> **Layer 4 — Load Balancer (most commonly missed):**
> ```
> Multiple app servers behind ONE load balancer
> → the load balancer itself is now the SPOF
>
> Fix: multiple LBs + DNS failover
>      cloud providers offer managed LBs with built-in HA (AWS ALB, GCP LB)
> ```
>
> **Layer 5 — Data centre / Availability Zone:**
> ```
> All of the above in one AZ → AZ goes down → everything goes down
> Fix: deploy across multiple AZs
>      most cloud providers have 3 AZs per region
> ```
>
> **99.99% means 4.3 minutes of downtime per month:**
> No human can detect, respond, and fix an incident in 4.3 minutes. Every failover at every layer must be fully automated.
>
> ```
> 99.9%  → manual on-call response works
> 99.99% → automated detection + automated failover required at every layer
> ```
>
> > [!important] The load balancer is the most commonly missed SPOF in interviews. Candidates add multiple app servers but forget the single LB in front of them is still a SPOF.
>
> > [!tip] Interview framing
> > *"Systematically eliminate SPOFs layer by layer: app servers → cache → DB → load balancer → AZ. The most commonly missed one is the load balancer — multiple app servers behind a single LB still has a SPOF. At 99.99%, every failover must be automated — 4.3 minutes/month doesn't give humans time to respond."*

---

> [!question] Your monitoring shows 99.9% availability. But users are complaining the service "feels broken". How is this possible and what do you investigate?

> [!success]- Answer
>
> **Availability and reliability are separate signals:**
> ```
> Availability = % of requests that got a response
> Reliability  = % of responses that were correct
>
> A service returning 200 OK with wrong data is available but unreliable
> ```
>
> **What to investigate:**
>
> **1. Latency — check P99, not averages:**
> ```
> Average latency:  120ms  → looks fine
> P99 latency:      2,400ms → 1 in 100 users waits 2.4 seconds
>
> Those users feel the service is broken even though it's "up"
> ```
>
> **2. Semantic errors — logic bugs that return 200 but wrong data:**
> ```
> Product price showing $0     → 200 OK, availability check passes, user experience broken
> Search returning wrong order → 200 OK, looks healthy in monitoring
> Cart totals calculated wrong → 200 OK, users losing money
>
> These are the only purely "reliability" failures — semantic correctness errors
> Availability monitoring cannot detect them
> ```
>
> **3. Consistency violations:**
> ```
> Causal consistency broken    → user's actions arrive out of order
> Read-your-own-writes broken  → user edits profile, refreshes, sees old data
> Monotonic reads broken       → user sees data "go backwards" on refresh
>
> All return 200, all look "available", all feel broken
> ```
>
> **How to detect semantic and consistency errors:**
> ```
> Synthetic transactions  → run known inputs through the system, verify expected outputs
> Business metrics        → revenue per hour, conversion rate — drops signal real problems
> User-facing error rate  → track 4xx from user perspective, not just 5xx from infra
> ```
>
> > [!important] Semantic errors are the hardest failure mode — the system is available and healthy in every infrastructure metric, but returning wrong answers. You can only detect them by knowing what the correct answer should be.
>
> > [!tip] Interview framing
> > *"Availability only measures 'did it respond' — not 'did it respond correctly'. Investigate P99 latency (averages hide tail pain), semantic errors (200 OK with wrong data — only detectable with synthetic transactions), and consistency violations (read-your-own-writes, monotonic reads). Business metrics like conversion rate will drop before infrastructure metrics flag anything."*

---

> [!question] You're consulting for a startup. Their CTO says "we have 100 users, we don't need high availability." How do you respond?

> [!success]- Answer
>
> **The CTO is half right — and that half matters:**
>
> At 100 users, 99.999% availability (26 seconds/month) is almost certainly not justified. The engineering cost is enormous — multi-region, fully automated failover, self-healing infrastructure. For 100 users, the cost of building this is wildly disproportionate.
>
> **But "we don't need any availability thinking" is wrong:**
>
> The right question isn't "how many users" — it's **"what does one hour of downtime cost?"**
>
> ```
> SaaS B2B tool used during work hours:
> 100 users × $200/month = $20k MRR
> 1 hour downtime → enterprise clients call immediately
> → trust damage disproportionate to scale
> → may violate contractual SLA with a paying customer
>
> Consumer app with 100 users:
> Casual users, no SLA commitments
> → 1 hour downtime = inconvenience, not catastrophe
> ```
>
> **The practical response:**
> ```
> Don't build for 99.999% with 100 users — that's over-engineering
>
> Do:
> → deploy across 2 AZs (cheap, eliminates most AZ-level failures)
> → use managed DB with automatic failover (RDS Multi-AZ, PlanetScale)
> → define basic on-call so someone is notified when it goes down
> → set a realistic SLO for internal use only (no contractual SLA yet)
> ```
>
> **Availability is not binary — the question is "how much?"**
> The answer scales with the cost of failure, not the number of users.
>
> As the startup grows, the HA investment grows with it. Don't over-engineer now, but don't skip the basics either — managed services give you most of the benefit for nearly none of the cost.
>
> > [!important] Availability decisions are driven by cost of failure, not user count. An enterprise B2B product with 10 paying customers at $50k/year each needs much higher availability than a consumer app with 10,000 casual users.
>
> > [!tip] Interview framing
> > *"100 users doesn't mean skip availability — it means calibrate the investment. The question is: what does one hour of downtime cost? B2B with SLAs? Needs at least multi-AZ and managed failover. Consumer app with casual users? You have more slack. Managed cloud services give you most of HA for free — there's no reason to skip the basics regardless of scale."*
