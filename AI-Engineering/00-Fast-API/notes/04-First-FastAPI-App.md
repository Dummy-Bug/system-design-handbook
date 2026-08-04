Time to move from theory to a running application.

---

## Setting up the project

### Virtual environment

Python needs to already be installed. Any recent version is fine.

```bash

# Mac
python3 -m venv venv
```

This creates a `venv` folder holding an isolated Python environment. A name like `.venv` works too — some tooling can be fussier about dotfiles, but it's not a real obstacle either way.

Activate it:

```bash
source venv/bin/activate
```

> [!note] PyCharm 
> In **PyCharm**, The terminal activation only affects your shell — the editor needs to be told separately, or you get import errors and no autocomplete despite the packages being installed correctly.

### Installing FastAPI

`pip install fastapi` works, but installs the bare minimum — FastAPI alone is not enough to run a production-grade application, since it depends on a cluster of supporting packages.

```bash
pip install "fastapi[standard]"
```

The `[standard]` extra pulls in the full set: Pydantic, `uvicorn`, DNS/email validation utilities, HTTP protocol libraries, and more. Notably, **it brings `uvicorn` along with it** — no separate install step needed.

Then freeze the exact versions for reproducibility:

```bash
pip freeze > requirements.txt
```

This is the standard way to hand off a project — anyone else can recreate the same environment from that one file.

---

## What is uvicorn, and why is it needed at all?

FastAPI code by itself is just Python. Something has to actually run it as a web server, listening on a port, accepting connections. That something is **uvicorn**.

> [!important] Uvicorn is an **ASGI web server implementation for Python**. Its job is to take your FastAPI application and make it live as an actual web server — this is the concrete piece of software behind the ASGI concept discussed earlier: the thing that lets one worker juggle many in-flight requests.

Since it ships with the `[standard]` extra, no separate install is required.

---

## The first route

Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Swiggy orders service",
        "status": "healthy"
    }
```

A few things worth naming precisely:

- **`app = FastAPI()`** creates the **application object** — the thing the rest of your code attaches routes to.
- **`@app.get("/")`** is a decorator. It registers the function directly below it as the handler for GET requests to the root path `/`. `get` maps to retrieving data; there is a matching `post`, `put`, `patch`, `delete` for the other request types covered earlier.
- **The function name is arbitrary.** `read_root` is just a label; calling it anything else changes nothing about behavior.
- **A plain Python dictionary comes back as JSON automatically.** No manual serialization step — return the dict, and FastAPI converts it to JSON on its own.

### Running it

```bash
uvicorn main:app --reload
```

Reading that command: run the file `main`, find the object named `app` inside it, and serve it. `--reload` makes uvicorn watch the files and restart automatically on every change — **hot reload**.

This starts the server at `localhost:8000`. Visiting `/` in a browser shows the returned JSON directly.

### Common flags

```bash
uvicorn main:app --reload --port 8001 --host 0.0.0.0
```

- `--port` — run on a different port than the default 8000
- `--host` — `0.0.0.0` instead of `127.0.0.1` to accept connections from outside localhost
- `--workers` — how many worker processes to run; a production concern, not a development one

### Running it from Python directly

The same server can be started programmatically instead of from the terminal, which is convenient for debugging:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

This is the standard `if __name__ == "__main__":` guard, doing the exact same thing the terminal command did — just triggered by running the file with `python main.py` instead.

---

## A more deliberate second file

To keep the course structured, later examples get numbered filenames — e.g. `01-fastapi-foundation.py` — rather than always `main.py`. Purely a convention for organizing many small examples; nothing FastAPI-specific about the naming.

```python
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(
    title="Swiggy Order Service",
    description="""
    This is internal API for managing orders.
    It will handle creation and tracking of delivery systems.
    """,
    version="1.2.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

`FastAPI()` takes far more than just being instantiated — this is where the app's documentation metadata lives:

| Parameter | What it controls |
|---|---|
| `title` | Name shown at the top of the generated docs |
| `description` | Longer explanation, supports multiple lines via triple-quoted strings |
| `version` | Whatever versioning scheme you use — semver is typical |
| `docs_url` | Where the **Swagger** docs are served — default `/docs` |
| `redoc_url` | Where the **Redoc** docs are served — a visually fancier alternative, default `/redoc` |
| `openapi_url` | Where the raw OpenAPI schema JSON lives — some production tooling and paid platforms consume this file directly to build their own documentation UI |

There is more available beyond this — terms-of-service links, contact info, license info. The general rule: the more of this gets filled in, the more useful the documentation is for anyone else who has to integrate against the API later.

### Two routes, with docstrings

```python
@app.get("/")
def read_root():
    """
    Root endpoint - does a simple health check.
    """
    return {
        "message": "Welcome to Swiggy order service",
        "status": "healthy",
    }


@app.get("/about")
def about():
    """
    Returns API metadata.
    """
    return {
        "service": "order-service",
        "team": "backend platform",
        "region": "ap-south-1",
        "version": "1.2.2",
    }
```

The docstring convention: a short line naming the endpoint, then what it does after a dash. Not mandatory, but it becomes part of the generated documentation, so it earns its keep. `ap-south-1` here is an AWS region name, used as a stand-in for "wherever this service happens to be deployed."

Run it:

```bash
uvicorn 01-fastapi-foundation:app --reload
```

> [!question]- I wrote maybe 20-30 lines total and got two fully documented, JSON-serializing routes. Is that actually representative, or a toy-example simplification?
> It is representative — that speed is close to the entire pitch for FastAPI covered earlier. No manual JSON serialization step, no manually written docs (the `/docs` and `/redoc` pages are generated straight from the code and the docstrings), and the routing is a one-line decorator per endpoint.
>
> What is *not* shown yet: request bodies, path/query parameters, validation on incoming data, error handling, database calls. Those add real lines of code. But the baseline — stand up a route, return structured data, get documentation for free — really is close to this fast.

Visiting either route in a browser normally isn't how this gets tested in practice, though — that's what web request clients (Postman, etc.) are for, and they're where the workflow moves next.
