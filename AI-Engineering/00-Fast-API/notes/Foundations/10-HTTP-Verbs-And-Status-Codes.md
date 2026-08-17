A backend with no frontend has an obvious testing problem: there are no buttons, no forms, nothing to click that sends a request. Everything that would normally come from user interaction has to be constructed by hand instead — which is the actual reason a web request client is a required tool here, not an optional convenience.

---

## GET is special: it works from a browser address bar

Copy any `GET` endpoint's URL and paste it directly into a browser's address bar, and it works — the browser makes a `GET` request just by navigating there. This is why simple API exploration is often done by just visiting a URL directly, no separate tool required.

No other verb can be triggered this way. A `POST`, `PUT`, `PATCH`, or `DELETE` request needs something that constructs the request deliberately — a form, a script, or a client like Postman / Web Request Kit. There is no way to type a URL into an address bar and have the browser send a `POST`.

This is the concrete reason a request client earns its place in the toolkit: it's simulating everything a real frontend would normally provide, for every verb **other** than GET.

---

## The verbs

| Verb | Job | Idempotent? |
|---|---|---|
| **GET** | Read a resource | Yes |
| **POST** | Create a new resource | No |
| **PUT** | Replace a resource completely | Yes |
| **PATCH** | Update a resource partially | No |
| **DELETE** | Remove a resource | Yes |
| **HEAD** | Same as GET, but headers only — no body | Yes |
| **OPTIONS** | Capability check — what's allowed on this endpoint | Yes |

### What idempotent actually means

**Idempotent** means: sending the same request more than once produces the same end state as sending it exactly once.

- **GET** — reading the same resource repeatedly should return the same data, every time, until something changes it. Reading doesn't change anything, so nothing about a repeated read can differ.
- **PUT** — sends the complete replacement data for a given id. If the same `PUT` request accidentally fires five times, the end result is identical to it firing once: the resource ends up in that exact replaced state either way.
- **DELETE** — one request says **this id should be deleted.** If the request is accidentally sent twice, only one deletion actually happens — the first request deletes it, and the second finds nothing left to delete. The **end state** (the resource is gone) is the same regardless of how many times the request landed.
- **POST** — deliberately **not** idempotent. Each `POST` is a request to create something new. Sending the same **create an order** request five times should reasonably create five orders, not one — repetition is expected to have a cumulative effect.
- **PATCH** — updates only the fields actually sent, leaving the rest untouched. More network-efficient than `PUT` for small changes, but not guaranteed idempotent the way `PUT` is, since a partial update's effect can depend on the resource's current state.

> [!important] Idempotency is a **guarantee your endpoint needs to honor**, not something that happens automatically just by choosing the right verb name. Naming a route `PUT` doesn't make it idempotent — the handler's own logic has to actually behave that way (e.g., a full replace rather than an increment). The verb is a signal of **intent** to whoever's calling the API; the guarantee still has to be built.

### HEAD and OPTIONS — rarely used, worth recognizing

**HEAD** is functionally identical to `GET`, except the response body is stripped out — only headers come back. Useful when the caller only needs metadata (does this resource exist, how large is it) without paying the cost of transferring the full body.

**OPTIONS** is a capability check — it's how a client asks **what's allowed here?** This is the mechanism behind **CORS preflight requests**: browsers automatically send an `OPTIONS` request before certain cross-origin requests, to check the server's permissions before sending the real one. A request client like Postman or Web Request Kit does **not** do this automatically — it's a plain HTTP client, not a browser, so it doesn't simulate that preflight behavior unless an `OPTIONS` request is sent manually.

---

## Status codes: a convention, not an enforced rule

All five ranges, since the callout below and the earlier backend note both refer to the later ones:

| Range | Category | What it says |
|---|---|---|
| **100–199** | Informational | Keep going — rare in ordinary API work |
| **200–299** | Success | It worked. `200` OK, `201` Created, `204` No Content |
| **300–399** | Redirection | It lives somewhere else now |
| **400–499** | Client error | You asked wrong. `400` Bad Request, `404` Not Found, `422` Unprocessable Content |
| **500–599** | Server error | The server broke while trying. `500` Internal Server Error |

The two that show up constantly in FastAPI specifically are `422`, which FastAPI returns automatically whenever incoming data fails to match a model, and `404`, which is raised by hand whenever a well-formed request asks for something that isn't there.

> [!note] Nothing technically stops a server from returning `200` on an error, or `404` on a success. The ranges are a **widely followed convention**, not something HTTP enforces. An organization can pick its own standard, as long as it stays consistent — but returning success codes for failures, or vice versa, is the kind of inconsistency that actively misleads whoever's consuming the API. The earlier note on backends already covered `200`/`404`/`500` as concrete examples of this convention in action.

The reassurance worth ending on: none of this needs to be memorized or hand-built. FastAPI has proper status-code handling built in, which is exactly what the actual project work — starting next — puts to use.
