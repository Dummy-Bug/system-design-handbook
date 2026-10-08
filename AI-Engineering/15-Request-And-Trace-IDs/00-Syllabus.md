#ids #request-id #tracing #correlation #syllabus

# 15 · Request And Trace IDs — Syllabus

**4 notes, 22 rungs.** A short folder, between `14-Logging` and `02-Observability`. It starts where logging left off, with a request ID in every line, and ends at the point where a trace needs spans. Every kind of ID a production service carries is placed by its scope: one call, one operation across services, one user. The evaluation of which ones the society tax agent needs is the last note.

> A rung is the **smallest thing that has to be understood before the next thing makes sense**. Rungs are ordered so that **each one either breaks the previous one or is forced by it**, and so that **no term is used before it is defined**.

**Currency check (2026-10-08), on Python 3.14.7.** Python 3.14 has `uuid.uuid7()` in its standard library; Python 3.13 and older need a package such as `uuid-utils`. The trace header standard is W3C Trace Context, `traceparent`; OpenTelemetry log records carry its `TraceId` and `SpanId`. `X-Request-Id` is a widely used convention, not a formal standard.

---

## How to teach from this

**One note at a time, one rung at a time.** A rung is taught in the terminal first, and only after a response does that section go into the note.

**Where a rung says break, it is run, not read.** The lab is `~/Desktop/projects/ids-lab/src/ids_lab/`, `note01/` for note 1 and so on.

**Clean slate.** Nothing is explained by comparison with another language or framework.

---

## Note 1 · One Request, One ID

**Break:** five header values, sent to the function that chooses a request ID; only one of them is kept.

1. A service handles many requests at once, so their log lines interleave; a request ID in every line is what separates them again.
2. The ID either comes from the caller, in an `X-Request-Id` header, or is made fresh, as a UUIDv7, which sorts by creation time.
3. A header comes from outside, so it is checked before it is trusted: a fixed set of characters and a maximum length, with `fullmatch`, because `match` accepts anything that merely starts well.
4. The caller makes a new ID for every call, not one per user: five clicks are five requests and five IDs.
5. Reusing the caller's ID is what lets one ID find the same click in every service it passed through; such an ID is called a **correlation ID**.
6. That works only if every service reuses it, forwards it and logs it, into one log store, under one field name.
7. It finds every line of a click, but cannot say which service called which, or where the time went.

> **Recall:** Why reuse a caller's ID at all? · What could an unchecked header do? · Why `fullmatch`? · What four things must hold for one ID to find a click in every service?

---

## Note 2 · Many IDs, Many Scopes

**Break:** place each of eleven production IDs by what it stays the same for.

1. IDs differ by **scope**: the set of work over which an ID stays the same.
2. One request or one operation: request ID, trace ID, span ID, and a cloud vendor's own trace header.
3. Many requests, grouped by who made them: session ID, user ID, tenant ID, and W3C baggage, which carries such values across services.
4. Some IDs in logs have a different job entirely: an idempotency key makes a retry safe, a job ID names background work, a message ID lets a consumer skip a duplicate, and business IDs make a domain searchable.
5. The scopes nest: a session holds many clicks, each click is one trace, each trace holds many spans, and user and tenant sit on all of them.

> **Recall:** What is an ID's scope? · Which IDs group requests by who made them? · Why is an idempotency key not a tracing ID?

---

## Note 3 · Traces And Spans

**Break:** one click through three services and two bank calls, with every ID printed at every hop.

1. A **trace ID** stays the same across every hop of one operation, exactly like a request ID; what it adds is a standard format every tracing tool understands.
2. A request ID finds the lines, but cannot show which of two bank calls was slow.
3. A **span** is one piece of work with its own **span ID**, its **parent's span ID**, and its own start and end time; parents turn the spans into a tree, and the times turn the tree into a waterfall.
4. Every span gets its own ID, even when it shares a parent with another: siblings have one parent and different IDs.
5. The `traceparent` header carries the trace ID and the sender's span ID together; each service copies the trace ID unchanged, makes its own span ID, and sends that on.
6. Without spans, a trace ID is a request ID in a standard format; the spans are what the rest of tracing is built on, in `02-Observability`.

> **Recall:** What does a trace ID add over a request ID? · Which field turns a list of spans into a tree? · Can two spans share an ID? · Why is the trace ID never lost between hops?

---

## Note 4 · Which IDs The Society Tax Agent Needs

Not yet taught. Each ID from note 2 is weighed against the society tax agent's real cases, and kept, planned or left out, with the reason.

---

## Deferred, deliberately

| Topic | Why it is out |
|---|---|
| Instrumenting spans with OpenTelemetry, sampling, exporters | `02-Observability`, which covers tracing in depth |
| How an idempotency store works | a reliability topic, not a tracing one |
| W3C baggage in detail | named only; nothing here sends it yet |

---

## Where this lands in the society tax agent

**The starting point, 2026-10-08.**

| Piece | State |
|---|---|
| request ID chosen per request: the caller's if valid, otherwise a new UUIDv7 | done |
| request ID in every log line and in the `X-Request-Id` response header | done |
| request ID forwarded to the society's records service on every call | planned, in its portal sign-in feature |
| the records service reading the ID and logging it | not there yet |
| the treasurer's web app sending an ID with every call | not checked |
| tenant IDs bound to every log line after sign-in | planned, with its auth |

To be completed by note 4.

---

## Sources to verify against

- [W3C Trace Context](https://www.w3.org/TR/trace-context/), for `traceparent`, trace-id and parent-id
- [W3C Baggage](https://www.w3.org/TR/baggage/)
- [OpenTelemetry log data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/), for `TraceId` and `SpanId` on log records
- [Heroku HTTP request IDs](https://devcenter.heroku.com/articles/http-request-id), a production example of `X-Request-ID`
- [AWS Application Load Balancer request tracing](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-request-tracing.html), for `X-Amzn-Trace-Id`
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [Python `uuid` module](https://docs.python.org/3/library/uuid.html), for `uuid7()`
