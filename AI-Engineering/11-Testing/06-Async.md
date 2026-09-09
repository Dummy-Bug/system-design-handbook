#testing #pytest #async #anyio #fastapi

**A test calls the function, asserts on what comes back, and passes — while the function never ran.** No mock, no weak assertion, nothing that looks like a mistake. Async code opens a fourth door into the vacuous test, and it is the only one that looks exactly like a correct test.

# Async Changes The Rules

> [!info] Calling an `async def` function does not run it. It builds a coroutine object, which is truthy, and the body waits for something to await it — so a synchronous test can assert on the result of a function that never executed.

## The test that passes without running anything

```python
# payroll.py
async def fetch_monthly_pay(teacher_id):
    return 5000
```

```python
# test_payroll.py
def test_pay_is_returned():
    result = fetch_monthly_pay(7)
    assert result
```

```
1 passed, 1 warning in 0.01s
```

Now empty the function.

```python
async def fetch_monthly_pay(teacher_id):
    pass
```

```
.                                                                        [100%]
1 passed in 0.00s
```

Still green.

### What result actually was

```python
def test_what_is_it():
    result = fetch_monthly_pay(7)
    print(type(result), result, bool(result), result == 5000)
```

```
type : <class 'coroutine'>
value: <coroutine object fetch_monthly_pay at 0x106ee6ec0>
bool : True
== 5000? False
```

**Calling an `async def` function does not run it.** It builds a coroutine object and hands that back; the body does not execute until something awaits it.

```python
result = fetch_monthly_pay(7)     # a coroutine, not 5000
assert result                     # every coroutine object is truthy
```

The assertion asks whether an object is truthy, and it always is. So the test passes whatever the function contains, including nothing.

> This is the vacuous test through a fourth door, and the worst of the four — because **nothing about the test looks wrong**. No mock, no obviously weak assertion, no empty loop. The function was called and the result was asserted on, which is what a test is supposed to do.

---

## Python did notice

```
RuntimeWarning: coroutine 'fetch_monthly_pay' was never awaited
```

It always notices. But look at where that lands — in the warnings summary at the foot of the report, under `1 passed, 1 warning`.

On a real suite carrying forty accumulated warnings about deprecated libraries, nobody reads it. Which is the cry-wolf mechanism again: a signal buried in noise has stopped being a signal.

> **Warnings in a suite are worth keeping at zero**, for the same reason flaky tests are worth fixing. A warning nobody reads cannot warn anybody, and this is the one it will be hiding behind.

One other thing would have caught it.

```python
assert result == 5000      # a coroutine does not equal 5000
```

> Which is the earlier rule in new clothes: **assert on the value, not on the truthiness.**

---

## The fix needs something pytest does not have

Awaiting requires being inside an async function, and a test function is not one by default.

```python
async def test_pay_is_returned():
    result = await fetch_monthly_pay(7)
    assert result == 5000
```

```
async def functions are not natively supported.
You need to install a suitable plugin for your async framework, for example:
  - anyio
  - pytest-asyncio
  - pytest-tornasync
  - pytest-trio
  - pytest-twisted

FAILED test_payroll.py::test_pay_is_returned - Failed: async def functions ar...
1 failed in 0.00s
```

**This failure is the good outcome.** It is loud, it names the problem, and it lists the fixes. Compare it with the silent pass at the top of this note — the same mistake, caught here and invisible there, and the only difference is that the test was honest about being async.

Running a coroutine needs an **event loop**, and pytest does not supply one. Something else has to.

---

## Two plugins, and it is a choice rather than an accumulation

| | `pytest-asyncio` | anyio's plugin |
|---|---|---|
| Ships as | its own package | **part of `anyio` itself** |
| Marker | `@pytest.mark.asyncio` | `@pytest.mark.anyio` |
| Backends | asyncio only | asyncio and Trio |
| Adoption | the more widely used of the two | standard in the FastAPI and Starlette world |

`pytest-asyncio` is the more popular package overall, and for plain asyncio code with no web framework in it, the lower-friction choice.

**FastAPI's own documentation uses anyio and never mentions `pytest-asyncio` once.** Its async-testing page is written entirely around the other marker.

```python
@pytest.mark.anyio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
```

Note it also uses `AsyncClient` with `ASGITransport` rather than `TestClient`. That belongs to the FastAPI note, and it is worth seeing early.

### They conflict

`pytest-asyncio` in **auto mode** breaks the anyio plugin in the same session. AnyIO's own documentation says so, and names the fix: remove `asyncio_mode` from the pytest configuration so `pytest-asyncio` stays in its default strict mode.

> **Installing both and hoping is the one path that does not work.** Pick one.

### Three things that settle it for ASGI code

**Starlette is built on anyio**, not on asyncio directly. The framework already made this choice.

**`pytest-asyncio` cannot drive `TaskGroup` or `CancelScope`.** A Starlette request handler runs inside an anyio task group, and anyio cancel scopes are level-triggered — which is why an unshielded write in a `finally` block is lost on a single ordinary client disconnect. Testing behaviour like that **requires** the anyio plugin; it is not merely more convenient.

**It is already installed.** `anyio` arrives with FastAPI through Starlette, so choosing it adds no dependency at all.

---

## The smallest async test that works

```python
import pytest

from python_lab.payroll import fetch_monthly_pay


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_pay_is_returned():
    result = await fetch_monthly_pay(7)
    assert result == 5000
```

```
..                                                                       [100%]
2 passed in 0.01s
```

Three pieces are doing work.

| Piece                   | Job                                              |
| ----------------------- | ------------------------------------------------ |
| `@pytest.mark.anyio`    | this test needs an event loop, please supply one |
| `anyio_backend` fixture | **which** event loop                             |
| `await`                 | actually runs the coroutine                      |

---

## What an event loop is, and why anyio has to ask

An `async def` function does not run itself. Something has to take the coroutine, start it, pause it when it reaches an `await`, run something else meanwhile, and come back to it. **That something is the event loop.**

Python ships one, called **asyncio**. There is also a well-regarded alternative called **Trio** — a different library with a different design, not a version of asyncio.

**anyio is a layer that runs on top of either**, so code written against anyio works unchanged on both. That is the whole purpose of it.

Which creates a question `pytest-asyncio` never has to ask. There is one asyncio, so its plugin simply uses it. anyio supports two, so it cannot know which is wanted — and `anyio_backend` is the fixture that answers.

### The fixture is not required

anyio ships its own, and reading it is worth more than any description of it.

```python
@pytest.fixture(scope="module", params=get_available_backends())
def anyio_backend(request):
    return request.param
```

**It is parametrised over every backend anyio can find installed.**

```python
>>> from anyio import get_available_backends
>>> get_available_backends()
('asyncio',)
```

With Trio absent that list holds one entry, so every test runs once — which is why deleting the fixture from a test file changes nothing at all.

### Writing your own is a pin, not a requirement

```python
@pytest.fixture
def anyio_backend():
    return "asyncio"
```

That **overrides** anyio's fixture with one that is not parametrised.

The reason to bother is the multiplication from the fixtures note, arriving from a direction nobody watches. The default's parameter list is not something anybody wrote — it is **whatever happens to be installed**.

| `anyio_backend` | Parameters | Result |
|---|---|---|
| anyio's default, Trio absent | `("asyncio",)` | one run per test |
| anyio's default, Trio installed | `("asyncio", "trio")` | **two runs per test** |
| your own, returning a string | none | one run per test, always |

So the day `trio` turns up in the environment — quite possibly dragged in by some other package — every anyio test in the suite starts running twice, and nothing in the code changed to cause it.

> **Define it to say this application runs on asyncio and only asyncio.** Not because the plugin needs telling, but because the default's answer depends on what is installed rather than on a decision anybody made.

For a library that genuinely supports both backends the default is exactly right, and returning `["asyncio", "trio"]` is a deliberate choice to test against both. For an application on FastAPI, one backend is the truth and pinning it removes a surprise.

Put it in `conftest.py` and it covers the whole suite rather than being repeated in every file.

---

## Async fixtures

A fixture can be `async def` too, and it needs the same plumbing a test does.

```python
async def open_connection():
    return {"connected": True}


@pytest.fixture
async def connection():
    return await open_connection()


@pytest.mark.anyio
async def test_async_test_with_async_fixture(connection):
    assert connection["connected"]


def test_sync_test_with_async_fixture(connection):
    assert connection
```

```
.E
ERROR at setup of test_sync_test_with_async_fixture
'test_sync_test_with_async_fixture' requested an async fixture 'connection',
with no plugin or hook that handled it. This is an error, as pytest does not
natively support it.
```

The async test passed. The sync test **errored**, loudly, naming both the test and the fixture, with a link to the documentation.

> Older material warns that a sync test given an async fixture silently receives a coroutine. **Current pytest catches it** — this is an error at setup rather than a quiet pass, and it is the good outcome for the same reason the earlier plugin failure was.

---

## One loop per test

```python
@pytest.mark.anyio
async def test_one():
    print(id(asyncio.get_running_loop()))
```

```
  test_one   loop: 4414286416
  test_two   loop: 4414656336
  test_three loop: 4414659856
```

Three tests, three different loops. **That is anyio's default and it is the safe one** — nothing an object holds can outlive the test that created it, because the loop it belongs to is gone.

Which sets up the error that costs an afternoon.

---

## The error that names everything except the cause

```python
# conftest.py
@pytest.fixture                  # function scope, the default
def anyio_backend():
    return "asyncio"
```

```python
# test_mismatch.py
@pytest.fixture(scope="module")  # module scope
async def shared_lock():
    return asyncio.Lock()


@pytest.mark.anyio
async def test_one(shared_lock):
    async with shared_lock:
        assert True
```

```
ScopeMismatch: You tried to access the function scoped fixture anyio_backend
with a module scoped request object. Requesting fixture stack:
  .../anyio/pytest_plugin.py:133:  def wrapper(anyio_backend, request, **kwargs)
Requested fixture:
  conftest.py:4:  def anyio_backend()
```

An **async** fixture needs an event loop to run in, so anyio's plugin makes it depend on `anyio_backend`. And the scope rule from the fixtures note applies unchanged: a module-scoped fixture cannot depend on a function-scoped one.

### Read what that message names

| Named | What it is |
|---|---|
| `anyio_backend` | the fixture at the bottom of the chain |
| `anyio/pytest_plugin.py:133  wrapper` | a function inside a library nobody here wrote |

**`shared_lock` appears nowhere**, and neither does `test_mismatch.py`. The fixture whose `scope="module"` caused all of it is not in the message.

> You are handed a conflict between a line in your `conftest.py` and a line in a library, and **the thing that has to change is in a third file that is not mentioned**.

### The fix, and the irony in it

```python
@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"
```

```
..                                                                       [100%]
2 passed in 0.00s
```

One word. Now look again at anyio's own default.

```python
@pytest.fixture(scope="module", params=get_available_backends())
def anyio_backend(request):
    return request.param
```

**It is module-scoped.** So pinning the backend with a plain `@pytest.fixture` quietly **narrowed** the scope from module to function, and that narrowing is what broke a module-scoped async fixture two files away.

> **Overriding a fixture means inheriting responsibility for its scope as well as its value.** The pin was about which backend to run on; it also changed how long the loop lives, and nothing in the code says so.

### Which is why one loop per test is the default worth keeping

The moment a fixture is widened past `function`, the loop has to widen to match — and everything sharing that loop is now sharing state across tests. That is the leak from the fixtures note, with an event loop as the shared object.

Widen it only when a fixture genuinely cannot be rebuilt per test. A database container qualifies. An `asyncio.Lock` does not, and the same file with no scope at all works perfectly.
