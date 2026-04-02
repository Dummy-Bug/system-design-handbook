# Percentiles — P50, P95, P99, P999

> [!question] Is your system actually fast for all users — or just on average?
> Averages lie. Percentiles tell the truth.

---

## Why Averages Lie

Look at these response times for 10 requests your API just handled:

```
10ms, 12ms, 11ms, 13ms, 10ms, 11ms, 12ms, 10ms, 11ms, 500ms
```

**Average = 59ms**

Does that feel right? 9 out of 10 users got ~11ms. One user got 500ms. The average (59ms) represents absolutely nobody's actual experience.

The fast users weren't as slow as 59ms. The slow user wasn't as fast as 59ms.

> [!warning] The real danger
> If your team monitors only average latency and it looks fine — you could have thousands of users having a terrible experience and never know. The average buries the outliers.

---

## What Percentiles Actually Mean

Instead of *"what's the average time?"*, percentiles ask:

**"X% of requests completed within what time?"**

Sort all your response times from fastest to slowest. A percentile tells you the value at a specific position in that sorted list.

Using our example sorted:
```
10ms, 10ms, 10ms, 11ms, 11ms, 11ms, 12ms, 12ms, 13ms, 500ms
```

| Percentile | Meaning | Value |
|---|---|---|
| **P50** | 50% of requests completed within this time — the median, the typical user | 11ms |
| **P95** | 95% of requests completed within this time — only 5% were slower | 13ms |
| **P99** | 99% of requests completed within this time — only 1% were slower | 500ms |
| **P999** | 99.9% of requests completed within this time — only 0.1% were slower | used at massive scale |

> [!info] P99 = 500ms here
> The average (59ms) completely hid this. P99 surfaces it immediately. That one slow request is now visible and measurable.

---

## Why P99 Matters More Than P50 at Scale

At small scale, 1% of requests being slow feels negligible.

At Google scale — 10 billion searches per day — 1% is **100 million bad experiences daily**.

At your company's scale — 1 million requests per day — 1% is still **10,000 frustrated users every single day**.

> **At scale, your P99 is somebody's everyday experience.**

---

## Which Percentile to Optimize For

You don't just look at one percentile in isolation. You monitor all of them together — P50 tells you the typical experience, P95 shows occasional slowness creeping in, P99 surfaces serious outliers. Each tells you something different about your system's health.

But when setting a target for your system, you pick **one** to optimize for based on how much a slow request hurts your users:

Each system has a different tolerance for slow requests. Match the percentile to the user's expectation:

| System | Optimize for | Why |
|---|---|---|
| Chat app (WhatsApp) | P99 | Nobody tolerates a message taking 2 seconds |
| Stock trading platform | P999 | One slow trade can cost millions |
| Payment API | P99 | User is staring at a loading spinner waiting for confirmation |
| Google Search | P99 | Users abandon after 2 seconds, go to competitor |
| Video upload | P95 | Uploads are expected to take time, occasional slowness is fine |
| Batch analytics pipeline | P50 | Nobody is waiting in real time, typical performance is enough |
| Hospital patient monitoring | P999 | A missed alert can cost a life |
| Ride matching (Uber) | P99 | Driver assignment taking 10 seconds feels broken |
| Email delivery | P95 | A slight delay is acceptable, total failures are not |
| Game server (FPS) | P999 | Even rare lag spikes ruin the experience — players notice 50ms |

---

## How to Use This in an Interview

Never say *"the system should have low latency"*.

Say: *"P99 latency should be under 100ms — at our scale of 10M daily users, even 1% slow requests means 100K bad experiences per day which is unacceptable for a real-time chat system."*

> [!tip] The formula for scale impact
> `Users affected per day = Daily requests × (1 - percentile as decimal)`
>
> 10M requests/day at P99 = 10M × 0.01 = **100,000 users getting a slow response every day**
