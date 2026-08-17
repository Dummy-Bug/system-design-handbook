
Earlier note showed the manual version of something FastAPI can do automatically. This is where the automatic version replaces both.

---

## Query parameters, declared instead of read

we know we can do `request.query_params` — and everything after the `?`, get's handed back as a plain dictionary and the code has to inspect by hand. That works, but FastAPI has a much better way: **declare the query parameter as a function argument directly.**

```python
from fastapi import Query

@app.get("/menu")
def get_menu(
    category: str | None = Query(default=None, description="Filter by chai, snacks, or combos"),
):
    ...
```

Reading this apart:

- **`category: str | None`** — the type annotation names every value this parameter is allowed to hold: a string, or `None`. `None` is not a category of values the way `str` is — its type has exactly one member, `None` itself. This annotation does **not** make the parameter optional; that is the default's job, one line down.
- **`Query(default=None, ...)`** — `Query` is how a query parameter's **metadata** gets attached: a `description` that shows up directly in the auto-generated docs, and the default value. **`default=None` is the piece that makes the parameter optional**, so the route works fine with no `?category=...` at all.
- **FastAPI does the matching itself.** No manual dictionary lookup, no `request.query_params.get("category")` — the value (or `None`, if absent) just shows up as `category` inside the function, already extracted.

> [!important] The default is what makes a query parameter optional — not the `| None`. This is the ordinary Python rule, unchanged: a parameter with a default can be left out, a parameter without one cannot. FastAPI reads the same signature Python does and does not invent a second rule for query parameters. Three signatures, each called with `category` left off entirely:
> - `category: str | None = Query(default=None)` → `200`, and `category` is `None` inside the function.
> - `category: str | None = Query()` → `422`, Field required. It has the `| None` and is **still required**.
> - `category: str = Query(default=None)` → `200`. It has no `| None` and is **still optional**.

---

## Path parameters, with automatic type conversion

 `request.path_params` — are always strings, with no conversion. Declaring a path parameter as a typed function argument fixes that too:

```python
@app.get("/menu/{item_id}")
def get_item(item_id: int):
    ...
```

Everything arriving over HTTP is text — there's no such thing as **an integer** on the wire, only the characters `"4"`. But because `item_id` is annotated `int`, **FastAPI converts it automatically** before the function ever sees it. Request `/menu/4`, and `item_id` arrives inside the function as the actual integer `4`, not the string `"4"`.

> [!important] The variable name in the function signature must match the `{placeholder}` name in the decorator **exactly** — `item_id` in both places, not `item_id` in one and `itemId` in the other. There's no autocomplete warning if they drift apart; a mismatch there just means the parameter never gets filled in correctly.

If the value in the URL can't be converted — `/menu/banana` when an `int` is expected — FastAPI rejects the request automatically with a validation error, before the function body runs at all. That validation is a side effect of declaring the type, not something written by hand.

---

## `response_model` — not dependency injection

A route can declare the shape its response is guaranteed to have:

```python
@app.get("/menu", response_model=MenuResponse)
def get_menu(...):
    ...
```

`response_model` tells FastAPI: whatever this function returns, validate it against `MenuResponse`'s shape before sending it out, and use that shape to generate the docs for this route's response.

> [!important] This is genuinely easy to conflate with **dependency injection** — both involve a parameter that the route seems to **depend on** — but they are two unrelated mechanisms. 

> **Dependency injection** is specifically the `Depends(...)` pattern from the request-lifecycle note: something resolved **before** the function runs, at stage 4, usually to hand the function something it needs (a DB session, an authenticated user). 

> `response_model` operates at the opposite end entirely — stage 7, **response validation**, after the function has already returned. Nothing about `response_model` is **injected** into the function; the function never even sees it as a parameter. Worth keeping these two firmly separate, since they solve different problems at different points in the pipeline.

---

## Raising `HTTPException` for error responses

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="No item found in category: chai")
```

This is the standardized way to send back an error instead of a success response. `status_code` sets the HTTP status code the client receives; `detail` is the message that shows up in the JSON error body.

Raising it works exactly like raising any other Python exception — execution of the function stops at that line, and FastAPI catches it and turns it into the corresponding HTTP response, formatted consistently, without any manual `if error: return {...}` branching needed.
