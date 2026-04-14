
> [!info] The read path checks the paste status before doing anything else. Each status maps to a specific HTTP response — no ambiguity, no silent failures.

---

## The status-to-response map

```
status = PROCESSED    → 200 OK + paste content
status = IN_PROGRESS  → 503 Service Unavailable + Retry-After: 30
status = FAILED       → 404 Not Found
row not found         → 404 Not Found
```

Each case is distinct and honest.

---

## Why 503 for IN_PROGRESS, not 202

**202 Accepted** means "the server accepted your request and will process it." It's a write-side code — used when a POST or PUT is queued for processing. It doesn't make semantic sense on a GET request.

**503 Service Unavailable** means "the resource exists but can't be served right now — try again later." This is exactly the situation: the paste exists (DB row is there, shortCode is valid), but the content isn't available yet because the S3 upload is still in flight.

The `Retry-After: 30` header tells the client to try again in 30 seconds. By then, either the upload succeeded (200 on retry) or all retries exhausted and it's FAILED (404 on retry).

---

## Why 404 for FAILED, not 500

**500 Internal Server Error** implies something went wrong on the server that the client can't do anything about. It signals a bug or unexpected state.

**404 Not Found** is the right response here: the paste was never successfully created. From the client's perspective, this shortCode does not have readable content — it's effectively the same as a paste that never existed. The client can surface this to the user as "paste not found" or "this link is invalid."

Using 500 for a FAILED paste would be misleading — it's not a server bug, it's a resource that failed to materialise.

---

## The race condition argument

The most natural concern: user gets 201, shares the link, friend clicks it while the paste is still IN_PROGRESS.

In practice this race is nearly impossible:

```
Async S3 upload completes in:   ~100–200ms
Time for user to:
  - copy the shortCode
  - paste it into a message
  - send it
  - recipient opens it
  Realistic minimum:             30+ seconds
```

The upload is done hundreds of times before a human can share and click. The IN_PROGRESS state exists to handle S3 actually being down for a meaningful period — not for the normal case.

So the 201 is honest: the paste was created. The shortCode is yours. Share it. It will be readable by the time anyone clicks it.

---

> [!tip] Interview framing
> "The async upload means s3_url is NULL at the time of the 201 response. We handle failures with a state machine: IN_PROGRESS → PROCESSED on success, IN_PROGRESS → FAILED after retries exhausted. Upload jobs go into a message queue so they survive app server crashes — workers retry with exponential backoff and jitter. Read path checks status: PROCESSED returns 200, IN_PROGRESS returns 503 with Retry-After, FAILED returns 404. In practice the race condition between sharing and reading is nearly impossible — the async upload completes in ~200ms, far faster than any human can share and click a link."
