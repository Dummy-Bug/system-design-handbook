# Performance Metrics

> [!question] Before you design anything — how do you know if your system is working **well**?
> You measure it. Performance Metrics are the measurements that answer that question.

---

## The Doctor Analogy

When a doctor checks your health, they don't just say *"you look fine"*. They measure:
- Blood pressure
- Heart rate 
- Temperature

Each number tells them something **specific**. A high temperature means infection. Low blood pressure means something else entirely. They can't treat you without knowing which number is off.

Your system works the same way. When something is wrong, you need to know **which metric is failing** before you can fix it.

---

## The Core Vitals of a System

| Metric | The question it answers |
|---|---|
| **Latency** | How long does one request take? |
| **Throughput** | How many requests can we handle per second? |
| **Availability** | How often is the system actually up? |
| **Durability** | Do we ever lose data? |

> [!tip] The mindset shift
> Every architecture decision you make — adding a cache, sharding a database, using a queue — is a direct response to **one of these metrics being bad**.
> 
> Before you propose any solution in an interview, ask yourself: *which metric am I fixing right now?*

---

## Why this matters in interviews

Interviewers will ask you to define requirements. Vague answers fail. Specific metric-based answers pass.

❌ *"The system should be fast"*  
✅ *"P99 latency should be under 100ms"*

❌ *"It should handle a lot of traffic"*  
✅ *"We need to support 50,000 requests per second at peak"*

We'll go through each metric one by one. Each gets its own file.
