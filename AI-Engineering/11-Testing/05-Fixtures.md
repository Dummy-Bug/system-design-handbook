#testing #pytest #fixtures #isolation

**Widening a fixture's scope is how a slow suite becomes a fast one, and it is the single most common way a suite starts lying.** Both come from the same setting, and the difference between them is one property of the object being shared.

# Fixtures, And Where State Leaks

> [!info] A fixture is setup that tests ask for by name. How often it runs is a choice, running it less often is how suites get fast, and running it less often is also how one test's state reaches another.

## The problem fixtures solve

A test file with no fixtures in it.

```python
def test_gross_annual():
    records = MagicMock()
    records.fetch_monthly_pay.return_value = 5000
    tax = MagicMock()
    tax.tax_for.return_value = 6000
    service = PayrollService(records, tax)

    assert service.gross_annual(7) == 60000


def test_tax_due():
    records = MagicMock()
    records.fetch_monthly_pay.return_value = 5000
    tax = MagicMock()
    tax.tax_for.return_value = 6000
    service = PayrollService(records, tax)

    assert service.tax_due(7) == 6000


def test_net_annual():
    records = MagicMock()
    records.fetch_monthly_pay.return_value = 5000
    tax = MagicMock()
    tax.tax_for.return_value = 6000
    service = PayrollService(records, tax)

    assert service.net_annual(7) == 54000
```

**Fifteen lines of setup, three lines of assertion.** Every test says the same six lines before it says anything of its own.

That is annoying rather than dangerous. Here is the dangerous part.

### What happens when the code changes

The service grows a third dependency — an audit log — so the constructor takes another argument.

```
FAILED test_payroll.py::test_gross_annual - TypeError: PayrollService.__init_...
FAILED test_payroll.py::test_tax_due      - TypeError: PayrollService.__init__() m...
FAILED test_payroll.py::test_net_annual   - TypeError: PayrollService.__init__(...
3 failed in 0.02s
```

Three tests, three identical edits. With forty tests it is forty.

And that is still the **visible** failure. The invisible one is drift: with forty copies, whoever updates them fixes thirty-eight and improvises on two, and the file quietly starts disagreeing with itself about what the world looks like — with nothing failing to say so.

---

## The same file with a fixture

```python
@pytest.fixture
def service():
    records = MagicMock()
    records.fetch_monthly_pay.return_value = 5000
    tax = MagicMock()
    tax.tax_for.return_value = 6000
    audit_log = MagicMock()
    return PayrollService(records, tax, audit_log)


def test_gross_annual(service):
    assert service.gross_annual(7) == 60000


def test_tax_due(service):
    assert service.tax_due(7) == 6000


def test_net_annual(service):
    assert service.net_annual(7) == 54000
```

```
...                                                                      [100%]
3 passed in 0.01s
```

**One line each.** The constructor change is now one edit in one place, and there is exactly one description of the world in the file, so nothing can drift from anything.

### What the parameter actually holds

Worth being explicit about, because the name appears twice and means two different things.

```python
@pytest.fixture
def service():                   # here it is a function
    ...
    return PayrollService(records, tax, audit_log)


def test_gross_annual(service):  # here it is a PayrollService
    assert service.gross_annual(7) == 60000
```

pytest sees the parameter name, finds the fixture with that name, **calls it**, and passes the return value in. By the time the test body runs, the calling has already happened.

Printing it removes any doubt.

```python
def test_what_the_parameter_actually_is(expensive_client):
    print(type(expensive_client), expensive_client)
```

```
type : <class 'dict'>
value: {'connected': True}
```

So writing `service()` would be trying to call a `PayrollService` object, and Python would say it is not callable.

The Java version makes it obvious.

```java
@Test
void testOne(@Autowired RecordsClient client) {
    client.fetch(7);      // not client().fetch(7)
}
```

Nobody calls an injected dependency, because injection means the framework already built it and handed it over. **A fixture parameter is exactly that** — the name is a request, and what arrives is the object.

The only thing making it look odd in Python is that the fixture function and the injected value share a name. In Spring the bean type and the parameter name are different words, so the two never blur.

### The part specific to tests

Removing duplication is the ordinary argument and it applies to any code. Something else is happening here too.

> **Each test now says only what makes it different.** `test_tax_due` is a single line, and that line is the entire content of the test.

Which pays off on failure. A failing test that is one line tells you immediately what it was checking. A failing test buried in six lines of arrange means separating the subject from the scaffolding — every time, for every failure.

### The order that matters

This fixture is correct because it was **pulled out of three tests that already existed and already agreed**.

A fixture written before the tests is a guess about what they will need, and guesses accumulate into a `conftest.py` full of setup nobody uses and nobody dares delete.

> **Write the duplication first. Then remove it.**

---

## How often a fixture runs is a choice

Every fixture so far has run once per test. That is a default rather than a law.

Here is one that announces itself.

```python
@pytest.fixture
def expensive_client():
    print("\n  >>> building the client")
    return {"connected": True}


def test_one(expensive_client):
    assert expensive_client["connected"]

# ... test_two, test_three, test_four, all the same
```

```
  >>> building the client
.
  >>> building the client
.
  >>> building the client
.
  >>> building the client
.
4 passed in 0.00s
```

Four tests, **four builds**.

Every run in this note uses the same command.

```
uv run pytest -q -s
```

`-q` for the short report, and **`-s` to stop pytest swallowing `print`**. Anything printed by a passing test is captured and discarded by default, to keep the report clean — so without `-s` those `>>> building the client` lines never appear at all.

Now one word changes.

```python
@pytest.fixture(scope="module")
def expensive_client():
    ...
```

```
  >>> building the client
....
4 passed in 0.00s
```

**One build, four tests.**

### The five scopes

| Scope      | Runs once per          | Torn down when     |
| ---------- | ---------------------- | ------------------ |
| `function` | test — **the default** | that test ends     |
| `class`    | test class             | the class ends     |
| `module`   | file                   | the file ends      |
| `package`  | directory              | the directory ends |
| `session`  | **entire run**         | the run ends       |

They nest as expected, and the wider the scope the fewer times the fixture runs.

### Why anyone bothers

That toy fixture builds a dictionary, so the saving is nothing. Substitute something real.

- starting a Postgres container — **two to five seconds**
- creating a database schema — hundreds of milliseconds
- loading a model or a large file — seconds
- opening an authenticated HTTP session — a round trip

At `function` scope across 200 tests, a two-second container start is **400 seconds of pure setup**. At `session` scope it is two seconds, once.

That is not an optimisation. It is the difference between a suite that runs on every save and a suite nobody runs.

### And the price

Look again at what the module-scoped version actually did.

```python
return {"connected": True}
```

Four tests received **the same dictionary object**. Not four equal dictionaries — one dictionary, handed to all of them.

At `function` scope each test got its own, so nothing one test did could reach another. At `module` scope that guarantee is gone, and it was removed by a keyword argument that reads like a performance setting.

> **Scope is not a performance setting. It is a decision about whether tests share an object**, and the speed is a side effect of that decision.

---

## The leak, built out of nothing but a keyword

A fixture returning a list of teachers, shared across the run.

```python
@pytest.fixture(scope="session")
def teachers():
    return [
        {"id": 7, "name": "Priya"},
        {"id": 8, "name": "Rahul"},
    ]


def test_hiring_adds_a_teacher(teachers):
    teachers.append({"id": 9, "name": "Arshiya"})
    assert len(teachers) == 3


def test_the_school_has_two_teachers(teachers):
    assert len(teachers) == 2
```

Each one alone:

```
$ pytest -q -k hiring
1 passed, 1 deselected in 0.00s

$ pytest -q -k school
1 passed, 1 deselected in 0.00s
```

Both together:

```
E   where 3 = len([{'id': 7, 'name': 'Priya'}, {'id': 8, 'name': 'Rahul'}, {'id': 9, 'name': 'Arshiya'}])

FAILED test_teachers.py::test_the_school_has_two_teachers - AssertionError: a...
1 failed, 1 passed in 0.01s
```

The second test found a teacher the first one hired.

> **This is the cache leak from the previous note, rebuilt with no global variable anywhere.** One keyword argument was enough.

### How innocent the fixture looks

Every line inside it is correct. It returns a **fresh list literal** — new brackets, new dictionaries, nothing shared with anything.

That is exactly the trap. A function body creating a new object promises freshness **per call**, not per test. `scope="session"` means it is called once, so all of that freshness happens once and everything afterwards receives the same object.

Change the one word to `scope="function"` and both tests pass, because the body runs twice and there genuinely are two lists.

---

## The property that decides it

Not everything at session scope is dangerous. These are all fine.

```python
@pytest.fixture(scope="session")
def base_url():
    return "http://records.example/api"      # a string cannot be changed


@pytest.fixture(scope="session")
def db_container():
    ...                                      # expensive, and nobody mutates a container


@pytest.fixture(scope="session")
def tax_bands():
    return (10000, 50000, 100000)            # a tuple cannot be changed
```

The deciding factor is not how expensive the object is, or how many tests use it. It is **whether a test can change it**.

| Session-scoped object | Safe? | Why |
|---|---|---|
| a string, a tuple, a frozen config | yes | nothing can modify it |
| a running container or connection | usually | expensive, and tests use it rather than alter it |
| a list, a dict, a populated database | **no** | one test's write is every later test's starting state |

> **Widen scope only for things that are expensive and immutable — or expensive and explicitly reset between uses.** A mutable object at session scope is a shared global with nicer syntax.

### Why it is hard to catch

The failing test is `test_the_school_has_two_teachers`, and it is correct. It asserts something true about a school with two teachers and would pass on its own forever.

The damage was done by `test_hiring_adds_a_teacher`, **which passed**.

The report points at the victim, the guilty test is green, and reversing the order moves the failure. The only difference from the earlier version is that this one was caused by a keyword argument rather than a module-level dictionary — which makes it harder to see, because there is no global anywhere to notice.

---

## One test, many cases

Three tests that differ only in their numbers.

```python
def test_one_thousand():
    assert annual_from_monthly(1000) == 12000


def test_zero():
    assert annual_from_monthly(0) == 0


def test_negative():
    assert annual_from_monthly(-500) == -6000
```

The same thing as one function.

```python
@pytest.mark.parametrize(
    "monthly, expected",
    [
        (1000, 12000),
        (0, 0),
        (-500, -6000),
    ],
)
def test_annual_from_monthly(monthly, expected):
    assert annual_from_monthly(monthly) == expected
```

```
test_annual_from_monthly[1000-12000] PASSED               [ 33%]
test_annual_from_monthly[0-0] PASSED                      [ 66%]
test_annual_from_monthly[-500--6000] PASSED               [100%]
3 passed in 0.00s
```

One function, **three tests**, each with an id built from its values.

### Why not just loop inside one test

Put a bug in the implementation — return 999 for anything at or below zero — and run both versions.

```python
def test_annual_from_monthly_loop():
    for monthly, expected in CASES:
        assert annual_from_monthly(monthly) == expected
```

```
loop version:           1 failed
parametrised version:   2 failed, 1 passed
```

The bug breaks two of the three cases. **The loop reported one**, because `assert` raises and the loop stops there. Fix that case, rerun, discover the next one — one at a time.

The parametrised version reports both failures and the case that still passes, so the shape of the bug is visible immediately: it affects zero and negatives, not positives.

| | Loop inside one test | `@pytest.mark.parametrize` |
|---|---|---|
| Cases reported | the first failure only | all of them |
| Report says | `1 failed` | `2 failed, 1 passed` |
| Running one case | not possible | `pytest "test_x.py::test_annual_from_monthly[0-0]"` |
| A case is | an iteration | a test, with its own id |

> **Each parametrised case is a separate test** — separately reported, separately runnable, separately counted.

---

## Parametrising the fixture instead

The same idea one level up. A fixture can take `params`, and then **every test using it runs once per value**.

```python
@pytest.fixture(params=["postgres", "sqlite"])
def database(request):
    return request.param


def test_insert(database):
    ...


def test_query(database):
    ...


def test_delete(database):
    ...
```

```
test_insert[postgres] PASSED                     [ 16%]
test_insert[sqlite] PASSED                       [ 33%]
test_query[postgres] PASSED                      [ 50%]
test_query[sqlite] PASSED                        [ 66%]
test_delete[postgres] PASSED                     [ 83%]
test_delete[sqlite] PASSED                       [100%]
6 passed in 0.01s
```

**Three tests, two params, six runs.**

`request` **is a fixture pytest supplies itself**, and `request.param` holds the current value. Nothing in the three tests mentions parameters — they ask for `database` and get run twice.

### Multiplies rather than adds

Two folders. Both hold **five test functions** and **three values**. Only the placement of the values differs.

```
A - the values on a test        ->   7 passed
B - the values on a fixture     ->  15 passed
```

**Folder A**

```python
@pytest.mark.parametrize("monthly", [1000, 0, -500])
def test_annual(monthly): ...

def test_tax(): ...
def test_net(): ...
def test_report(): ...
def test_audit(): ...
```

The three values belong to `test_annual`, and nothing else in the file knows they exist.

```
test_annual   3 runs
test_tax      1
test_net      1
test_report   1
test_audit    1
              ----
              7
```

It **added** two runs: `3 + 1 + 1 + 1 + 1`.

**Folder B**

```python
# conftest.py
@pytest.fixture(params=["postgres", "sqlite", "mysql"])
def database(request): ...
```

```python
def test_annual(database): ...
def test_tax(database): ...
def test_net(database): ...
def test_report(database): ...
def test_audit(database): ...
```

Now the values belong to the fixture, and every test asking for it inherits all three — **the whole test body runs again for each value**.

```
test_annual   3 runs
test_tax      3
test_net      3
test_report   3
test_audit    3
              ----
              15
```

It **multiplied**: `5 x 3`.

### Where the values are written decides who they apply to

| | Written on | Applies to | Growth |
|---|---|---|---|
| `@pytest.mark.parametrize` | one test | that test only | `+ (cases - 1)` |
| `@pytest.fixture(params=...)` | the fixture | every test that names it | `x cases` |

The second is a decision made **once**, in a `conftest.py`, that keeps applying to tests written months later by people who never opened that file.

| | Tests using the fixture | Params | Total runs |
|---|---|---|---|
| today | 5 | 3 | 15 |
| in six months | 40 | 3 | 120 |
| plus a fourth backend | 40 | 4 | **160** |

Nobody decides to add forty test runs. Somebody adds one string to a list, sees a one-word diff, and every test in the folder below that `conftest.py` runs an extra time — including the ones with nothing to do with databases, which were only pulling the fixture in for a connection string.

> **Parametrise the test when the cases belong to that test. Parametrise the fixture only when every dependent test genuinely has to hold under all the values.**

The legitimate use is exactly that second sentence — a suite that must pass identically against two database backends, or two API versions. When that is really the requirement, nothing else does the job as well. When it is not, it is a quiet multiplier on runtime that nobody notices being added.

---

## A fixture is a dependency injection container

Try giving a long-lived fixture a short-lived dependency.

```python
@pytest.fixture(scope="function")
def per_test_thing():
    return {"fresh": True}


@pytest.fixture(scope="session")
def long_lived_thing(per_test_thing):
    return {"holds": per_test_thing}
```

```
ScopeMismatch: You tried to access the function scoped fixture per_test_thing
with a session scoped request object.
```

pytest refuses, and it is an error rather than a warning.

That is Spring's **singleton-injecting-a-prototype** problem, and pytest simply declines to let it happen.

### The translation

Everything in this note has a Spring name.

| pytest | Spring |
|---|---|
| `@pytest.fixture` | `@Bean` |
| naming it as a parameter | `@Autowired` |
| resolution by **name** | resolution by **type** |
| `scope="function"` | prototype |
| `scope="session"` | singleton |
| `conftest.py` | a `@Configuration` class, scoped by folder |
| a fixture asking for other fixtures | a bean with constructor dependencies |
| `ScopeMismatch` | injecting a prototype into a singleton |

> **A fixture is a dependency injection container** — not analogous to one, but the same thing with a smaller syntax and a folder-based scope for visibility.

Which means existing reasoning about bean lifetimes applies here unchanged, and so does the bug that comes with it.

### The bug that transfers

The classic Spring mistake is a singleton bean holding mutable state. Built once, injected everywhere, and one request's write becomes the next request's starting condition. Fine in development, wrong under concurrency.

The pytest version has already appeared in this note.

```python
@pytest.fixture(scope="session")
def teachers():
    return [{"id": 7, "name": "Priya"}, {"id": 8, "name": "Rahul"}]
```

**Same bug, same cause, same fix.** A long-lived object handed to short-lived consumers, where the object can be changed.

One rule resolves both: a singleton is safe while it is **stateless or immutable**, and dangerous the moment it holds something writable. Spring says stateless beans; this note says expensive and immutable. They are the same sentence.

### Where the analogy stops

Two differences, both in pytest's favour.

**Resolution is by name, not type.** Spring finds a `RecordsClient` by its type and complains when two candidates exist. pytest finds `records_client` by that exact string. Simpler — and it means a fixture can be shadowed, since a `conftest.py` deeper in the tree can define the same name and quietly override the one above it. Occasionally exactly what is wanted, occasionally very confusing.

**Scope is enforced rather than merely documented.** Spring allows a prototype to be injected into a singleton and then behaves surprisingly. pytest raises `ScopeMismatch` and stops.

The mistake still available is the one above — a session-scoped fixture whose object is mutable — because nothing about a list's type says whether anybody is going to write to it.
