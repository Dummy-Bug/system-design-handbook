#dependency-injection #fastapi #python #architecture

**In a web service, your code does not call your route functions — the framework does.** A request arrives, and the framework decides which function to run and what to pass it. That makes the framework the one piece of code standing exactly where a request turns into a function call, and so the natural place to hand a function what it needs.

# Declared At The Door

> [!info] Two words used throughout. A **route** is a function the framework calls when an incoming request's URL matches a pattern attached to it. A **collaborator**, as in [[01-Hidden-Inputs]], is anything a function uses without having made it itself — here, a service object.

## The framework calls your function, so it chooses the arguments

`src/wiring_lab/note03/a_the_framework_is_the_caller.py`:

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient


class SalaryService:
    def __init__(self, salaries: dict[str, int]) -> None:
        self.salaries = salaries

    def salary_for(self, employee_id: str) -> int:
        return self.salaries[employee_id]


salary_service = SalaryService(salaries={"1000": 900_000})

app = FastAPI()


@app.get("/salaries/{employee_id}")
def get_salary(employee_id: str) -> dict[str, int]:
    print(f"framework called get_salary(employee_id={employee_id!r})")
    return {"salary": salary_service.salary_for(employee_id)}


client = TestClient(app)
response = client.get("/salaries/1000")
print("status ->", response.status_code)
print("body   ->", response.json())
```

`TestClient` sends a request to the app inside the same program, so the example needs no running server. The request is for the URL `/salaries/1000`.

```
$ uv run python src/wiring_lab/note03/a_the_framework_is_the_caller.py

framework called get_salary(employee_id='1000')
status -> 200
body   -> {'salary': 900000}
```

**No line in the file calls `get_salary`.** The request names a URL, not a function. The framework matched that URL against the pattern `/salaries/{employee_id}`, took `"1000"` out of it, and called `get_salary(employee_id="1000")` itself — the first line of output is the function reporting that it was called, and with what.

Asking the question from [[01-Hidden-Inputs]] of this route — what does it need, and who supplies each thing:

| What `get_salary` needs | Who supplies it |
|---|---|
| `employee_id` | **the framework**, taken out of the URL and passed as an argument |
| `salary_service` | **nobody** — the function reaches for the module-level object, a hidden input |

The framework already chooses one of the function's arguments. The other is fetched by the function from a shared place, exactly the pattern the earlier notes took apart.

> [!important] The framework already stands between the request and your function
> It is the caller, so it decides what the function receives. Handing over one value from the URL is something it does already; handing over the collaborators a function needs is the same job, done by the same piece of code, at the same moment.

## The route declares the service, and the framework fetches it

FastAPI lets a route list a collaborator on its `def` line and name a **provider** for it — an ordinary function whose only job is to return one. The framework calls the provider and passes the result in.

`src/wiring_lab/note03/b_the_framework_supplies_it.py`:

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class SalaryService:
    def __init__(self, salaries: dict[str, int]) -> None:
        self.salaries = salaries

    def salary_for(self, employee_id: str) -> int:
        return self.salaries[employee_id]


startup_salary_service = SalaryService(salaries={"1000": 900_000})


def get_salary_service() -> SalaryService:
    print("framework called get_salary_service()")
    return startup_salary_service


app = FastAPI()


@app.get("/salaries/{employee_id}")
def get_salary(
    employee_id: str,
    salary_service: Annotated[SalaryService, Depends(get_salary_service)],
) -> dict[str, int]:
    print(f"framework called get_salary(employee_id={employee_id!r})")
    print("  same object built at startup:", salary_service is startup_salary_service)
    return {"salary": salary_service.salary_for(employee_id)}


client = TestClient(app)
response = client.get("/salaries/1000")
print("status ->", response.status_code)
print("body   ->", response.json())
```

The one new construct is the second parameter's annotation. It says two things at once:

| Part of `Annotated[SalaryService, Depends(get_salary_service)]` | What it tells the reader and the framework |
|---|---|
| `SalaryService` | what the parameter is |
| `Depends(get_salary_service)` | how the framework gets one: by calling `get_salary_service` |

`Depends` is handed the function itself, without parentheses. No line in the file calls `get_salary_service`, just as no line calls `get_salary`.

```
$ uv run python src/wiring_lab/note03/b_the_framework_supplies_it.py

framework called get_salary_service()
framework called get_salary(employee_id='1000')
  same object built at startup: True
status -> 200
body   -> {'salary': 900000}
```

The output gives the order. The framework called the provider first, then called the route with the provider's result as `salary_service` — and that argument is the very object built when the program started.

The same question as before, what the route needs and who supplies it, now has a different answer in its second row:

| What `get_salary` needs | Reaching for it, the previous section | Declaring it, this section |
|---|---|---|
| `employee_id` | the framework, taken from the URL | the framework, taken from the URL |
| `salary_service` | **nobody** — the route fetched a module-level object | **the framework**, by calling the provider named on the `def` line |

The route now states everything it needs on its `def` line, and never learns where the service came from.

> [!note] The reaching moved rather than disappeared
> `get_salary_service` still returns a module-level object. What changed is where that lookup lives: out of the route, and into one small function whose only job is handing the service out. That is the function a test replaces — and replacing it changes nothing about the route.

## A provider can ask for a provider

[[02-Composition-Root]] ended with one `Services` dataclass holding every service, built once when the program starts. A route that only needs the salary service should not have to know that bundle exists. So there are two providers here, and the second asks for the first on its own `def` line, in exactly the way a route asks for a provider.

`src/wiring_lab/note03/c_providers_ask_for_providers.py`:

```python
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class SalaryService:
    def salary_for(self, employee_id: str) -> int:
        return {"1000": 900_000}[employee_id]


class LeaveService:
    def leave_balance_for(self, employee_id: str) -> int:
        return {"1000": 12}[employee_id]


@dataclass
class Services:
    salary: SalaryService
    leave: LeaveService


startup_services = Services(salary=SalaryService(), leave=LeaveService())


def get_services() -> Services:
    print("framework called get_services()")
    return startup_services


def get_salary_service(
    services: Annotated[Services, Depends(get_services)],
) -> SalaryService:
    print("framework called get_salary_service(services=...)")
    return services.salary


app = FastAPI()


@app.get("/salaries/{employee_id}")
def get_salary(
    employee_id: str,
    salary_service: Annotated[SalaryService, Depends(get_salary_service)],
) -> dict[str, int]:
    print(f"framework called get_salary(employee_id={employee_id!r})")
    return {"salary": salary_service.salary_for(employee_id)}


client = TestClient(app)
response = client.get("/salaries/1000")
print("status ->", response.status_code)
print("body   ->", response.json())
```

```
$ uv run python src/wiring_lab/note03/c_providers_ask_for_providers.py

framework called get_services()
framework called get_salary_service(services=...)
framework called get_salary(employee_id='1000')
status -> 200
body   -> {'salary': 900000}
```

The request was for the route. To call the route the framework needs a salary service, so it reads `get_salary_service`'s `def` line and finds that it needs a `Services` bundle from `get_services`. It then calls the functions in the reverse of the order it discovered them, starting with the one that needs nothing.

```mermaid
flowchart LR
    R["get_salary<br/>the route"] -- needs --> S["get_salary_service"]
    S -- needs --> B["get_services"]
    B -- needs --> N["nothing"]
    B -. "called 1st" .-> S
    S -. "called 2nd" .-> R
    style R fill:#1f6feb,color:#fff
    style S fill:#8957e5,color:#fff
    style B fill:#238636,color:#fff
    style N fill:#6e7681,color:#fff
```

Ask each function what it knows about:

| Function | What it asks for | What it has never heard of |
|---|---|---|
| `get_services` | nothing | the salary provider, the route |
| `get_salary_service` | a `Services` bundle from `get_services` | the route, and where the bundle was built |
| `get_salary` | a `SalaryService` from `get_salary_service` | `get_services`, `Services`, `startup_services` |

The route has no idea that a bundle of services exists. `get_salary_service` has no idea where that bundle came from. Each link knows only the one directly before it, and the framework is the only thing that sees the whole chain.

> [!important] Providers chain, so each link changes alone
> A provider declares what it needs in the same way a route does, which lets providers ask for other providers. The framework follows the declarations backwards from the route and assembles the chain on each request. Changing where the `Services` bundle comes from is an edit to `get_services` and to nothing else in the chain.

## A provider that yields can clean up — if the cleanup is in a finally

Some things are opened for a single request and have to be closed when it is over: a database session, a connection borrowed from a pool. `SalarySession` below stands in for one, and prints when it opens and when it closes.

A provider that **returns** its object has nowhere to put the closing. A provider that **yields** does. The framework runs the provider up to the `yield`, hands the yielded object to the route, and pauses the provider there; once the route has finished, it resumes the provider and the lines after the `yield` run. `Iterator[SalarySession]` is how a function that yields a `SalarySession` is annotated.

`src/wiring_lab/note03/d_yield_without_finally.py`:

```python
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class SalarySession:
    def __init__(self) -> None:
        print("  session opened")

    def salary_for(self, employee_id: str) -> int:
        return {"1000": 900_000}[employee_id]

    def close(self) -> None:
        print("  session closed")


def get_session() -> Iterator[SalarySession]:
    session = SalarySession()
    yield session
    session.close()


app = FastAPI()


@app.get("/salaries/{employee_id}")
def get_salary(
    employee_id: str,
    session: Annotated[SalarySession, Depends(get_session)],
) -> dict[str, int]:
    print(f"  route running for {employee_id}")
    return {"salary": session.salary_for(employee_id)}


client = TestClient(app, raise_server_exceptions=False)

print("request for 1000")
response = client.get("/salaries/1000")
print("  client got", response.status_code)

print("request for 9999, which the route cannot find")
response = client.get("/salaries/9999")
print("  client got", response.status_code)
```

Two requests are sent. The second asks for an employee that does not exist, so `salary_for` raises a `KeyError` and the framework answers with a 500. `raise_server_exceptions=False` makes `TestClient` hand back that 500 instead of re-raising the error inside the script.

```
$ uv run python src/wiring_lab/note03/d_yield_without_finally.py

request for 1000
  session opened
  route running for 1000
  session closed
  client got 200
request for 9999, which the route cannot find
  session opened
  route running for 9999
  client got 500
```

The first request opens, runs the route, and closes. **The second opens a session and never closes it.** When the route raised, the error was sent back into the provider at the paused `yield`, and like any error it skipped every line after the point where it arrived — including `session.close()`.

The fix is a `finally` block, which runs whether the code above it succeeded or raised. Nothing else in the file changes.

`src/wiring_lab/note03/e_yield_with_finally.py`:

```python
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class SalarySession:
    def __init__(self) -> None:
        print("  session opened")

    def salary_for(self, employee_id: str) -> int:
        return {"1000": 900_000}[employee_id]

    def close(self) -> None:
        print("  session closed")


def get_session() -> Iterator[SalarySession]:
    session = SalarySession()
    try:
        yield session
    finally:
        session.close()


app = FastAPI()


@app.get("/salaries/{employee_id}")
def get_salary(
    employee_id: str,
    session: Annotated[SalarySession, Depends(get_session)],
) -> dict[str, int]:
    print(f"  route running for {employee_id}")
    return {"salary": session.salary_for(employee_id)}


client = TestClient(app, raise_server_exceptions=False)

print("request for 1000")
response = client.get("/salaries/1000")
print("  client got", response.status_code)

print("request for 9999, which the route cannot find")
response = client.get("/salaries/9999")
print("  client got", response.status_code)
```

```
$ uv run python src/wiring_lab/note03/e_yield_with_finally.py

request for 1000
  session opened
  route running for 1000
  session closed
  client got 200
request for 9999, which the route cannot find
  session opened
  route running for 9999
  session closed
  client got 500
```

| What the route did | Close written plainly after `yield` | Close inside `finally` |
|---|---|---|
| succeeded | closed | closed |
| raised | **never closed** | closed |

In both files, on the requests where the close ran, `session closed` is printed before `client got` — the cleanup had finished before the client received its response.

> [!warning] A plain close after yield leaks on every failed request
> Code written after the `yield` runs only when the route succeeds. A route that raises sends its error into the provider at the `yield`, and the close never happens — one open session left behind per failed request, with nothing on the happy path to suggest it. The close belongs in `finally`, where it runs either way.

## Replace the provider, and the route receives a different service

The route below is the one from the section that introduced providers, unchanged. What is new is a second provider meant for a test, which returns a `SalaryService` built with test data, and `app.dependency_overrides` — a plain dictionary on the app whose key is the provider a route asks for and whose value is the provider to call in its place.

`src/wiring_lab/note03/f_override_the_provider.py`:

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class SalaryService:
    def __init__(self, salaries: dict[str, int]) -> None:
        self.salaries = salaries

    def salary_for(self, employee_id: str) -> int:
        return self.salaries[employee_id]


startup_salary_service = SalaryService(salaries={"1000": 900_000})


def get_salary_service() -> SalaryService:
    return startup_salary_service


app = FastAPI()


@app.get("/salaries/{employee_id}")
def get_salary(
    employee_id: str,
    salary_service: Annotated[SalaryService, Depends(get_salary_service)],
) -> dict[str, int]:
    return {"salary": salary_service.salary_for(employee_id)}


def get_test_salary_service() -> SalaryService:
    return SalaryService(salaries={"1000": 1})


client = TestClient(app)
print("real provider        ->", client.get("/salaries/1000").json())

app.dependency_overrides[get_salary_service] = get_test_salary_service
print("provider overridden  ->", client.get("/salaries/1000").json())

app.dependency_overrides.clear()
print("override cleared     ->", client.get("/salaries/1000").json())
```

```
$ uv run python src/wiring_lab/note03/f_override_the_provider.py

real provider        -> {'salary': 900000}
provider overridden  -> {'salary': 1}
override cleared     -> {'salary': 900000}
```

The same URL, requested three times, gives three answers:

| Moment | Which provider the framework calls | Salary returned |
|---|---|---|
| no override | `get_salary_service` | `900000` |
| override set | `get_test_salary_service` | `1` |
| override cleared | `get_salary_service` | `900000` |

The route's code is identical in all three, and it cannot tell the difference. It asks for a `SalaryService` from `get_salary_service`; the framework checks `dependency_overrides` before deciding which function to actually run. The override here is set after the client was already created, and it still takes effect on the next request.

Compare what supplying test data took with a hidden input, as in [[01-Hidden-Inputs]], and what it takes with a declared provider:

| To give the route test data | A hidden, module-level input | A declared provider |
|---|---|---|
| what changes | the shared object, which must then be put back by hand | one dictionary entry |
| does the route's code change | no — but its hidden input is swapped out from under it | no — its declared input is swapped openly |
| undoing it | restoring the shared object | `dependency_overrides.clear()` |
| where the swap is visible | nowhere near the route | on the line that sets the override |

> [!important] The declaration is the test seam
> The same `def` line that lets the framework supply a service is what lets a test supply a different one. Because the route names a provider instead of reaching for an object, replacing that provider changes what every route using it receives — without editing any route, and without the route being able to tell.

## Declared in three places, built once per request

Providers chain, so the same dependency can easily be declared by more than one of them in a single request. Here a per-request `Session` is needed by two readers, each reader's provider declares `get_session`, and the route declares both readers and a session directly.

`src/wiring_lab/note03/g_built_once_per_request.py`:

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class Session:
    def __init__(self) -> None:
        print("  session opened")


class SalaryReader:
    def __init__(self, session: Session) -> None:
        self.session = session


class LeaveReader:
    def __init__(self, session: Session) -> None:
        self.session = session


def get_session() -> Session:
    return Session()


def get_salary_reader(
    session: Annotated[Session, Depends(get_session)],
) -> SalaryReader:
    return SalaryReader(session)


def get_leave_reader(
    session: Annotated[Session, Depends(get_session)],
) -> LeaveReader:
    return LeaveReader(session)


app = FastAPI()


@app.get("/summary")
def get_summary(
    salary: Annotated[SalaryReader, Depends(get_salary_reader)],
    leave: Annotated[LeaveReader, Depends(get_leave_reader)],
    session: Annotated[Session, Depends(get_session)],
) -> dict[str, bool]:
    return {"one_session": salary.session is leave.session is session}


client = TestClient(app)

print("first request")
print("  body ->", client.get("/summary").json())

print("second request")
print("  body ->", client.get("/summary").json())
```

`Depends(get_session)` appears three times: in `get_salary_reader`, in `get_leave_reader`, and in the route. The route's answer checks whether the session held by each reader and the session it received itself are one and the same object.

```
$ uv run python src/wiring_lab/note03/g_built_once_per_request.py

first request
  session opened
  body -> {'one_session': True}
second request
  session opened
  body -> {'one_session': True}
```

Each request printed `session opened` once, **and each time all three places held the same session.** Within a request the framework calls a provider the first time it is needed, keeps the result, and hands that same result to every other place that declared it. The second request started over and opened a fresh session.

| Where `get_session` is declared | Sessions if each declaration built its own | Sessions built, as run |
|---|---|---|
| once, in one request | 1 | 1 |
| three times, in one request | 3 | **1** |
| three times, over two requests | 6 | **2** |

For a database session this is the behaviour wanted: both readers work inside one session and so see one transaction, and the request opens one connection rather than three.

> [!important] Declaring a dependency again costs nothing within a request
> A provider's result is settled for the rest of the request the first time the framework builds it. However many providers and routes declare the same dependency, it is built once and shared — so each piece of code can declare exactly what it needs, without worrying that doing so creates duplicates.

## It reaches only as far as the framework's own calls

Everything in this note has depended on one fact from its first section: the framework is the caller. That is also the limit. A declaration is an instruction to the framework, and an instruction only has effect where the framework is the one making the call.

The function below is declared exactly like every route so far, and is called twice — once through a request, and once directly by the file's own last line.

`src/wiring_lab/note03/h_only_where_the_framework_calls.py`:

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


class SalaryService:
    def __init__(self, salaries: dict[str, int]) -> None:
        self.salaries = salaries

    def salary_for(self, employee_id: str) -> int:
        return self.salaries[employee_id]


startup_salary_service = SalaryService(salaries={"1000": 900_000})


def get_salary_service() -> SalaryService:
    return startup_salary_service


app = FastAPI()


@app.get("/salaries/{employee_id}")
def get_salary(
    employee_id: str,
    salary_service: Annotated[SalaryService, Depends(get_salary_service)],
) -> dict[str, int]:
    return {"salary": salary_service.salary_for(employee_id)}


client = TestClient(app)
print("called by the framework ->", client.get("/salaries/1000").json())
print("called by our own code  ->", get_salary(employee_id="1000"))
```

The type checker rejects the direct call before anything runs:

```
$ uv run ty check src/wiring_lab/note03/h_only_where_the_framework_calls.py

error[missing-argument]: No argument provided for required parameter `salary_service` of function `get_salary`
  --> src/wiring_lab/note03/h_only_where_the_framework_calls.py:55:37
   |
55 | print("called by our own code  ->", get_salary(employee_id="1000"))
   |                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
info: Parameter declared here
  --> src/wiring_lab/note03/h_only_where_the_framework_calls.py:48:5
   |
48 |     salary_service: Annotated[SalaryService, Depends(get_salary_service)],
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Found 1 diagnostic
```

Running it anyway shows both halves in one go:

```
$ uv run python src/wiring_lab/note03/h_only_where_the_framework_calls.py

called by the framework -> {'salary': 900000}
Traceback (most recent call last):
  File "/Users/home/Desktop/projects/wiring-lab/src/wiring_lab/note03/h_only_where_the_framework_calls.py", line 55, in <module>
    print("called by our own code  ->", get_salary(employee_id="1000"))
                                        ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
TypeError: get_salary() missing 1 required positional argument: 'salary_service'
```

The same function, with the same declaration, in the same file:

| Who calls `get_salary` | What supplies `salary_service` | Result |
|---|---|---|
| the framework, through a request | the framework, by calling the provider named in the declaration | `{'salary': 900000}` |
| our own code, directly | **nothing** — `Depends` is an instruction to the framework, and the framework is not involved | `TypeError`, the argument is simply missing |

`Depends(get_salary_service)` is not machinery attached to the function. It is a note left for the framework, read when the framework prepares a call. Call the function yourself and the note is just an unread annotation, so the parameter is an ordinary required argument that nobody passed.

> [!important] Two boundaries, and this note covered one
> Everything here works because a request arrives at a route the framework calls. An agent's tools are called by the model's loop instead, so nothing a route declared ever reaches them, and `Depends` cannot cross that gap — which is exactly the situation the last row of the table shows.
>
> The identity a tool needs still starts in the HTTP request, where only a route can read it. So the second boundary is not an alternative to this one: the route receives the caller and the services here, and something else has to carry them from there into the tools.
