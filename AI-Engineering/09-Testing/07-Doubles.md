#testing #pytest #mocks #doubles

**Python spells every kind of test double `Mock`, so the differences between them have to be held in the head rather than read off the type.** Four names, four jobs, and two of them have opposite rules about what a test may assert on.

# Test Doubles, Named Precisely

> [!info] A stub supplies an answer so the code can run and should never be asserted on. A mock records what happened so the test can check it, and that assertion is the point. Confusing the two produces tests that break on every refactor while catching nothing.

## Two doubles, one class

One function with two dependencies.

```python
def notify_underpaid(teacher_id, records, mailer):
    pay = records.fetch_monthly_pay(teacher_id)
    if pay < 3000:
        mailer.send(to=f"teacher{teacher_id}@school.example",subject="Pay review")
        return True
    return False
```

```python
def test_underpaid_teacher_is_emailed():
    records = MagicMock()                              # supplies an answer
    records.fetch_monthly_pay.return_value = 2500

    mailer = MagicMock()                               # records what happened

    result = notify_underpaid(7, records, mailer)

    assert result is True
    mailer.send.assert_called_once_with(
        to="teacher7@school.example", subject="Pay review"
    )
```

Both are `MagicMock()`. They are doing two entirely different jobs.

### The distinction

| | **Stub** | **Mock** |
|---|---|---|
| Its job | supply an answer the code needs | record what was done to it |
| Direction | data going **in** to the subject | behaviour coming **out** of the subject |
| The test asserts on it | no | **yes, that is the point** |
| Above | `records` | `mailer` |

> **How to tell which one you are looking at: does the test assert on it?** If not it is a stub — scaffolding, so the code can run. If it does, that assertion is a substantial part of what the test is for.

---

## Why the distinction matters when Python does not care

Nothing enforces this. It matters because **the two have opposite rules about assertions**.

A mock should be asserted on. That is its entire reason for existing.

A stub should not. Here is what happens when that is forgotten.

Take the same function, with one sloppy detail — it asks for the pay twice.

```python
def notify_underpaid(teacher_id, records, mailer):
    if records.fetch_monthly_pay(teacher_id) < 3000:
        mailer.send(
            to=f"teacher{teacher_id}@school.example",
            body=f"Your pay is {records.fetch_monthly_pay(teacher_id)}",
        )
        return True
    return False
```

Two tests, identical except for one extra line at the end of the second.

```python
def test_behaviour_only():
    records = MagicMock()
    records.fetch_monthly_pay.return_value = 2500
    mailer = MagicMock()

    result = notify_underpaid(7, records, mailer)

    assert result is True
    assert mailer.send.call_count == 1


def test_behaviour_plus_the_stub():
    records = MagicMock()
    records.fetch_monthly_pay.return_value = 2500
    mailer = MagicMock()

    result = notify_underpaid(7, records, mailer)

    assert result is True
    assert mailer.send.call_count == 1
    assert records.fetch_monthly_pay.call_count == 2
```

```
..                                                                       [100%]
2 passed in 0.01s
```

### Now tidy the code

Ask once and remember the answer.

```python
def notify_underpaid(teacher_id, records, mailer):
    pay = records.fetch_monthly_pay(teacher_id)
    if pay < 3000:
        mailer.send(
            to=f"teacher{teacher_id}@school.example",
            body=f"Your pay is {pay}",
        )
        return True
    return False
```

A duplicate call removed. **The email is identical and the stub is untouched.**

```
FAILED test_notify.py::test_behaviour_plus_the_stub - AssertionError: assert ...
1 failed, 1 passed in 0.01s
```

### Which one failed, and why

**`test_behaviour_only` passed.** It asserts what the function is for — an underpaid teacher gets one email. That did not change, so the test did not care that the implementation did.

**`test_behaviour_plus_the_stub` failed**, on `records.fetch_monthly_pay.call_count == 2`.

That line was asserting **how often the function asks for its data**. Version 1 asked twice because it was sloppy; version 2 asks once. The test was quietly holding the sloppiness in place.

### The cost is not the one failure

That test now has to be edited to say `== 1`. Which means:

- it needed changing although the behaviour did not
- the change is mechanical, so it gets made without thinking
- **and that is exactly when a real regression slips through**, because the habit of editing this test whenever the implementation moves has already been trained

> **A test that fails on every refactor stops being read and starts being edited.** That is how a suite decays into something people fix rather than something people trust.


### The two assertions, side by side

| Assertion | Asks | Breaks when |
|---|---|---|
| `assert mailer.send.call_count == 1` | did the right thing happen | the behaviour changes — **correct** |
| `assert records.fetch_monthly_pay.call_count == 2` | did it happen the way I expected | the implementation changes — **noise** |

> `records` is a stub. It exists so the **function can obtain a number**, and the moment a test asserts on it, the test has **stopped examining the function** and started examining the shape of a conversation nobody asked to keep stable.

> `mailer` is different. Sending that email **is** **the** **behaviour**, so asserting on it is asserting on the outcome.

> **Assert on the mock. Leave the stub alone.** Same class, opposite rules.

That is a failure mode the earlier notes never touched. Not a test that passes when it should fail — a test that **fails when nothing is wrong**, which is the other half of the pair from the first note.

---

## The fake, and what it catches that a stub cannot

Put a bug in the function — it looks up the wrong teacher.

```python
def notify_underpaid(teacher_id, records, mailer):
    pay = records.fetch_monthly_pay(teacher_id + 1)      # the bug
    if pay < 3000:
        mailer.send(to=f"teacher{teacher_id}@school.example", body=f"Your pay is {pay}")
        return True
    return False
```

Two tests. One uses the stub from earlier; the other uses a **fake**.

```python
class FakeRecords:
    """A working implementation, with a dictionary instead of a database."""

    def __init__(self, pay_by_id):
        self._pay = pay_by_id

    def fetch_monthly_pay(self, teacher_id):
        return self._pay[teacher_id]


def test_with_a_stub():
    records = MagicMock()
    records.fetch_monthly_pay.return_value = 2500
    mailer = MagicMock()

    assert notify_underpaid(7, records, mailer) is True


def test_with_a_fake():
    records = FakeRecords({7: 2500})
    mailer = MagicMock()

    assert notify_underpaid(7, records, mailer) is True
```

```
test_with_a_stub  ->  passed
test_with_a_fake  ->  FAILED - KeyError: 8
```

The function asked for teacher **8** when it was given **7**.

**A stub answers every question the same way.** Ask about 7, about 8, about a teacher who does not exist — 2500 every time. It cannot notice a wrong argument because it never looks at arguments.

**A fake has behaviour.** Nine lines and a dictionary instead of a database, but it genuinely implements the thing, so asking for a teacher it does not hold fails exactly as the real records system would.

| | Answers | Notices a wrong argument |
|---|---|---|
| **Stub** | the same thing, always | no |
| **Fake** | according to its own state | **yes** |

> A fake costs more to write and catches a class of bug a stub structurally cannot.

---

## The spy, where the real code still runs

```python
def test_with_a_spy():
    real = FakeRecords({7: 2500})
    records = MagicMock(wraps=real)          # a spy

    result = notify_underpaid(7, records, mailer)

    assert result is True    # real behaviour happened
    records.fetch_monthly_pay.assert_called_once_with(7)   # and it was recorded
```

Compare a plain mock with one given `wraps=`.

```
MagicMock()             ->  <MagicMock ...>    recorded: [call(7)]
MagicMock(wraps=real)   ->  2500               recorded: [call(7)]
```

Both wrote the call down. Only the second produced a real answer.

### It bypasses nothing, it adds a layer

```
your code  ->  MagicMock(wraps=real)  ->  real
                      |                     |
              writes down the call     does the work
```

The mock sits in front. Every call is **recorded and then forwarded** to whatever it wraps, and the answer coming back is the real one rather than an invented `MagicMock`. It even fails the same way — ask that spy for teacher 8 and it raises `KeyError`, because the object underneath does.

### What it wraps is whatever you hand it

Above, that was a `FakeRecords`, so the spy forwarded into a dictionary. **Two doubles stacked**, which is not a normal arrangement — it was done that way so the demonstration needs no database.

In real use, `wraps=` goes around the actual object.

```python
records = MagicMock(wraps=RecordsClient(url, token))
```

Now the real client runs, the real network call happens, the real answer comes back, and every call made to it is recorded as well.

### When you would reach for one

> **A spy is for when you cannot replace the thing, but you want to know what was asked of it.**

Chasing a slow endpoint, suspecting the same lookup is happening four times. Swap the client for a stub and you have changed the very behaviour under investigation. Wrap it in a spy and everything runs exactly as before, plus `call_count` answers the question.

The cost is that **a spy is not isolation.** The real work still happens — the network call, the database write, the email — so it belongs to debugging and to careful integration tests, never to a fast unit suite.


---

## The four, in one table

|          | The real code runs                 | Answers come from        | Its purpose                         |
| -------- | ---------------------------------- | ------------------------ | ----------------------------------- |
| **Stub** | no                                 | `return_value`           | let the subject proceed             |
| **Mock** | no                                 | nowhere, it only records | assert on the interaction           |
| **Fake** | no — a simpler implementation runs | **its own state**        | behave like the real thing, cheaply |
| **Spy**  | **yes**                            | the real object          | watch without changing anything     |

### Why the names carry the weight in Python

Every one of those was a `MagicMock` or a plain class.

```python
records = MagicMock()                    # stub
mailer  = MagicMock()                    # mock
records = FakeRecords({7: 2500})         # fake
records = MagicMock(wraps=real)          # spy
```

**Python has no separate type for any of them.** Java at least offers `mock()` and `spy()` as different functions; here the only signal is what the test does with the object afterwards.

> Which is why the vocabulary matters more in Python than in a language that encodes it. Somebody in a review saying **that is a stub, do not assert on it** is making a precise technical point, and nothing in the code says it for them.

---

## The double that will impersonate anything

A real class with exactly one method.

```python
class RecordsClient:
    def fetch_monthly_pay(self, teacher_id):
        raise RuntimeError("this would hit the network")
```

And production code with a typo in it.

```python
def notify_underpaid(teacher_id, records, mailer):
    pay = records.fetch_montly_pay(teacher_id)      # montly
    mailer.send(to=f"teacher{teacher_id}@school.example", body=f"Your pay is {pay}")
    return True
```

Two tests, differing only in how the double is built.

```python
def test_with_a_plain_mock():
    records = MagicMock()
    notify_underpaid(7, records, MagicMock())


def test_with_autospec():
    records = create_autospec(RecordsClient)
    notify_underpaid(7, records, MagicMock())
```

```
FAILED test_notify.py::test_with_autospec - AttributeError: Mock object has n...
1 failed, 1 passed in 0.04s
```

**The plain mock passed.** The function calls a method that does not exist on the real class, puts the resulting mock object into an email body, and the test is green.

```
AttributeError: Mock object has no attribute 'fetch_montly_pay'.
Did you mean: 'fetch_monthly_pay'?
```

Autospec failed, and named the typo.

### Even when the plain mock fails, it fails uselessly

The version above passes the value straight into the email. Change it so the value is actually **used** — compared against a threshold — and the plain mock does eventually break.

```python
def notify_underpaid(teacher_id, records, mailer):
    pay = records.fetch_montly_pay(teacher_id)      # same typo
    if pay < 3000:                                  # the new line
        mailer.send(to=f"teacher{teacher_id}@school.example")
        return True
    return False
```

Both tests now fail, and the two messages are not equally useful.

```
plain mock:  TypeError: '<' not supported between MagicMock and int
autospec:    AttributeError: Mock object has no attribute 'fetch_montly_pay'.
             Did you mean: 'fetch_monthly_pay'?
```

`MagicMock()` invented the method, returned another mock, and the test carried on until `pay < 3000` tried to compare a mock with a number. **The message points at the comparison; the bug is the typo on the line above it.**

And that failure was luck. It only broke because something happened to compare the value. The passed-along version had no comparison and stayed green.

---

## What create_autospec does

```python
records = create_autospec(RecordsClient)
```

It reads the real class and builds a double **shaped like it**. Ask for a method that is not there and the answer is `AttributeError` rather than an invention. It checks signatures too, so calling a method with the wrong number of arguments raises, exactly as the real one would.

| | `MagicMock()` | `create_autospec(RealClass)` |
|---|---|---|
| Unknown method | invented silently | `AttributeError` |
| Wrong argument count | accepted | `TypeError` |
| Knows the real class | no | yes |
| Cost | nothing | one import |

There is a shorter form of the same idea.

```python
records = MagicMock(spec=RecordsClient)
```

`spec=` constrains attribute names. `create_autospec` does that plus signatures, and recurses into nested attributes. **Prefer `create_autospec`** — stricter, and it costs the same.

### Why this matters more than it looks

Earlier: a mock cannot fail an assertion by accident. This is the same property one level up — **a mock cannot fail to have a method either**.

So an ordinary `MagicMock` will happily impersonate an API that no longer exists. Rename a method on the real client, update every caller, miss one, and that one's test stays green forever — because the double never knew what the real class looked like.

> **A test double that does not know the shape of the thing it replaces cannot notice when that shape changes.** Autospec is the one line that connects them.

Which answers something left open earlier. A vacuous test caused by mocking one layer too high is a judgement problem. A vacuous test caused by a typo or a stale API is **mechanically preventable**, and this is the mechanism.

---

## Where patch has to point

Two modules and one import style.

```python
# records.py
def fetch_monthly_pay(teacher_id):
    raise RuntimeError("this hit the real network")
```

```python
# notify.py
from records import fetch_monthly_pay


def is_underpaid(teacher_id):
    return fetch_monthly_pay(teacher_id) < 3000
```

Two tests, differing in one word.

```python
def test_patching_where_it_is_defined():
    with patch("records.fetch_monthly_pay", return_value=2500):
        assert is_underpaid(7) is True


def test_patching_where_it_is_used():
    with patch("notify.fetch_monthly_pay", return_value=2500):
        assert is_underpaid(7) is True
```

```
FAILED test_notify.py::test_patching_where_it_is_defined - RuntimeError: this...
1 failed, 1 passed in 0.01s
```

The first patched something, and the real function ran anyway.

### Why

The one-line version is a Java one. Two variables holding the same reference, and reassigning one does not touch the other.

```java
Client a = new Client();
Client b = a;          // both point at the same object

a = new FakeClient();  // only 'a' moved. 'b' still points at the original
```

`patch` is that reassignment. Here it is in four steps.

**A module is a table of names.**

Every module holds a table mapping names to objects. `records.py` has one entry in its table.

```
records' table
  "fetch_monthly_pay"  ->  <function at 4446024656>
```

**`from ... import` copies into the other table.**

```python
# notify.py
from records import fetch_monthly_pay
```

That line runs **once**, when `notify` is first imported. It looks the name up in `records`' table and writes an entry into `notify`'s table pointing at the same object.

```
records' table
  "fetch_monthly_pay"  ->  <function at 4446024656>

notify's table
  "fetch_monthly_pay"  ->  <function at 4446024656>     the same object
```

Two entries, one function — and `records.fetch_monthly_pay is notify.fetch_monthly_pay` is `True`.

**`patch` edits one table entry.**

```
patch("records.fetch_monthly_pay")

records' table
  "fetch_monthly_pay"  ->  <MagicMock at 4445979712>    changed
notify's table
  "fetch_monthly_pay"  ->  <function at 4446024656>     untouched
```

`patch` did work. It changed `records`' entry, and nothing else.

**Which table does the running code read.**

```python
# notify.py
def is_underpaid(teacher_id):
    return fetch_monthly_pay(teacher_id) < 3000
```

That function lives in `notify`, so when it runs, Python resolves `fetch_monthly_pay` in **notify's table** — the module the code is written in.

It never consults `records`' table. The only time it did was at import, and that is long over. So patching `records` changed a table nobody reads, and the real function ran.

Point the patch at `notify` instead and the entry that `is_underpaid` actually reads is the one replaced.

```
patch("notify.fetch_monthly_pay")

records' table
  "fetch_monthly_pay"  ->  <function at 4446024656>     untouched
notify's table
  "fetch_monthly_pay"  ->  <MagicMock at 4445979376>    changed
```

> **`patch("module.name")` swaps an entry in that module's table**, so it has to be the module whose code does the calling — not the module where the function was written.

### The rule, and the symptom

> **Patch where the name is used, not where it is defined.**

The symptom is worth memorising, because it is not an error.

**Nothing complains.** `patch` found a name at `records.fetch_monthly_pay` and replaced it successfully — it has no way to know that nobody was reading it. So the patch applies to something nothing looks at, and the real code runs.

Here that was loud, because the real function raises. In a real codebase it is usually quieter: a slow test, a live HTTP call, a row written to a real database, and the test still passes.

### The import style decides the target

```python
from records import fetch_monthly_pay      # patch "notify.fetch_monthly_pay"
fetch_monthly_pay(teacher_id)
```

```python
import records                             # patch "records.fetch_monthly_pay"
records.fetch_monthly_pay(teacher_id)
```

> The second form looks the attribute up **at call time**, every time — so patching the definition works, because that is genuinely where the lookup goes.

Which is a real argument for `import records` over `from records import ...` in code meant to be tested. Not a style preference: it changes what has to be patched, and removes the most common way to get patching wrong.

It is also the same idea as a module-level cache. **A name bound at import time behaves differently from one resolved at call time**, and testability is usually the first place that difference shows up.

---

## Mock at the boundary you own

Three layers: your function, your client, and somebody else's HTTP library.

```python
# http_lib.py — a third-party library. You did not write it.
def get(url): ...


# records.py — yours
class RecordsClient:
    def fetch_monthly_pay(self, teacher_id):
        return http_lib.get(f"/teachers/{teacher_id}/pay")


# notify.py — yours
def is_underpaid(teacher_id, records):
    return records.fetch_monthly_pay(teacher_id) < 3000
```

Two tests for the same function, placing the double at two different depths.

```python
def test_mocking_their_library():
    with patch("http_lib.get", return_value=2500):
        assert is_underpaid(7, RecordsClient()) is True


def test_mocking_my_boundary():
    records = create_autospec(RecordsClient)
    records.fetch_monthly_pay.return_value = 2500

    assert is_underpaid(7, records) is True
```

```
..                                                                       [100%]
2 passed in 0.01s
```

### Then the library releases version 2

`get` becomes `request`. `records.py` is updated to match, and **nothing about what your code does has changed.**

```python
# http_lib.py
def request(url, method="GET"): ...


# records.py
class RecordsClient:
    def fetch_monthly_pay(self, teacher_id):
        return http_lib.request(f"/teachers/{teacher_id}/pay")
```

```
FAILED test_notify.py::test_mocking_their_library
       - AttributeError: <module 'http_lib'> does not have the attribute 'get'
1 failed, 1 passed in 0.04s
```

`is_underpaid` never changed and neither did its behaviour. But one test knew the name of a function inside a library, and that name moved.

### Where the two doubles sit

```
is_underpaid  ->  RecordsClient  ->  http_lib
                        |               |
                  your boundary    their internals
```

**`RecordsClient` is yours.** You wrote `fetch_monthly_pay`, you decide when its name changes, and if you change it then a failing test is correct.

**`http_lib.get` is not yours.** Its shape changes on somebody else's release schedule, for reasons unconnected to your code, and a test breaking because of it tells you nothing about whether your code is right.

> **Mock at the boundary you own.** A double at a seam you control breaks only when you break something. A double inside a dependency breaks when the dependency changes, which is noise wearing the costume of a test failure.

### What owning it actually means

Not that you wrote every line — that **you decide what the interface is**.

`RecordsClient` counts even when it is thin. A class doing nothing but calling `http_lib` still gives you a name you control, which is exactly why such wrappers keep appearing in codebases that are pleasant to test.

Where no wrapper exists, mocking the library is the only option and a legitimate one. It is worth knowing that a maintenance cost has been taken on, and that five lines would have removed it.

---

## Outcome or choreography

> assert on the outcome rather than the choreography, **unless the choreography is the requirement**

Both halves are real, and both have already appeared.

```python
assert result is True                        # the outcome
mailer.send.assert_called_once_with(...)     # the choreography
```

The first is right for `is_underpaid`, where the answer is what matters and how it was obtained is nobody's business.

The second is right for `notify_underpaid`, where **sending the email is the entire point**. No return value could carry that, and one email rather than two is a genuine requirement.

> The mistake is not asserting on calls. It is asserting on calls **when there was an outcome available to assert on instead**.
