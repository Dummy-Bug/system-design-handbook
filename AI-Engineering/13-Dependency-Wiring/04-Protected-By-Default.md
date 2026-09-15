#dependency-injection #fastapi #security #architecture

**Who is calling is a dependency like any other.** It can be reached for or declared, exactly as a service can — and unlike a service, the choice decides what happens to a route that nobody remembered to protect.

# Protected By Default

> [!info] Two words used throughout. **Authentication** is working out who is making a request. A **header** is a labelled line a client sends alongside the URL, such as `X-Employee-Id: 1000`, which is how the examples here carry an identity.

## Who is calling is a dependency like any other

A route usually needs to know who is asking, not only what they asked for, and that identity arrives inside the request itself.

A real service reads a signed cookie or a token and verifies it. These examples use a plain header, which keeps them small; verifying it comes later.

`src/wiring_lab/note04/a_who_is_calling_is_a_dependency.py`:

```python
from typing import Annotated

from fastapi import Depends, FastAPI, Header
from fastapi.testclient import TestClient


def get_caller_id(x_employee_id: Annotated[str, Header()]) -> str:
    print(f"  provider read the header: {x_employee_id!r}")
    return x_employee_id


app = FastAPI()


@app.get("/me")
def read_me(caller_id: Annotated[str, Depends(get_caller_id)]) -> dict[str, str]:
    print(f"  route received caller_id={caller_id!r}")
    return {"you_are": caller_id}


client = TestClient(app)

print("request with the header")
response = client.get("/me", headers={"X-Employee-Id": "1000"})
print("  status ->", response.status_code, "body ->", response.json())

print("request without the header")
response = client.get("/me")
print("  status ->", response.status_code, "body ->", response.json())
```

The provider is an ordinary function, and the one new construct is `Header()`. In [[03-Declared-At-The-Door]] a provider asked for another provider; this one asks the framework for a piece of the request instead, and FastAPI matches the parameter name to the header name, so `x_employee_id` reads `X-Employee-Id`.

The route then declares the caller in exactly the way it declared a service.

```
$ uv run python src/wiring_lab/note04/a_who_is_calling_is_a_dependency.py

request with the header
  provider read the header: '1000'
  route received caller_id='1000'
  status -> 200 body -> {'you_are': '1000'}
  
request without the header
  status -> 422 body -> {'detail': [{'type': 'missing', 'loc': ['header', 'x-employee-id'], 'msg': 'Field required', 'input': None}]}
```

The second request is the one worth reading twice. **Neither print appeared.** The framework could not build `caller_id`, so it never called the route and answered by itself — the route was not consulted about a request that carried no identity.

| | A service, in the previous note | The caller, here |
|---|---|---|
| where it comes from | built once at startup, handed over by a provider | read out of this request by a provider |
| how the route asks for it | `Annotated[SalaryService, Depends(get_salary_service)]` | `Annotated[str, Depends(get_caller_id)]` |
| if the provider cannot supply it | — | the route never runs |

> [!important] Identity needs no special mechanism
> Who is calling is another input a function needs, so it can be stated on the `def` line and supplied by the framework, exactly like a service. And because the framework builds every declared input before calling the route, a request that cannot produce an identity is turned away before any of your code sees it.

## Middleware checks the path before any route runs

The other way to authenticate puts the check somewhere else entirely: in **middleware**, a function the framework runs before every request reaches a route.

```
request  ->  middleware  ->  route
             decides whether the route runs at all
```

Middleware receives the whole request, and `call_next`, which is how it says carry on to the route. Because it runs for every request, it also needs some way to tell which requests need a check — and what it has to go on is the URL.

`src/wiring_lab/note04/b_middleware_checks_the_path.py`:

```python
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()

PUBLIC_PATHS = {"/health"}


@app.middleware("http")
async def require_caller_id(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    print(f"  middleware sees path {request.url.path}")

    if request.url.path in PUBLIC_PATHS:
        print("    public, no check")
        return await call_next(request)

    if not request.headers.get("X-Employee-Id"):
        print("    no identity, refusing")
        return JSONResponse(status_code=401, content={"detail": "Who are you?"})

    print("    identity present, allowing")
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    print("  route health running")
    return {"status": "ok"}


@app.get("/salaries")
def read_salaries() -> dict[str, int]:
    print("  route read_salaries running")
    return {"salary": 900_000}


client = TestClient(app)

print("GET /health, no header")
response = client.get("/health")
print("  ->", response.status_code, response.json())

print("GET /salaries, no header")
response = client.get("/salaries")
print("  ->", response.status_code, response.json())

print("GET /salaries, with header")
response = client.get("/salaries", headers={"X-Employee-Id": "1000"})
print("  ->", response.status_code, response.json())
```

Neither route mentions identity. Neither declares a caller, and neither knows the middleware exists.

```
$ uv run python src/wiring_lab/note04/b_middleware_checks_the_path.py

GET /health, no header
  middleware sees path /health
    public, no check
  route health running
  -> 200 {'status': 'ok'}

GET /salaries, no header
  middleware sees path /salaries
    no identity, refusing
  -> 401 {'detail': 'Who are you?'}

GET /salaries, with header
  middleware sees path /salaries
    identity present, allowing
  route read_salaries running
  -> 200 {'salary': 900000}
```

It works, and the middle request is the proof: **no route ran at all.** The middleware answered 401 itself, so `read_salaries` was never called.

| | Declared on the route | Checked in middleware |
|---|---|---|
| what decides a check applies | the route's own `def` line | a path comparison, in another file |
| does the route mention identity | yes, it declares it | no |
| how many places state the rule | one per route | one, for the whole application |
| what the route receives | the caller, as an argument | nothing — the check happened elsewhere |

The third row is the appeal, and it is a real one: a single function protects everything, and no route has to remember anything.

> [!important] The middleware decides from the URL, not from the route
> Middleware can authenticate, because it runs first and can refuse. But to do that it must work out which requests need a check, and the only thing it has is the path — compared against a list that lives in a file which has never heard of the routes it is protecting.

## A path check has a default, and the default lands on every route added later

The same middleware can be written the other way round: naming the paths it **protects** rather than the ones it lets through.

`src/wiring_lab/note04/c_the_route_nobody_listed.py`:

```python
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()

PROTECTED_PREFIX = "/salaries"


@app.middleware("http")
async def require_caller_id(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path.startswith(PROTECTED_PREFIX):
        if not request.headers.get("X-Employee-Id"):
            return JSONResponse(status_code=401, content={"detail": "Who are you?"})
        return await call_next(request)

    return await call_next(request)


@app.get("/salaries")
def read_salaries() -> dict[str, int]:
    return {"salary": 900_000}


@app.get("/bonuses")
def read_bonuses() -> dict[str, int]:
    return {"bonus": 50_000}


client = TestClient(app)

print("GET /salaries, no header  (listed)")
response = client.get("/salaries")
print("  ->", response.status_code, response.json())

print("GET /bonuses,  no header  (added later, nobody updated the middleware)")
response = client.get("/bonuses")
print("  ->", response.status_code, response.json())
```

The last line of the middleware is the one that matters. It is the answer for **every path that did not match**, and the answer is: carry on to the route.

`/bonuses` is a route somebody added later. They were working on bonuses rather than on authentication, and never opened the middleware file.

```
$ uv run python src/wiring_lab/note04/c_the_route_nobody_listed.py

GET /salaries, no header  (listed)
  -> 401 {'detail': 'Who are you?'}

GET /bonuses,  no header  (added later, nobody updated the middleware)
  -> 200 {'bonus': 50000}
```

**Salaries are protected and bonuses are served to anyone.** Nothing failed, nothing warned, and the new route works exactly as its author intended — which is what makes this hard to catch, because working is how it looks in both cases.

Now change one thing: which list the middleware keeps. It names the public paths, and everything else needs a check. The routes are identical, and nobody updates the middleware here either.

`src/wiring_lab/note04/d_deny_by_default.py`:

```python
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()

PUBLIC_PATHS = {"/health"}


@app.middleware("http")
async def require_caller_id(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    if not request.headers.get("X-Employee-Id"):
        return JSONResponse(status_code=401, content={"detail": "Who are you?"})

    return await call_next(request)


@app.get("/salaries")
def read_salaries() -> dict[str, int]:
    return {"salary": 900_000}


@app.get("/bonuses")
def read_bonuses() -> dict[str, int]:
    return {"bonus": 50_000}


client = TestClient(app)

print("GET /salaries, no header  (protected)")
response = client.get("/salaries")
print("  ->", response.status_code, response.json())

print("GET /bonuses,  no header  (added later, still nobody updated the middleware)")
response = client.get("/bonuses")
print("  ->", response.status_code, response.json())
```

```
$ uv run python src/wiring_lab/note04/d_deny_by_default.py

GET /salaries, no header  (protected)
  -> 401 {'detail': 'Who are you?'}

GET /bonuses,  no header  (added later, still nobody updated the middleware)
  -> 401 {'detail': 'Who are you?'}
```

| The route nobody listed | Middleware lists the protected paths | Middleware lists the public paths |
|---|---|---|
| what happens to it | served to anyone | refused |
| how the mistake surfaces | somebody reads the middleware, or somebody exploits it | the first request to it fails |
| what the mistake costs | data exposed, with no signal | a route that does not work until it is added to the list |

Both defaults produce mistakes, and the difference is which kind. One is found in minutes by the person who wrote the route; the other may not be found at all.

> [!warning] Every unlisted path gets the same answer, and that answer was chosen once
> A path comparison must decide something about paths it does not recognise, and whatever it decides applies to every route anybody adds afterwards. Listing the protected paths means a new route is open by default. Listing the public ones means a new route is closed by default. Neither list is checked against the routes that actually exist.

## Attach the check to the router, and protection follows the route

The check itself needs nothing new — it is the provider from the first section, which reads the header and returns the caller. What is new is `APIRouter`: a group of routes, which can carry dependencies that apply to every route registered on it.

`src/wiring_lab/note04/e_protection_follows_the_router.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header
from fastapi.testclient import TestClient


def require_caller_id(x_employee_id: Annotated[str, Header()]) -> str:
    print(f"  check ran, caller {x_employee_id!r}")
    return x_employee_id


public = APIRouter()
protected = APIRouter(dependencies=[Depends(require_caller_id)])


@public.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@protected.get("/salaries")
def read_salaries() -> dict[str, int]:
    return {"salary": 900_000}


@protected.get("/bonuses")
def read_bonuses() -> dict[str, int]:
    return {"bonus": 50_000}


app = FastAPI()
app.include_router(public)
app.include_router(protected)

client = TestClient(app)

print("GET /health, no header")
response = client.get("/health")
print("  ->", response.status_code, response.json())

print("GET /salaries, no header")
response = client.get("/salaries")
print("  ->", response.status_code, response.json())

print("GET /bonuses, no header  (added later, nobody touched the auth code)")
response = client.get("/bonuses")
print("  ->", response.status_code, response.json())

print("GET /bonuses, with header")
response = client.get("/bonuses", headers={"X-Employee-Id": "1000"})
print("  ->", response.status_code, response.json())
```

`/bonuses` is the route that went unprotected in the previous section. Here nobody had to remember it: it was registered on the protected router because it reads employee money, and that decision is the protection.

```
$ uv run python src/wiring_lab/note04/e_protection_follows_the_router.py

GET /health, no header
  -> 200 {'status': 'ok'}

GET /salaries, no header
  -> 422 {'detail': [{'type': 'missing', 'loc': ['header', 'x-employee-id'], 'msg': 'Field required', 'input': None}]}

GET /bonuses, no header  (added later, nobody touched the auth code)
  -> 422 {'detail': [{'type': 'missing', 'loc': ['header', 'x-employee-id'], 'msg': 'Field required', 'input': None}]}

GET /bonuses, with header
  check ran, caller '1000'
  -> 200 {'bonus': 50000}
```

The third request is the one that went wrong before: the same route, the same forgetful author, the opposite outcome. And no route body mentions the check — `require_caller_id` appears on exactly one line in the whole file, the one that creates the router.

| | A path list in middleware | A dependency on the router |
|---|---|---|
| what makes a route protected | its URL appears in, or misses, a list | which router it was registered on |
| where that fact is written down | a file that does not know the routes | the line that declares the route |
| a route added without thinking about identity | gets whatever the default is | gets its router's protection |
| checking whether one route is protected | read the list, then match the URL by eye | read the decorator above it |

> [!important] Protection becomes a property of where the route lives
> The question changes from did anybody add this path to the list, asked later by somebody reviewing the middleware, to which router does this route belong on, asked as the route is written, by the person writing it. Nothing has to be remembered afterwards, because nothing was left for afterwards.

One honest detail in the output: the refusal is a 422 rather than a 401, because the framework is reporting a missing required input rather than refusing a caller. The next section replaces the check with one that decides for itself what to say.

## A check that decides for itself what to say

The provider so far only read the header and handed it on, so anything wrong with the header was the framework's business — which is why a missing one came back as a complaint about a required field.

Making the header optional takes that decision back. `str | None` with a default of `None` means the framework hands over `None` instead of refusing, and the function has both cases to answer for. A dependency can raise `HTTPException` to end the request there, and this one does.

`src/wiring_lab/note04/f_a_real_check.py`:

```python
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

KNOWN_EMPLOYEES = {"1000", "1001"}


def require_caller_id(x_employee_id: Annotated[str | None, Header()] = None) -> str:
    if x_employee_id is None:
        print("  refusing: no identity")
        raise HTTPException(status_code=401, detail="Who are you?")

    if x_employee_id not in KNOWN_EMPLOYEES:
        print(f"  refusing: {x_employee_id!r} is not an employee")
        raise HTTPException(status_code=401, detail="Who are you?")

    print(f"  allowing: caller {x_employee_id!r}")
    return x_employee_id


protected = APIRouter(dependencies=[Depends(require_caller_id)])


@protected.get("/salaries")
def read_salaries() -> dict[str, int]:
    print("  route read_salaries running")
    return {"salary": 900_000}


app = FastAPI()
app.include_router(protected)

client = TestClient(app)

print("GET /salaries, no header")
response = client.get("/salaries")
print("  ->", response.status_code, response.json())

print("GET /salaries, header 9999")
response = client.get("/salaries", headers={"X-Employee-Id": "9999"})
print("  ->", response.status_code, response.json())

print("GET /salaries, header 1000")
response = client.get("/salaries", headers={"X-Employee-Id": "1000"})
print("  ->", response.status_code, response.json())
```

The second check is the one the previous version could not make at all. A header that is present but names somebody who does not exist is not a missing input — it is a wrong answer, and only a real check can tell those apart. In a real service `KNOWN_EMPLOYEES` is a signed cookie or a token being verified; the shape of the function stays exactly this.

The router and the route are unchanged.

```
$ uv run python src/wiring_lab/note04/f_a_real_check.py

GET /salaries, no header
  refusing: no identity
  -> 401 {'detail': 'Who are you?'}

GET /salaries, header 9999
  refusing: '9999' is not an employee
  -> 401 {'detail': 'Who are you?'}

GET /salaries, header 1000
  allowing: caller '1000'
  route read_salaries running
  -> 200 {'salary': 900000}
```

`route read_salaries running` appears once, on the third request.

| Request | What the check found | Status | Did the route run |
|---|---|---|---|
| no header | nothing identifying the caller | 401 | no |
| `X-Employee-Id: 9999` | an identity that is not one of ours | 401 | no |
| `X-Employee-Id: 1000` | a known employee | 200 | yes |

Both refusals say the same thing to the client, which is deliberate. Telling an unknown caller that `1000` would have worked is telling them which identities to try.

| | The provider returns the header | The check raises |
|---|---|---|
| identity missing | the framework's wording about a required field | a 401 in your own words |
| identity present but invalid | **accepted** — nothing examines the value | 401 |
| who decides what the client is told | the framework | the check |

> [!important] A dependency can refuse, not only supply
> Once who-is-calling is declared like any other input, the function supplying it can do the whole job: read the request, decide, and raise to end it. Because it hangs on the router rather than on each route, every route in that group is covered by a decision none of them can see, and a route never has to handle a caller the check has already turned away.

## What middleware keeps once the check has moved

With the check on the router, middleware is left with the work that has nothing to do with any particular route. Giving every request an id is the clearest example: a short unique string that identifies this one request in the logs and goes back to the client, so a bug report can name it.

`src/wiring_lab/note04/g_what_middleware_keeps.py`:

```python
import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    Response,
)
from fastapi.testclient import TestClient

KNOWN_EMPLOYEES = {"1000"}


def require_caller_id(x_employee_id: Annotated[str | None, Header()] = None) -> str:
    if x_employee_id not in KNOWN_EMPLOYEES:
        raise HTTPException(status_code=401, detail="Who are you?")
    return x_employee_id


app = FastAPI()


@app.middleware("http")
async def add_request_id(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = str(uuid.uuid4())[:8]
    print(f"  middleware: start {request_id} {request.method} {request.url.path}")

    response = await call_next(request)

    print(f"  middleware: done  {request_id} status {response.status_code}")
    response.headers["X-Request-Id"] = request_id
    return response


public = APIRouter()
protected = APIRouter(dependencies=[Depends(require_caller_id)])


@public.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@protected.get("/salaries")
def read_salaries() -> dict[str, int]:
    return {"salary": 900_000}


app.include_router(public)
app.include_router(protected)

client = TestClient(app)

print("GET /health, no header")
response = client.get("/health")
print("  ->", response.status_code, "id:", response.headers.get("X-Request-Id"))

print("GET /salaries, no header")
response = client.get("/salaries")
print("  ->", response.status_code, "id:", response.headers.get("X-Request-Id"))

print("GET /salaries, header 1000")
response = client.get("/salaries", headers={"X-Employee-Id": "1000"})
print("  ->", response.status_code, "id:", response.headers.get("X-Request-Id"))
```

One thing about the shape is new. Every middleware in the earlier sections ended at `call_next`; this one keeps the result and carries on, so its last three lines run **after** the route has produced an answer. That is what lets it report the status and attach a header to the response.

```
$ uv run python src/wiring_lab/note04/g_what_middleware_keeps.py

GET /health, no header
  middleware: start eaaeca27 GET /health
  middleware: done  eaaeca27 status 200
  -> 200 id: eaaeca27

GET /salaries, no header
  middleware: start dcd30103 GET /salaries
  middleware: done  dcd30103 status 401
  -> 401 id: dcd30103

GET /salaries, header 1000
  middleware: start dff5e2be GET /salaries
  middleware: done  dff5e2be status 200
  -> 200 id: dff5e2be
```

The middle request is the one worth noticing. It was refused by the router's check, and the middleware still logged it and still put an id on the response — a refused request is exactly the one somebody will want to find in the logs later.

The middleware does read the path, but only to print it; it never branches on it. That distinction is the test for what belongs here:

| The work | Does it need to know which route this is | Where it belongs |
|---|---|---|
| generating a request id | no — every request gets one | middleware |
| logging the method, path and status | no — every request has them | middleware |
| attaching `X-Request-Id` to the response | no | middleware |
| deciding whether this caller may proceed | **yes** — the answer differs per route | the router |

Printing the path describes the request. Branching on the path makes a decision the route should have made.

| | Check in middleware | Check on the router |
|---|---|---|
| middleware holds | a path list and an authentication decision | a request id and logging |
| the router holds | nothing | the authentication decision |
| a newly added route is | open or closed by default, whichever the list chose | protected by the router it was added to |

> [!important] The test for middleware is whether it needs to know the route
> Middleware is the right place for work that is identical for every request and needs no knowledge of routes. As soon as a middleware has to ask which route this is, it is making a decision that belongs with the route — and that question is how a path list, and a default for everything not on it, gets introduced.
