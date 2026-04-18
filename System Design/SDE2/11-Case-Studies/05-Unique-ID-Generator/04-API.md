# API Design

## Why POST and not GET

The instinct is to use GET — after all, you're "getting" an ID. But GET is semantically idempotent: calling it twice should return the same result. This endpoint does the opposite — every call must return a *different* ID. POST is the correct verb because each call creates something new.

---

## The endpoint

```
POST /api/v1/id
```

No request body required.

---

## Why no request body

The caller — say the Tweet service or the Order service — has nothing useful to tell the ID generator. The generator doesn't need to know what the ID is for, who is requesting it, or where it will be stored. Its only job is to return a unique ID.

The machine ID that gets baked into the ID is the ID generator node's own machine ID — determined internally, not passed by the caller. The caller doesn't know which node it's talking to (the load balancer handles that), and it shouldn't need to.

> [!info] Optional: service namespace for observability
> Some systems optionally accept a `service_name` in the body purely for monitoring — so the generator can track which services are consuming IDs and at what rate. This is not a core functional requirement, just an observability nicety.

---

## Response

```json
{
  "id": 3457892345678901234
}
```

**Type: `int64` / `long`** — not a string.

> [!danger] Don't return the ID as a string
> It's tempting to return `"id": "3457892345678901234"` as a string for "safety." But the whole point of this service is space-efficient, machine-readable IDs. A 64-bit integer fits in 8 bytes. A string representation of that same number takes 19 bytes — more than double. Every caller stores this in a database column; `BIGINT` is the right type, not `VARCHAR`.

> [!danger] Don't return a separate timestamp field
> One of the FRs is that IDs are sortable by creation time. If the design is correct, time is already encoded inside the ID itself. Returning a separate `timestamp` field is redundant — it means the ID failed to encode time, or the caller doesn't trust it. Neither is acceptable.

---

## Summary

| Field | Value |
|---|---|
| Method | POST |
| Path | `/api/v1/id` |
| Request body | None (optional `service_name` for observability) |
| Response | `{ "id": int64 }` |
| Response type | `int64` — not string, not double |
