# Streaming in LangGraph — Reading Path

How a LangGraph pipeline streams events to a frontend, from async fundamentals through to the driver/consumer architecture and the HITL interrupt mechanic.

This MOC links 14 atomic notes across three folders. Read in order on first pass; jump around freely once the mental model is built.

---

## Async Fundamentals

The substrate everything else is built on. Skip if you already understand the asyncio event loop and queue API.

1. [[coroutines-and-event-loop]] — what `async def` and `await` actually do underneath
2. [[queue-api-and-backpressure]] — `asyncio.Queue` API surface, bounded vs unbounded, backpressure
3. [[put-vs-put-nowait]] — when the producer-side difference vanishes, and why you still pick deliberately
4. [[get-vs-get-nowait]] — why the consumer side is asymmetric with the producer side

---

## The Streaming Architecture Problem

Where does event-emission responsibility belong, and where does the queue object live?

5. [[architecture-inversion]] — nodes own emission; streaming service is dumb infrastructure
6. [[per-request-queue-scoping]] — why the queue lives on RequestContext, not on global state, not in graph state
7. [[queue-vs-list-vs-sse-vs-sqs]] — picking the right messaging tool for the right distance and durability

---

## The Interrupt Mechanic

How a graph pauses mid-execution for human input and resumes minutes later from a new HTTP request.

8. [[what-interrupt-actually-is]] — what "pause" actually means; why the coroutine stack can't be serialized
9. [[re-execution-on-resume]] — the node re-runs from the top; reads-before, writes-never
10. [[interrupt-pause-vs-return]] — same line of code, different behavior based on checkpointer state
11. [[why-await-response-fails]] — why you can't just `await` the human's response inside the node (and how this leads back to reinventing `interrupt()`)

---

## Putting It Together

Combining the architecture with the interrupt mechanic into a working streaming pipeline.

12. [[driver-pattern]] — funneling node-level and graph-level events onto a single queue
13. [[sentinel-pattern]] — how the consumer knows when to stop; `finally` as the only safe place
14. [[shield-slow-warning]] — `asyncio.shield` for "still working..." progress without killing the underlying call

---

## What You Should Be Able to Explain After This Path

- Why a streaming service should never interpret graph state — and what it should do instead
- Where an `asyncio.Queue` can and cannot live, and why the answer is "per-request context only"
- What happens to a coroutine's stack when it's "paused" — and why that means LangGraph can't actually pause inside a node
- Why the same `interrupt()` call can both pause and return, and what determines which
- How to design a streaming pipeline that survives interrupts, exceptions, and slow operations cleanly
