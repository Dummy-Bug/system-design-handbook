# Performance Metrics & Key Terms

---

## Latency

The time it takes to handle a single request — from the moment 
it arrives to the moment the response is sent back. 
Measured in milliseconds.

**Example:** 
User clicks "Place Order" on Zomato. Your server receives the 
request, validates it, writes to DB, and sends back a response. 
Total time taken = latency of that request.

---

### P50, P95, P99 — critical concept

Average latency is useless in production. Here is why:

Imagine 100 requests come in:
- 99 complete in 10ms
- 1 takes 10,000ms (10 seconds)

Average = ~110ms. Looks perfectly fine on a dashboard.
But 1 real user just waited 10 seconds and probably never 
ordered again.

This is why we use percentiles:
- **P50** — 50% of requests complete within this time. 
  The median experience.
- **P95** — 95% of requests complete within this time.
- **P99** — 99% of requests complete within this time.
- **P99.9** — 99.9% of requests complete within this time. 
  Called "tail latency".

At Google/Razorpay scale, P99 is what gets monitored and 
alerted on. If P99 spikes, thousands of real users are having 
a bad experience right now.

**Example:**
Razorpay's payment confirmation API has a P99 of 300ms.
That means 99 out of every 100 payment confirmations complete 
within 300ms. The 1 that does not is a real user staring at 
a loading spinner on a payment screen — worst possible moment.

---

### Tail latency amplification

If one request internally calls 10 microservices, and each 
service has a 1% chance of being slow — the probability that 
at least one of them is slow is much higher than 1%.

**Example:**
Zomato's order placement calls:
- Auth service
- Restaurant service
- Inventory service
- Pricing service
- Notification service

If each has 1% chance of being slow, your overall order API 
will be slow far more than 1% of the time. Slow tail latencies 
compound across every service call in the chain.

This is why microservices need aggressive timeouts — if one 
downstream service is slow, you cannot let it drag down 
your entire request.

---

## Throughput

How many requests your system can handle per unit of time.
Measured in RPS (requests per second) or TPS (transactions 
per second).

**Examples:**
- Razorpay processing 50,000 payment transactions per second 
  during a big sale — high TPS requirement.
- Hotstar serving 10 million concurrent streams during IPL — 
  measured in GB/sec of data transferred.
- Zomato handling 100,000 order requests per second during 
  lunch peak — high RPS requirement.

---

## Latency vs Throughput — they are not the same

- **Latency** = how fast is ONE request handled
- **Throughput** = how MANY requests can be handled simultaneously

Think of a highway:
- A single lane road can be very fast with no traffic (low latency) 
  but only one car passes at a time (low throughput).
- A 10 lane highway moves thousands of cars simultaneously 
  (high throughput) but during rush hour every car slows down 
  (high latency).

**Real world example:**
Your Zomato order API responds in 50ms on average (great latency) 
but can only handle 100 req/sec before falling over (low throughput).

During lunch peak, 10,000 req/sec come in. Your latency 
shoots up to 5 seconds because requests are queuing up waiting 
for their turn. You have a throughput problem, not a latency problem.

Solution = horizontal scaling, add more servers.
Not = optimising your code to respond in 40ms instead of 50ms.

**In interviews when someone says "the system is slow" — 
immediately ask: is it a latency problem or a throughput problem? 
They have completely different solutions.**

---

## Bandwidth

The maximum amount of data that can be transferred per unit 
of time. Measured in Mbps or Gbps.

- Bandwidth is the physical ceiling.
- Throughput is what you actually achieve within that ceiling.
- Think of bandwidth as the diameter of a pipe. 
  Throughput is how much water actually flows through it.

### Who decides your bandwidth?

Multiple levels — each one is a potential ceiling:

**1. Network Interface Card (NIC)**
Every server has a physical NIC. A typical cloud VM gets 
1Gbps, 10Gbps, or 25Gbps depending on instance type.
This is the absolute hardware ceiling for that machine.

**2. Cloud Provider**
AWS, GCP, Azure allocate bandwidth per VM instance.
Small EC2 instance = 1Gbps. Large compute-optimized = 25Gbps.
You pay more for more bandwidth.

**3. Datacenter Uplink**
Even if your server has a 10Gbps NIC, if the datacenter's 
connection to the internet is 1Gbps — that is the real ceiling.
All servers in that datacenter share that uplink.

**4. Network Path**
If your server is in Mumbai and the user is in New York — 
the intercontinental cable bandwidth is shared by everyone.
This is why data should be served as close to the user 
as possible.

### When does bandwidth actually matter?

Your actual throughput is always limited by the weakest link:
```
Actual throughput = min(
    what your CPU can handle,
    what your DB can handle,
    what your bandwidth allows,
    what your memory allows
)
```

**Example 1 — bandwidth is NOT the bottleneck:**
Zomato order API returns a small JSON — order id, status, ETA. 
Maybe 2KB per response.
```
500 req/sec × 2KB = 1,000 KB/sec
                  = 1 MB/sec
                  = 0.008 Gbps
```
Nowhere near the 1Gbps NIC limit.
Your bottleneck is CPU or DB — fix that, not bandwidth.

**Example 2 — bandwidth IS the bottleneck:**
Order history API returns last 1000 orders with full details.
Maybe 2MB per response.
```
500 req/sec × 2MB = 1,000 MB/sec
                  = 1 GB/sec
                  = 8 Gbps
```
Already needs 8Gbps but NIC only provides 1Gbps.
Already in trouble at just 500 req/sec.

The fix here is not adding servers or optimising code.
The fix is reducing payload size:
- Paginate — return 20 orders instead of 1000
- Cache responses aggressively
- Compress the payload

**Example 3 — video streaming:**
Hotstar streaming IPL final to 50 million users at 4Mbps each:
```
50,000,000 × 4 Mbps = 200,000,000 Mbps
                    = 200,000 Gbps
                    = 200 Tbps
```
Pure bandwidth problem. Optimising code does nothing here.

---

## SLA, SLO, SLI

**SLI (Service Level Indicator)**
The actual measured metric. What you observe in production.
Example: "Our P99 latency right now is 180ms."
Example: "Our availability this month is 99.95%."

**SLO (Service Level Objective)**
The internal target you set for yourself.
Example: "Our P99 latency should stay below 200ms."
Example: "We target 99.99% availability internally."

**SLA (Service Level Agreement)**
The contractual promise made to customers.
Has financial penalties if breached.
Example: "We guarantee 99.9% uptime. 
If we breach it, you get service credits."

SLI is what you measure.
SLO is what you aim for internally.
SLA is what you promise externally.

**Critical rule:**
SLO must always be stricter than SLA.
If your SLA promises 99.9% uptime, your internal SLO should 
target 99.95% — so your alerts fire and your team reacts 
before you actually breach the customer contract.

The buffer between SLO and SLA is your reaction time window.

**Real world example:**
AWS S3 SLA guarantees 99.9% availability.
Internally AWS targets much higher — their SLO is likely 
99.99% or above.
This buffer is their safety margin.

---

## The Key Insight

All these metrics pull in different directions:

- Maximising throughput can hurt P99 latency — 
  system gets busy, tail requests slow down.
- Reducing latency aggressively can reduce throughput — 
  timeouts cut off slow requests but also drop valid ones.
- Serving large payloads increases throughput in bytes 
  but can hit bandwidth limits.

These tradeoffs are what every HLD interview is actually testing.
When an interviewer asks "how would you scale this?" — they want 
to see if you understand which metric is the bottleneck 
and what the tradeoff of your solution is.

---

## Practice Questions

---

**Q1.**
Hotstar is streaming the IPL final. 50 million users are watching 
simultaneously. Each stream is 4Mbps.

The engineering team is debating:
- Engineer A: "our servers are slow, we need to optimise our code"
- Engineer B: "we need more servers"

Who is right and why? What is the actual bottleneck?

**Answer:**
Both engineers are wrong. The bottleneck is bandwidth, not compute.
```
50,000,000 × 4 Mbps = 200,000,000 Mbps
                    = 200,000 Gbps
                    = 200 Tbps
```
200 Tbps of bandwidth is needed simultaneously.
Optimising code to respond in 40ms instead of 50ms does nothing 
— the bottleneck is not compute speed, it is data transfer volume.
Adding more servers helps with compute but each server still needs 
to push 4Mbps per stream — the total bandwidth requirement 
does not change.
The only real solution is distributing data geographically 
so no single point needs to push 200 Tbps.

---

**Q2.**
Your Razorpay payment API has:
- Average latency: 50ms
- P99 latency: 4000ms (4 seconds)

Your manager says "average looks fine, nothing to worry about."

Why is your manager wrong? At 1 million transactions per day, 
how many users are experiencing 4 second latency?
Why is this especially bad on a payment screen?

**Answer:**
Average latency hides the tail. The calculation:
```
P99 means 1% of requests are slow.
1% of 1,000,000 = 1,000,000 × (1/100)
                = 1,000,000 / 100
                = 10,000 users per day
```
10,000 users every single day are waiting 4 seconds for 
payment confirmation.

This is especially bad on a payment screen because during 
those 4 seconds the user has no idea:
- Did my money get debited?
- Did the payment go through?
- Should I click again or will I get charged twice?

That uncertainty causes users to either retry (potential 
double charge) or abandon (money possibly already debited).
A slow news feed is annoying. A slow payment confirmation 
causes real financial anxiety.

---

**Q3.**
Your company has three services:

Payment service:
- SLA promised to customers: 99.9% uptime
- Current measured SLI: 99.91% uptime

Order service:
- SLA promised to customers: 99.5% uptime
- Current measured SLI: 99.4% uptime

Notification service:
- SLA promised to customers: 99% uptime
- Current measured SLI: 99.2% uptime

Which service is in immediate trouble?
Which service looks fine but is actually risky?
What should the internal SLO be for the payment service?

**Answer:**
**Order service is in immediate trouble.**
SLI (99.4%) is already below SLA (99.5%).
Customer contract is already breached. 
Financial penalties are happening right now.

**Payment service looks fine but is actually risky.**
SLI (99.91%) is above SLA (99.9%) — technically no breach.
But the buffer is only 0.01%. One bad deployment and 
they breach the SLA. Alerts should be firing.

**Notification service is the healthiest.**
SLI (99.2%) is comfortably above SLA (99%) with 0.2% buffer.

**Payment service SLO should be 99.95%:**
```
SLA = 99.9%  (promised to customers)
SLO = 99.95% (internal target, stricter than SLA)

Buffer = 0.05%
```
Internal alerts fire at 99.95%, giving the team time 
to react before actually breaching the 99.9% customer promise.
The buffer between SLO and SLA is the reaction time window.