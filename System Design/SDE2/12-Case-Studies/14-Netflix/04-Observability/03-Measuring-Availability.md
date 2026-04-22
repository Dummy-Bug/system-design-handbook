# Observability — Measuring Availability

> [!info] Availability is not "is the server running?" — it is "did the user's stream start?" A BFF can be alive and returning 503s on every home feed request. That is not available.

---

## The Health Check Trap

The instinct when monitoring availability is to ping the server — send a heartbeat every few seconds and check if it responds. If it responds, it's up.

Consider this scenario:

```
BFF instance is running             ✓
Health check endpoint returns 200   ✓
But: Redis circuit breaker is OPEN
Result: every home feed request returns 503
```

From the health check: server is healthy. From the user: blank home screen. The health check missed the actual failure entirely.

Availability must be measured on real user requests, not synthetic pings.

---

## The Availability SLI Formula

```
Availability = successful operations / total operations
```

**Stream start availability:**

```
stream_start_attempts  — incremented on every Play button press
stream_start_successes — incremented when first chunk delivered to client

Stream start availability = stream_start_successes / stream_start_attempts
Target: 99.99%
```

**Home feed availability:**

```
home_feed_requests  — incremented on every GET /api/v1/home
home_feed_successes — incremented when BFF returns at least one row

Home feed availability = home_feed_successes / home_feed_requests
Target: 99.99%
```

Stream start and home feed are tracked separately. A CDN outage kills stream start availability while home feed stays healthy — genre metadata is cached in Redis and the BFF still responds. Measuring separately means the CDN failure pages immediately even when the home feed looks fine.

---

## What Counts as Success

For stream starts:

```
Play → manifest delivered → first chunk downloaded → frame rendered    ✓ success
Play → BFF returns 503                                                  ✗ failure
Play → manifest delivered → CDN timeout on chunk fetch                 ✗ failure
Play → entitlement check fails → 403 returned                          ✓ success (system worked correctly)
Play → user on slow network → quality drops to 480p but stream starts  ✓ success
```

A 403 for an unentitled user is a success — the system correctly enforced access control. A CDN timeout is a failure — the user wanted to watch and couldn't. Quality degradation is a success — the stream started, just at lower quality.

For home feed:

```
GET /api/v1/home → BFF returns 15 rows (Action service was down, row omitted)  ✓ success
GET /api/v1/home → BFF returns 503                                              ✗ failure
GET /api/v1/home → BFF returns 0 rows                                           ✗ failure
```

Graceful degradation counts as success. If the Action genre service is down and the BFF returns 19 rows instead of 20, that is a successful response — the system degraded gracefully without failing the user. A full 503 is the failure.

---

## Smooth Playback Availability

Beyond stream start, Netflix tracks whether streams stay healthy throughout playback. A stream that starts but buffers every 30 seconds is technically "available" by the stream start metric — but the user experience is broken.

```
active_streams        — number of streams currently playing
buffering_streams     — streams currently in a buffering state

Buffering ratio = buffering_streams / active_streams
Target: < 0.1%
```

At 20M concurrent viewers, 0.1% means 20,000 users buffering at any given moment is acceptable. More than that and something is degraded.

> [!tip] Interview framing
> "Availability is measured on real traffic — stream start successes divided by attempts. 403s count as successes. CDN timeouts count as failures. Home feed with one omitted row counts as success — graceful degradation still served the user. Stream start and home feed are tracked separately so a CDN failure alerts independently of BFF health."
