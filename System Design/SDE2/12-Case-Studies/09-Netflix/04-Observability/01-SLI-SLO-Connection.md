# Observability — SLI to SLO Connection

> [!info] SLO is the target. SLI is the measurement. Writing a number in the NFR is easy — knowing whether you're actually hitting it in production requires instrumentation.

---

## The Gap Between Design and Reality

When you design Netflix, you estimate: Redis genre cache hit ~1ms, BFF fan-out ~50ms, manifest fetch from CDN ~30ms. You conclude API latency should be well under 200ms and Time to First Frame well under 2 seconds.

But those are estimates. Production is not a whiteboard.

Maybe the BFF is waiting too long on a slow genre service before timing out. Maybe CDN cache miss rates are higher than expected on a new release night, forcing clients to fall back to S3. Maybe adaptive bitrate is switching quality too aggressively and introducing stutter the buffering ratio metric doesn't capture.

None of this shows up in estimates. It only shows up when you measure.

---

## What SLI Actually Means

SLI stands for Service Level Indicator. It is the actual measured value of the thing your SLO is about.

```
SLO (target):   API latency p99 < 200ms
SLI (reality):  actual measured p99 = 143ms  ← this is what you observe in production
```

The SLO tells you what you promised. The SLI tells you what you delivered. The only way to know if you're meeting your SLO is to continuously measure the SLI and compare.

---

## Netflix's SLOs and Their SLIs

Netflix has two types of latency — they are different problems measured differently.

**API Latency** — the home feed, search, metadata. Standard request-response.

**Time to First Frame (TTFF)** — the delay between clicking Play and the first video frame appearing. This involves fetching the manifest, selecting a quality, downloading the first chunk, and decoding it. Fundamentally slower than API calls.

**Smooth Playback** — staying in playback without buffering for the entire duration. The most Netflix-specific SLO — no other case study has this.

```
SLO 1:  API latency p99 < 200ms
SLI 1:  time from request receipt to response sent, measured on every API call

SLO 2:  Time to First Frame < 2 seconds
SLI 2:  time from Play button click to first video frame rendered, measured per stream start

SLO 3:  Buffering ratio < 0.1%
SLI 3:  total buffering time / total playback time, measured per active stream

SLO 4:  Availability > 99.99%
SLI 4:  successful stream starts / total stream start attempts, measured continuously
```

These are separate SLOs because they measure independent failure modes. A CDN outage tanks TTFF and buffering ratio while API latency stays healthy. A BFF overload degrades API latency while streams already in progress are unaffected. Measuring separately means separate alerting — one SLO breach pages someone without the others needing to breach too.

> [!tip] Interview framing
> "Four SLOs: API latency p99 < 200ms, Time to First Frame < 2 seconds, buffering ratio < 0.1%, availability > 99.99%. Measured separately — a CDN issue shouldn't mask itself behind healthy API metrics. TTFF is the most Netflix-specific SLO — no other system has it."
