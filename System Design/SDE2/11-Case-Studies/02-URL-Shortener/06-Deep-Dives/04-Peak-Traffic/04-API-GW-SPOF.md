
> [!info] The API Gateway itself can be a SPOF
> You added an API Gateway to eliminate single points of failure in the app server fleet. But the Gateway itself is now a single point of failure — if it goes down, 100% of traffic is dead. You need to make the Gateway redundant too.

---

## The problem

```
Without redundancy:
  Client → API Gateway (single instance) → App servers
  
  API Gateway dies → entire system unreachable
  All 1M requests/sec → nowhere to go
```

Every component you add to solve a scaling problem can itself become a SPOF. The API Gateway is no exception.

---

## The fix — multiple Gateway instances behind a cloud load balancer

Run multiple API Gateway instances across availability zones. Put a cloud load balancer (AWS ALB, GCP Cloud Load Balancing) in front of them.

```
Client
→ Cloud Load Balancer (managed, replicated by provider)
→ API Gateway instance 1  (availability zone A)
→ API Gateway instance 2  (availability zone B)
→ API Gateway instance 3  (availability zone C)
→ App Server fleet
```

If one Gateway instance dies, the cloud load balancer stops sending traffic to it within seconds (failed health checks). The remaining instances absorb the load.

---

## Is the cloud load balancer itself a SPOF?

No. Cloud load balancers are managed services — AWS ALB, GCP Cloud LB — replicated across multiple availability zones and data centers by the provider. You do not manage this redundancy yourself. It is a given.

This is a reasonable place to stop the SPOF chain. You cannot eliminate every possible failure — at some point you trust the cloud provider's infrastructure guarantees (which come with SLAs).

```
Cloud LB          → replicated by provider, not your problem
API Gateway fleet → 3+ instances across zones, your responsibility
App Server fleet  → auto-scaled, health-checked
Redis Cluster     → replicated
DB shards         → 3 replicas each
```

Every layer has redundancy. No single machine failure takes down the system.

---

## How many Gateway instances?

Same N+1 reasoning as everywhere else:

```
N instances handle peak load
+1 instance as spare for failover
```

With 3 instances across 3 availability zones, you can lose one entire zone and still serve traffic with 2 remaining instances — each handling 50% more load temporarily while the failed instance is replaced.

---

> [!tip] Interview framing
> "The API Gateway itself is a SPOF unless you run multiple instances. 3 instances across availability zones behind a cloud load balancer. Cloud LB is managed and replicated by the provider — reasonable place to stop the redundancy chain. If one Gateway goes down, health checks route traffic to the remaining instances within seconds."
