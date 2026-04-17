
## API Gateway Down

The API Gateway sits in front of the rate limiter. If it goes down, requests never reach the rate limiter at all.

---

## Impact

```
User → API Gateway (down) → ✗
```

Users see connection errors or timeouts. The rate limiter, Redis, Rule DB — all completely unaffected and healthy. But no traffic reaches them because the entry point is gone.

This is a **full user-facing outage** but it is outside the rate limiter's scope to solve. The API Gateway is its own system with its own redundancy requirements.

---

## API Gateway Redundancy (Not Rate Limiter's Problem)

In a production system, the API Gateway is never a single instance. It runs as multiple instances behind a load balancer or as a managed cloud service (AWS API Gateway, Kong, Nginx cluster):

```
Internet → Load Balancer → API Gateway Instance 1
                         → API Gateway Instance 2
                         → API Gateway Instance 3
```

One instance going down routes to others. The LB health checks detect failure within seconds.

The rate limiter does not need to handle API Gateway failures — that is the API Gateway's own fault isolation responsibility.

---

## Summary

```
Impact on rate limiter : none — rate limiter never receives traffic
Impact on users        : full outage — connection errors
Responsibility         : API Gateway team, not rate limiter
Solution               : multiple API Gateway instances behind LB
                         managed cloud API GW (inherently redundant)
```
