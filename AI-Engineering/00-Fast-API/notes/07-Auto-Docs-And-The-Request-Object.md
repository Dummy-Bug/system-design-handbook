Two things worth pulling apart here: the documentation that's already being generated for free, and everything that's hiding inside a single incoming request.

---

## The two documentation UIs

Both come from the `docs_url` and `redoc_url` set when the app was configured — `/docs` and `/redoc` — and both are generated automatically from the routes and their docstrings. Nothing extra is written to produce them.

### Swagger — `/docs`

Lists every route (`read_root`, `list_orders`, `get_order_status`, ...), each expandable, each showing exactly what was written in its docstring — "List recent orders" shows up verbatim, because that's exactly what the function's docstring says.

The app-level metadata configured earlier shows up here too — title, description, version — all pulled directly from the `FastAPI(...)` constructor arguments.

![[AI-Engineering/00-Fast-API/Images/swagger-docs-ui.png]]

Every field in that screenshot traces back to code already written: **"Swiggy Order Service"** is `title`, **"1.2.1"** is `version`, the description paragraph is the `description` string, and each route's one-line summary next to its method badge is that function's docstring. Nothing here was typed into a documentation tool separately — it's all sourced from `main.py`.

Clicking into a route and hitting **Try it out → Execute**:

- Sends a real request to the running backend
- Shows the equivalent `curl` command for that same request
- Shows the actual response, plus response headers
- Lets you download the response

This is a fully working API client built into the docs page — not just a static description of what the API *should* do.

### Redoc — `/redoc`

Same underlying data, different presentation: a single scrollable page instead of expandable sections, with a search bar and a schema viewer for each route. Slightly more polished visually; Swagger tends to be the more commonly used of the two day to day.

Which one gets used is mostly a matter of habit — they're built from the exact same source, so neither is missing information the other has.

### The raw source behind both: `openapi.json`

Both `/docs` and `/redoc` are themselves just two different renderers pointed at one underlying file — the `openapi_url` set earlier, `/openapi.json`. Visiting it directly shows the actual data both UIs are built from:

![[AI-Engineering/00-Fast-API/Images/openapi-json-raw.png]]

This is the **OpenAPI schema**: a single JSON document listing every path, every method, every summary and description, structured to a standard spec. It's why `title`, `description`, and `version` all show up verbatim here too, and why every route's docstring appears twice in this file — once under `"description"`, and mangled into an auto-generated `"operationId"` like `list_orders_orders_get`.

The practical use for this file: it's not just documentation for humans. Tools like Postman can **import** this JSON directly and generate a full request collection from it automatically — one file describing an entire API, machine-readable enough that another program can act on it without a human re-typing every route by hand.

---

## Controlling what shows up in the docs

The decorator takes more than just a path. Each of these is optional, and each one shapes what `/docs` and `/redoc` show for that route.

```python
@app.get(
    "/orders/active",
    summary="Get active orders",
    description="""
    Returns all orders that are currently in the system being prepared,
    or are out for delivery.
    """,
    tags=["orders"],
    response_description="A list of active order objects",
    deprecated=False,
)
def get_active_order():
    """
    Returns all orders that are currently in the system being prepared.
    """
    return {
        "active_orders": [
            {"id": 1, "item": "Masala Dosa", "status": "out for delivery"},
        ]
    }
```

| Parameter | What it controls |
|---|---|
| `summary` | Short one-line label for the route in the docs |
| `description` | Longer explanation — can span multiple lines |
| `tags` | Groups routes together into named sections in the docs UI |
| `response_description` | Describes what the *response* contains, separately from what the endpoint does |
| `deprecated` | Marks the endpoint as deprecated in the docs, without removing it |

None of this is required. If nothing is set, FastAPI falls back to the function's **docstring** as the description shown in the docs — which is exactly why every route so far has had one, even before any of these extra parameters existed.

### Tags group routes — carefully

```python
@app.get("/restaurants", tags=["restaurants"])
def list_restro():
    """
    List restaurants.
    """
    return {"restaurants": "test"}
```

Only `tags` was set here, nothing else — and that's a valid, minimal way to use these parameters. Not every route needs the full set from the first example.

> [!important] Tags work by exact string match, and there is no validation catching a typo. If a route uses `tags=["orders"]` and a later route accidentally writes `tags=["order"]`, FastAPI does not warn — it silently creates a **second**, separate category in the docs, one character off from the first. The category name is freeform text, not a fixed set of choices, so nothing stops a small typo from quietly splitting a group in two.

---

## What's actually inside a request

Everything so far returned fixed dictionaries. The next question: what does FastAPI actually *know* about the request that arrived — and how do you get at it?

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

- **`request: Request`** — declaring a parameter of type `Request` (imported from `fastapi`) is how a route gets access to the raw incoming request. FastAPI recognizes the type hint and passes the actual request object in automatically.
- **`async def` vs. `def`** — both are valid ways to define a route. Not every function needs to be async; it matters specifically when the function is doing non-blocking I/O (an async DB call, an external API call) that benefits from the event loop being able to move on to other work while it waits — the mechanism traced in the WSGI/ASGI note. A route like this one, doing no I/O at all, doesn't strictly need to be async — it's written that way here mostly by convention, since a lot of real routes will be.

### The fields, one at a time

| Field | What it holds |
|---|---|
| `request.method` | `GET`, `POST`, etc. — the decorator already enforces this, but it's readable directly if a handler needs to branch on it |
| `request.url` | The full URL that was hit. It's a URL object, not a plain string — `str(...)` converts it for easy reading/serializing |
| `request.headers` | Metadata the client sent along automatically — which host, connection type, user agent (browser/OS info), and more. Comes back as a header-object; `dict(...)` converts it to a plain dictionary |
| `request.path_params` | Whatever variable segments were captured out of the URL path itself |
| `request.query_params` | Whatever came after the `?` in the URL |

Headers, worth dwelling on for a second: they're metadata *about* the request, sent automatically by whatever client made it — not data you typically type in by hand. A browser or Postman fills in things like `User-Agent` (client and OS info) and `Connection` on its own.

---

## Path params vs. query params

These get confused constantly, and the distinction is simple once it's stated plainly.

|                                        | Path params                                                                                                            | Query params                                                                               |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Where they live**                    | Inside the URL path itself, e.g. `/order/{id}`                                                                         | After a `?` at the end of the URL, e.g. `?name=Elon`                                       |
| **Does the route have to declare it?** | **Yes** — the route's decorator must include the placeholder, e.g. `@app.get("/order/{id}")`, or nothing gets captured | **No** — automatically available on every route, no declaration needed                     |
| **Accessed via**                       | `request.path_params`                                                                                                  | `request.query_params`                                                                     |
| **Example**                            | `/order/42` → `{"id": "42"}` *(only if the route declares `{id}`)*                                                     | `/debug/request-info?name=Hitesh&course=FastAPI` → `{"name": "Elon", "course": "FastAPI"}` |

> [!important] Appending `/Elon` onto `/debug/request-info` does nothing useful, because that route's decorator never declared a path variable — there's nothing for Starlette's route matching to capture. `path_params` stays empty regardless of what gets typed after the URL, until a route is actually written with a `{placeholder}` in its path. That comes later. Query params, by contrast, work immediately on any route — `?key=value` pairs are always parsed and always available, no matter what the route declares.

---

## Testing all of this without writing a frontend

This is the practical use for a web request client, covered earlier only in the abstract. The two shown in practice:

**Postman.** The industry-standard tool. Free tier is generous enough for this kind of work — enter a URL, pick the method (GET, POST, ...), hit Send, and the response comes back along with headers, auth options, and a params editor that auto-populates from the URL's query string.

**Web Request Kit.** A lighter alternative — same basic job (enter URL, pick method, send, inspect response), with a tree view of the response data, a raw view, search across keys, and a simpler interface overall than Postman's.

There are others in the same space — Insomnia, Hoppscotch, Bruno, and more — and the choice between them doesn't matter much. Every one of them exists purely to do one thing: **construct and send an HTTP request, then show you what came back.** That's the entire job description, regardless of which tool's interface it happens to be wrapped in.
