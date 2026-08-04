`raise HTTPException(...)` has shown up constantly so far, and it works — but it's not actually how production FastAPI applications are usually structured. The more common pattern splits the job into two pieces: a **custom exception class** that carries data about what went wrong, and a **custom exception handler** that turns that data into an actual response. They're always written side by side, usually in the same file.

---

## Part one: the exception class

```python
class ResourceNotFoundError(Exception):
    def __init__(self, resource_id: str):
        self.resource_id = resource_id
```

A few things worth being precise about:

- **It inherits from `Exception`**, not `HTTPException`. This class isn't an HTTP concept at all — it's a plain Python exception that happens to carry whatever data the eventual handler will need.
- **The `__init__` stores data on `self`**, not for the exception's own sake, but so that *whatever catches this exception later* can read it back off — `self.resource_id = resource_id` here means anything handling this exception can access `exc.resource_id`.
- **This class, by itself, does nothing when raised.** It doesn't know how to become an HTTP response, doesn't know a status code, doesn't format anything. All it does is carry data upward when raised. Turning it into an actual response is a separate job entirely — that's what the handler is for.

> [!note] It's easy to skip calling `super().__init__()` here, since nothing about this class needs the base `Exception`'s own message-handling. The trade-off: without it, `Exception`'s default string representation stays empty — so if this exception were ever printed raw (an unhandled traceback, a stray log line), it wouldn't show anything useful. That's rarely a problem in practice, since the whole point is that a *handler* intercepts it and builds the real response — but it's worth knowing the class is deliberately not self-describing on its own.

A second exception can carry more than one piece of data, and give some fields sensible defaults:

```python
class InvalidInputError(Exception):
    def __init__(self, value: str, reason: str = "Invalid format"):
        self.value = value
        self.reason = reason
```

Same shape, just more attributes stored for the handler to use later.

---

## Part two: the exception handler

A handler is what actually gets registered to catch a specific exception class and produce a response from it.

```python
from fastapi import Request
from fastapi.responses import JSONResponse


async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "resource_not_found",
            "message": f"No resource found for id {exc.resource_id}",
            "resource_id": exc.resource_id,
        },
    )
```

What's different here from every route seen up to this point:

> [!important] Every earlier route just `return`ed a plain dict, and FastAPI converted it to JSON automatically. **That automatic conversion doesn't happen inside a handler.** A handler has to explicitly build and return a `JSONResponse` — status code and JSON content both spelled out by hand. This is the actual reason `JSONResponse` needs importing at all: it's the manual version of something that's normally invisible.

The two parameters are fixed in shape: **`request: Request`** (the request that triggered this, even if unused inside the handler body) and **`exc: ResourceNotFoundError`** — the *specific* exception class this handler is meant to catch, typed exactly, which is also how the data stored on it (`exc.resource_id`) becomes readable here.

A second handler for the second exception class follows the identical shape, just with different content:

```python
async def invalid_input_handler(request: Request, exc: InvalidInputError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_input",
            "message": f"Value {exc.value} is invalid: {exc.reason}",
            "value": exc.value,
        },
    )
```

`404` for "well-formed but not found," `400` for "malformed to begin with" — the same status-code distinction covered when path parameters and error handling were first introduced, now expressed as two different handlers instead of two branches of one `if`.

> [!note] Both handlers are written `async def` here, but neither actually does anything asynchronous — no `await` appears in either body. Per the sync-vs-async rule from earlier, that means plain `def` would be equally correct and arguably more consistent with "only use `async def` when there's a genuine `await`." Both forms work for exception handlers; `async def` is just the more common convention shown here.

---

Defining these classes and handlers doesn't connect them to anything yet — a class raised with `raise ResourceNotFoundError(...)` and a handler sitting in a file are still two disconnected pieces until something tells FastAPI "when this exception type is raised, run that handler." That registration step is separate from writing the classes and handlers themselves.

---

## Part three: registering the handler

The missing piece, done in `main.py` where the `app` object lives:

```python
app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
app.add_exception_handler(InvalidInputError, invalid_input_handler)
```

`app.add_exception_handler(...)` takes exactly two arguments: **the exception class** to watch for, and **the handler function** to run when that specific class is raised anywhere in the app. One call per exception type — two custom exception classes here means two registration calls.

Once both lines exist, the whole chain is finally connected: a route raises `ResourceNotFoundError(...)`, FastAPI recognizes the exception's type, looks up which handler was registered against that exact class, and runs it — producing the `JSONResponse` that handler builds, instead of an unhandled crash. Before this line existed, raising either custom exception would have just been an ordinary uncaught Python exception; this is the line that turns it into a deliberate, formatted HTTP response.

---

## Part four: raising and handling are two separate steps

It's easy to look at `raise ResourceNotFoundError(...)` sitting inside a route and assume that line is what produces the nice JSON error response. **It isn't.** Raising and handling are two completely separate operations, done by two completely separate pieces of code.

```python
raise ResourceNotFoundError(resource_id)
```

This line does exactly one thing: it stops normal execution of the current function and says *"something went wrong — here's a `ResourceNotFoundError` object carrying `resource_id`."* That's the whole job. It doesn't build a response. It doesn't know a status code exists. It doesn't know what JSON is. By itself, this line has no idea what a `404` even means.

> [!important] If `app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)` were never called, raising this exact same exception would **not** produce the formatted error body — it would produce a generic, unhandled `500 Internal Server Error`, because nothing in the app knows what to *do* with a `ResourceNotFoundError` when it sees one. Raising with nothing listening is just a crash. The custom response only exists because something is registered to catch it.

The handler is the piece that's actually listening. `app.add_exception_handler(...)` means: *"anywhere in this app, the instant a `ResourceNotFoundError` is raised — no matter which route, no matter how deep — call this specific handler with it."* That registration is the wire connecting a raise to a response.

Traced in full, one request:

1. A route runs, hits `raise ResourceNotFoundError(resource_id)`.
2. Execution of that route stops immediately — nothing after that line runs.
3. FastAPI catches the exception propagating upward and checks: is a handler registered for this exact type?
4. It finds `resource_not_found_handler`, and calls it — passing in the request and the exception object, which is exactly where `exc.resource_id` comes from.
5. The handler builds and returns the `JSONResponse`.
6. **That** is what actually reaches the client — nothing the original route returned or built directly.

### Why bother splitting it into two pieces at all

The alternative would be formatting the JSON response inline, right where the problem is detected:

```python
if resource_id not in DATA:
    return JSONResponse(status_code=404, content={"error": "...", ...})
```

That works for one route. It stops working cleanly the moment *ten* different routes across an app can all hit the same "resource not found" situation — each one would need to repeat the same response-formatting block, and any future change to that format (a renamed field, an added key) has to be hunted down and repeated in every copy.

Splitting the job means a route's only responsibility is *deciding something went wrong* — one line, `raise ResourceNotFoundError(...)`, with zero knowledge of HTTP status codes or JSON shapes. The *one* place that knows what a 404 response should look like is the handler, written once, guaranteed identical everywhere it fires. A business-logic file like `main.py` never needs to mention `JSONResponse`, `404`, or a response dict at all — that knowledge lives entirely inside the file holding the exceptions and handlers, nowhere near the routes that trigger it.
