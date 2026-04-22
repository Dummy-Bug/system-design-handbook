
> [!info] Knowing your SLI is breached is useless if nobody finds out for an hour
> Alerting is the mechanism that closes the loop — when SLI diverges from SLO, a human gets paged immediately.

---

## The alert rule

An alert is a rule evaluated continuously against your SLI measurements:

```
IF p99_redirect_latency > 50ms
FOR more than 2 minutes
→ page on-call engineer immediately
```

```
IF availability < 99.99%
FOR more than 2 minutes
→ page on-call engineer immediately
```

Simple threshold rules. But the "for more than 2 minutes" part is important.

---

## Why you need a sustained breach window

Without the duration condition, a single spiky second triggers a page. At 1M requests/second, you will have occasional spiky seconds. A viral tweet hits, a GC pause fires on one server, a network hiccup adds 30ms for two seconds — then everything recovers. No real incident.

If you alert on every spike, you wake engineers up at 3am for events that resolved themselves before anyone could respond. This is called **alert fatigue** — engineers start ignoring pages because most of them are false alarms. When the real incident happens, the page gets ignored too.

The 2-minute window filters out transient spikes while still catching real degradation fast enough to act on it.

```
Single spike (30 seconds): alert condition met but not sustained → no page
Sustained breach (3 minutes): condition met for > 2 minutes → page fires
```

You tune the window based on your SLO. A tighter SLO might warrant a 1-minute window. A more relaxed one might use 5 minutes.

---

## The full loop — SLO → SLI → Alert

```
SLO:     p99 redirect latency < 50ms          ← the promise
SLI:     actual p99 measured every 15 seconds  ← the reality
Alert:   fires when SLI > SLO for > 2 minutes  ← the notification
```

Every 15 seconds, Prometheus computes the fleet-wide p99. If it stays below 50ms, nothing happens. If it crosses 50ms and stays there for 2 minutes, the alert fires — PagerDuty (or equivalent) pages the on-call engineer.

The engineer gets woken up with the exact metric that triggered the alert, a link to the latency graph showing the spike, and the current value. They know immediately what broke and roughly when it started.

---

## Prometheus vs managed services

**Prometheus (self-hosted):**
- Open source, runs on your own infrastructure
- You manage storage, scaling, alerting rules configuration
- Pairs with Grafana for dashboards and Alertmanager for routing pages
- More control, more operational overhead

**Datadog / New Relic / Grafana Cloud (managed):**
- You send metrics to their service, they handle everything else
- No ops burden — no Prometheus servers to manage, no storage to provision
- Costs money per metric per month at scale
- Faster to set up, less to maintain

For a URL shortener at 100M MAU, either is fine. In a system design interview, name one and justify the choice — don't just list both without committing.

---

> [!tip] Interview framing
> "Alerting rule: if p99 exceeds 50ms for more than 2 minutes, page on-call. The sustained window prevents alert fatigue from transient spikes — a 30-second spike that self-resolves shouldn't wake someone at 3am, but a 3-minute breach definitely should. For the metrics stack: Prometheus if self-hosted with more control, Datadog if we want managed with no ops overhead. Full loop: SLO is the promise, SLI is what we measure every 15 seconds, alert fires when the two diverge."
