## The two documentation UIs

Both come from the `docs_url` and `redoc_url` set when the app was configured — `/docs` and `/redoc` — and both are generated automatically from the routes and their docstrings. Nothing extra is written to produce them.

### Swagger — `/docs`

Lists every route, each expandable. The docstring is what shows up **inside** an expanded route, as its description.

The app-level metadata configured earlier shows up here too — title, description, version — all pulled directly from the `FastAPI(...)` constructor arguments.

![[AI-Engineering/00-Fast-API/Images/swagger-docs-ui.png]]

Every field in that screenshot traces back to code already written: **Swiggy Order Service** is `title`, **1.2.1** is `version`, and the description paragraph is the `description` string.

> [!important] The grey label next to each method badge — **Read Root**, **About**, **List Orders**, **Get Order Status**, **Request Info** — is **not** the docstring. It is the **function's own name**, with underscores turned into spaces and each word capitalised: `read_root` becomes **Read Root**, `get_order_status` becomes **Get Order Status**. Compare against the actual code and it's obvious — `read_root`'s docstring reads `Root endpoint - does a simple health check.`, and none of that text appears anywhere in the screenshot.
>
> This label is OpenAPI's `summary` field, and FastAPI fills it in from the function name whenever `summary=...` isn't set explicitly. The **docstring** becomes the separate `description` field, which is only visible once a route is expanded. Two different fields, two different sources — which is also why a well-named function gets a readable docs listing for free, before a single docstring is written.

Clicking into a route and hitting **Try it out → Execute**:

- Sends a real request to the running backend
- Shows the equivalent `curl` command for that same request
- Shows the actual response, plus response headers
- Lets you download the response

This is a fully working API client built into the docs page — not just a static description of what the API **should** do.

### Redoc — `/redoc`

Same underlying data, different presentation: a single scrollable page instead of expandable sections, with a search bar and a schema viewer for each route. Slightly more polished visually; Swagger tends to be the more commonly used of the two day to day.

Which one gets used is mostly a matter of habit — they're built from the exact same source, so neither is missing information the other has.

### The raw source behind both: `openapi.json`

Both `/docs` and `/redoc` are themselves just two different renderers pointed at one underlying file — the `openapi_url` set earlier, `/openapi.json`. Visiting it directly shows the actual data both UIs are built from:

![[AI-Engineering/00-Fast-API/Images/openapi-json-raw.png]]

This is the **OpenAPI schema**: a single JSON document listing every path, every method, every summary and description, structured to a standard spec. It's why `title`, `description`, and `version` all show up verbatim here too. Each route contributes three separate strings, from three different places in the code:

| Field in `openapi.json` | Where it comes from |
|---|---|
| `summary` | The **function name**, prettified — `list_orders` becomes `List Orders`. Overridden by `summary=...` on the decorator. |
| `description` | The function's **docstring**. Overridden by `description=...` on the decorator. |
| `operationId` | Auto-generated from the **function name + path + method**, glued together — `list_orders` on `GET /orders` becomes `list_orders_orders_get`. The docstring plays no part in it. |

`operationId` looks like noise, but it's the stable machine-readable handle for that endpoint — client-code generators use it to name the function they produce for calling this route.

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
| `response_description` | Describes what the **response** contains, separately from what the endpoint does |
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


