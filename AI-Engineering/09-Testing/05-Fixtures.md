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

A sidebar on seeing that at all: **pytest swallows anything printed by a passing test**, to keep the report clean. The `-s` flag turns that capture off, which is why those lines are visible.

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

| Scope | Runs once per | Torn down when |
|---|---|---|
| `function` | test — **the default** | that test ends |
| `class` | test class | the class ends |
| `module` | file | the file ends |
| `package` | directory | the directory ends |
| `session` | entire run | the run ends |

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
