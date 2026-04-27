
## Availability over Consistency

Netflix is a user-facing system, not a financial one. If an admin uploads a new title and it hasn't propagated to all regions yet — that is acceptable. A user seeing a slightly stale homepage is far better than the system returning an error.

> [!info] A vs C decision
> **Choose Availability.** Eventual consistency is acceptable — a newly added title appearing a few seconds late in some regions is not a crisis. An error page is.

---

## Latency

There are two distinct latency targets in a streaming system — they are often confused but measure completely different things.

**API Latency** — loading the homepage, search results, fetching video metadata. This is a standard request-response interaction and should feel instant.

> [!info] API Latency target
> 100–200ms — beyond this users feel the interface is sluggish

**Time to First Frame (TTFF)** — the delay between a user clicking play and the first frame appearing on screen. This is not instant because before playback can start, the client must fetch the manifest file, identify the right chunk, download enough of it to begin, and decode the first frame.

> [!info] TTFF target
> Under 2 seconds — this is Netflix's real-world target. 100ms is not achievable here given the chunk download step alone.

---

## Smooth Playback

This is the most Netflix-specific NFR. Getting to the first frame is only half the problem — the harder part is staying there for 2 hours without buffering.

The client maintains a playback buffer — it downloads chunks slightly ahead of what is currently playing, typically 30 seconds worth. As long as the download speed stays above the playback bitrate, the buffer stays full and playback is smooth.

```
Download speed > Playback bitrate → buffer stays full → smooth playback
Download speed < Playback bitrate → buffer drains   → buffering spinner
```

---

## Fault Tolerance

If the thriller genre service goes down, action and comedy should keep streaming. If one CDN edge node fails, traffic should reroute to the next nearest node. No single component failure should take down the whole platform.

---

## Data Integrity

Whatever a user chose to stream or download, they must receive exactly that content — correct movie, correct episode, correct resolution. No mix-ups in content delivery.

---

## Summary

| NFR | Target |
|-----|--------|
| Consistency model | Availability over consistency |
| API latency | 100–200ms |
| Time to first frame | Under 2 seconds |
| Playback | Smooth, no buffering — adaptive bitrate as fallback |
| Fault tolerance | Genre/region failure must not take down full platform |
| Data integrity | User receives exactly what they requested |
