## Problem Context

Ride tracking requires **real-time location updates** between:
- Rider ↔ Server ↔ Driver

Both rider and driver:
- Continuously send their live GPS location
- Continuously receive the other party’s updates
- Expect low latency (sub-second to a few seconds)

This makes the problem **event-driven, real-time, and bidirectional** 

---

## Why Normal HTTP APIs Are Not Suitable

- HTTP follows request–response semantics
- Server cannot push updates arbitrarily
- Each update requires a new request with headers and auth
- Inefficient for high-frequency updates (location every few seconds)

**Conclusion:** 
HTTP is good for transactional operations (ride creation, payment) 
❌ Not suitable for continuous real-time updates

---

## Why Polling / Short Polling Is Not Suitable

### How it works
- Client periodically asks the server: “Any update?”
- Happens every 1–2 seconds

### Problems
- Massive number of unnecessary requests
- High CPU and network overhead
- Poor battery usage on mobile
- Updates are delayed until next poll

**Conclusion:**  
❌ Does not scale and wastes resources

---

## Why Long Polling Is Still Not Ideal

### How it works
- Client sends request
- Server holds it until an update occurs
- Client reconnects after response

### Problems
- Connection churn (close → reopen)
- Fragile on mobile networks
- Still inefficient at very large scale
- Mostly unidirectional in practice

**Conclusion:** 
⚠ Better than polling, still not ideal for continuous streaming

---

## Why Server-Sent Events (SSE) Falls Short

### What SSE Provides
- Persistent connection
- Server → client push

### Critical Limitation
- **Unidirectional only**
- Client cannot stream data back to server

### Why This Is a Problem Here
In ride tracking:
- Driver must continuously send location updates
- Rider must continuously send location updates

With SSE:
- You would need SSE for downstream updates
- PLUS separate HTTP calls for upstream location updates

This results in:
- Two communication channels
- Higher complexity
- Higher latency
- More overhead

**Conclusion:** 
⚠ SSE is fine for notifications 
❌ Not suitable for bidirectional real-time systems

---

## Why WebSockets Are the Right Choice

### What WebSockets Provide
- Persistent connection
- **Full-duplex communication**
- Low per-message overhead
- Server push + client streaming on same channel

### Why This Fits Ride Tracking Perfectly
- Driver → server → rider (driver GPS updates)
- Rider → server → driver (rider GPS updates)
- Status updates (accepted, arrived, started, completed)
- Optional chat support

All of this happens over a **single, long-lived connection**.

---

## Final Decision Summary

| Approach        | Real-Time | Duplex | Efficient | Suitable |
|----------------|----------|--------|-----------|----------|
| HTTP APIs      | ❌       | ❌     | ❌        | ❌       |
| Polling        | ❌       | ❌     | ❌        | ❌       |
| Long Polling   | ⚠        | ❌     | ⚠         | ❌       |
| SSE            | ✅       | ❌     | ⚠         | ❌       |
| WebSockets     | ✅       | ✅     | ✅        | ✅       |

---

> WebSockets are used because ride tracking requires low-latency, full-duplex communication where both rider and driver continuously send and receive location updates. HTTP and polling are inefficient, and SSE is unidirectional, making WebSockets the best fit.


```Json

Rider  ---> Load Balancer <---> Web Socket
```

```Json

Driver ---> Load Balancer <---> Web Socket
```
