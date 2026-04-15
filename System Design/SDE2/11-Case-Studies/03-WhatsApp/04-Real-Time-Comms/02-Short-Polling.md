
> [!info] Short polling — the naive fix
> The simplest way to fake real-time over HTTP: the client asks the server repeatedly on a fixed interval. "Any new messages?" — wait — "Any new messages?" — wait. It works, technically. But the numbers destroy it at scale.

---

## How it works

The client sets a timer. Every N seconds, it fires an HTTP request asking for new messages. The server checks, responds with whatever arrived since the last poll, and closes the connection. The timer fires again, and the cycle repeats.

```
t=0s:  Client → "GET /messages?since=0"    → Server → "nothing"
t=2s:  Client → "GET /messages?since=0"    → Server → "nothing"
t=4s:  Client → "GET /messages?since=0"    → Server → "nothing"
t=5s:  Alice sends Bob a message
t=6s:  Client → "GET /messages?since=0"    → Server → "1 new message"
```

Bob waits up to 2 seconds to see Alice's message. If the interval is 1 second, Bob waits up to 1 second. The only way to reduce latency is to poll faster — which makes the cost problem worse.

---

## The math — why it breaks at scale

Assumptions (80/20 rule applied twice):
```
MAU                   → 500M
DAU                   → 20% of MAU  = 100M  (80/20 — not everyone is active daily)
Concurrent online     → 20% of DAU  = 20M   (80/20 — not everyone is online at the same moment)
Poll interval         → every 2 seconds
```

Each online user fires one request every 2 seconds:

```
Requests/sec = 20M users / 2 seconds = 10M requests/sec
```

10 million requests per second. Now ask: how many of those return actual messages?

Write QPS is 10k messages/sec. So out of 10M requests:

```
Requests with a real message → 10k / 10M = 0.1% of requests
Empty responses              → 99.9% of all requests
```

Your servers are handling **10 million requests per second** to deliver **10 thousand messages per second**. You are doing 1,000× more work than necessary. 999 out of every 1,000 requests are pure waste — CPU, memory, network bandwidth, all burned on "nothing new here."

---

## The latency problem on top of the waste

Even with all that waste, you still don't get real-time. With a 2-second poll interval:

```
Best case:  message arrives 1ms after a poll → Bob sees it in ~2 seconds
Worst case: message arrives 1ms before a poll → Bob sees it immediately  
Average:    Bob waits ~1 second to see a message
```

Your 200ms latency SLO is completely out of reach. Reducing the interval to 200ms would mean:

```
Requests/sec = 20M users / 0.2 seconds = 100M requests/sec
```

100 million requests per second — ten times worse — and still only 0.01% of them carry actual data.

---

## Verdict

Short polling is rejected. The waste is catastrophic — 99.9% of requests return nothing. The latency is unacceptable. The only thing it has going for it is simplicity. At any real scale, it is not a viable option.

> [!danger] Common interview mistake
> Some candidates say "short polling is fine, we'll just poll every second." The interviewer will ask you to do the math. 20M users × 1 poll/sec = 20M req/sec, 99.95% empty. That answer fails immediately once the numbers are on the board.
