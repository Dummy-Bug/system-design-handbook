## What's actually inside a request

Everything so far returned fixed dictionaries. The next question: what does FastAPI actually **know** about the request that arrived — and how do you get at it?

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/debug/request-info")
async def request_info(request: Request):
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "path_params": request.path_params,
        "query_params": dict(request.query_params),
    }
```

A few things to notice before the fields themselves:

- **`request: Request`** — declaring a parameter of type `Request` (imported from `fastapi`) is how a route gets access to the raw incoming request. FastAPI recognizes the **type hint** and passes the actual request object in automatically.
- **`async def` vs. `def`** — both are valid ways to define a route. Not every function needs to be async; it matters specifically when the function is doing non-blocking I/O (an async DB call, an external API call) that benefits from the event loop being able to move on to other work while it waits — the mechanism traced in the WSGI/ASGI note. A route like this one, doing no I/O at all, doesn't strictly need to be async — it's written that way here mostly by convention, since a lot of real routes will be.

### The fields, one at a time

| Field | What it holds |
|---|---|
| `request.method` | `GET`, `POST`, etc. — the decorator already enforces this, but it's readable directly if a handler needs to branch on it |
| `request.url` | The full URL that was hit. It's a URL object, not a plain string — `str(...)` converts it for easy reading/serializing |
| `request.headers` | Metadata the client sent along automatically — which host, connection type, user agent (browser/OS info), and more. Comes back as a header-object; `dict(...)` converts it to a plain dictionary |
| `request.path_params` | Whatever variable segments were captured out of the URL path itself |
| `request.query_params` | Whatever came after the `?` in the URL |

Headers, worth dwelling on for a second: they're metadata **about** the request, sent automatically by whatever client made it — not data you typically type in by hand. A browser or Postman fills in things like `User-Agent` (client and OS info) and `Connection` on its own.

---

## Path params vs. query params

These get confused constantly, and the distinction is simple once it's stated plainly.

|                                        | Path params                                                                                                            | Query params                                                                               |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Where they live**                    | Inside the URL path itself, e.g. `/order/{id}`                                                                         | After a `?` at the end of the URL, e.g. `?name=Elon`                                       |
| **Does the route have to declare it?** | **Yes** — the route's decorator must include the placeholder, e.g. `@app.get("/order/{id}")`, or nothing gets captured | **No** — automatically available on every route, no declaration needed                     |
| **Accessed via**                       | `request.path_params`                                                                                                  | `request.query_params`                                                                     |
| **Example**                            | `/order/42` → `{"id": "42"}` **(only if the route declares `{id}`)**                                                     | `/debug/request-info?name=Elon&course=FastAPI` → `{"name": "Elon", "course": "FastAPI"}` |

> [!important] Appending `/Elon` onto `/debug/request-info` does nothing useful, because that route's decorator never declared a path variable — there's nothing for Starlette's route matching to capture. `path_params` stays empty regardless of what gets typed after the URL, until a route is actually written with a `{placeholder}` in its path. That comes later. Query params, by contrast, work immediately on any route — `?key=value` pairs are always parsed and always available, no matter what the route declares.

---

## Testing all of this without writing a frontend

This is the practical use for a web request client, covered earlier only in the abstract. The two shown in practice:

**Postman.** The industry-standard tool. Free tier is generous enough for this kind of work — enter a URL, pick the method (GET, POST, ...), hit Send, and the response comes back along with headers, auth options, and a params editor that auto-populates from the URL's query string.

**Web Request Kit.** A lighter alternative — same basic job (enter URL, pick method, send, inspect response), with a tree view of the response data, a raw view, search across keys, and a simpler interface overall than Postman's.

There are others in the same space — Insomnia, Hoppscotch, Bruno, and more — and the choice between them doesn't matter much. Every one of them exists purely to do one thing: **construct and send an HTTP request, then show you what came back.** That's the entire job description, regardless of which tool's interface it happens to be wrapped in.