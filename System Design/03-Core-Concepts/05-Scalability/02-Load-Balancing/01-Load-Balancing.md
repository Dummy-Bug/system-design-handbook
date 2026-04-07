# Load Balancing

> [!question] You have three servers now. How does a request know which one to go to?
> That's the load balancer's job — and without it, horizontal scaling is useless.

---

## What it is

A load balancer sits in front of your servers and distributes incoming requests across them. Users never talk to your servers directly — they talk to the load balancer, which forwards the request to a server on their behalf.

```
User → Load Balancer → Server A
                     → Server B
                     → Server C
```

Without a load balancer, users would need to know the IP of each individual server. Adding a new server would mean telling every user about it. That's not scalable. The load balancer is the single entry point — you add and remove servers behind it freely.

---

## What happens to the response

Two models:

**Through the load balancer**
Server sends response back to the load balancer, which forwards it to the user. Simple, but the load balancer handles double the traffic — both request and response.

**Direct Server Return (DSR)**
Request goes through the load balancer, but the response goes directly from the server to the user. The load balancer only handles incoming requests. Used when responses are large (video streaming, file downloads) and you don't want the load balancer to become the bottleneck.

---

## Health checks — how it knows a server is dead

Every few seconds the load balancer pings each server:

*"Are you alive?"*

The server responds with a 200 OK. If a server stops responding — marked unhealthy — traffic stops routing to it — an alert fires.

This is automatic failover in practice. No human needed. A server can die at 3am and within seconds the load balancer stops sending it traffic.

> [!info] Health checks are why automatic failover is possible
> The load balancer detects failure continuously. The moment a server goes unhealthy, it's removed from rotation before the next request arrives.

---

## The load balancer is itself a SPOF

You added a load balancer to eliminate SPOFs in your app servers. But now the load balancer is a single point of failure.

Fix: run two load balancers — one active, one passive — with a **floating IP**.

A floating IP is a virtual IP address that isn't tied to any specific machine. It points to whichever load balancer is currently active. If the active one dies, the floating IP is reassigned to the passive one in seconds. Users never notice — the IP address they're connecting to didn't change.

```
Users → Floating IP → Active Load Balancer  → Servers
                    → Passive Load Balancer (standby)
```

---

## Auto-scaling ties in here

Once you have a load balancer, you can add and remove servers dynamically:

- CPU across servers hits 80% → new server spins up → registers with load balancer → immediately starts receiving traffic
- Traffic drops at 3am → servers spin down → load balancer removes them from rotation

The load balancer is what makes this seamless. New servers just join — the load balancer discovers them and starts routing.

> [!tip] In an interview — always mention the load balancer as a SPOF
> *"The load balancer itself is a single point of failure. I'd run two in active-passive with a floating IP to eliminate it."*
