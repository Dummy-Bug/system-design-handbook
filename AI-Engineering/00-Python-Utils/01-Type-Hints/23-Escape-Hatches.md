#python #type-hints #typing #cast #escape-hatches #python-utils


`18-Narrowing` ended somewhere uncomfortable: `TypeIs` and `TypeGuard` turned out to be **promises you make**, not facts the checker verifies — a body of `return True` earned a clean `Success` and crashed at runtime.

This concept is the rest of that family, out in the open. Three ways to tell the checker *I know better than you*, in increasing order of bluntness. None of them make your code safer. All of them are necessary.

## Where narrowing stops

A dictionary whose values are `object` — the honest annotation for a bag of stuff you haven't pinned down:

```python
1  def handle(payload: dict[str, object]) -> str:
2      return payload["name"].upper()
```

```
$ mypy eh0.py
eh0.py:2: error: "object" has no attribute "upper"  [attr-defined]
```

Correct complaint. `object` sits at the top of the hierarchy and permits almost nothing, so `.upper()` isn't available on it.

And `18-Narrowing` already solved this:

```python
1  def handle(payload: dict[str, object]) -> str:
2      name = payload["name"]
3      if isinstance(name, str):
4          return name.upper()
5      raise TypeError("name must be a string")
```

```
$ mypy eh1.py
Success: no issues found in 1 source file
```

So the simple tool suffices. Now break it.

## The case narrowing cannot reach

You don't want one field. You want to hand the **whole dictionary** to something that expects a `ToolCall`:

```python
 4  class ToolCall(TypedDict):
 5      name: str
 6      args: dict[str, str]
 7
 8
 9  def dispatch(call: ToolCall) -> str:
10      return f"{call['name']}({call['args']})"
11
12
13  def handle(payload: dict[str, object]) -> str:
14      if isinstance(payload, ToolCall):
15          return dispatch(payload)
16      raise TypeError("not a tool call")
```

Line 14 is the same move as line 3 above. This time it is refused **twice**:

```
$ mypy eh2.py
eh2.py:14: error: Cannot use isinstance() with TypedDict type  [misc]
```

```
$ python3 eh2.py
TypeError: TypedDict does not support instance and class checks
```

Two refusals is unusual. Normally the checker objects to something Python would happily run; here Python refuses on its own account.

### Why — there is nothing on the object to look at

```python
 9  print(ToolCall.__mro__)
10  print(ToolCall(name="search", args={}).__class__)
```

```
$ python3 eh3.py
(<class '__main__.ToolCall'>, <class 'dict'>, <class 'object'>)
<class 'dict'>
```

Line 9 says the class genuinely exists and genuinely inherits from `dict`. Line 10 says the object you get back from it is a **plain dictionary** — `__class__` is `dict`, not `ToolCall`.

Both are true at once: the class is a construction-time convenience, and **it never stamps itself on the object it builds**. You go in through `ToolCall` and come out holding a dictionary with no memory of it.

So `isinstance` has nothing to follow. It walks `__mro__` (see `16-Protocol`), and there is no `__mro__` on the object leading anywhere useful. Two dictionaries with identical contents are indistinguishable, so the question genuinely has no answer.

And the check that *is* legal buys nothing:

```python
18      if isinstance(payload, dict):
19          return dispatch(payload)
```

```
$ mypy eh3.py
eh3.py:19: error: Argument 1 to "dispatch" has incompatible type "dict[str, object]"; expected "ToolCall"  [arg-type]
```

Every dictionary ever made passes that check, so mypy learns nothing from it. Line 19 is still `dict[str, object]`, still rejected.

> [!important] This is the position the escape hatches exist for, and it is worth naming precisely:
>
> **You know the fact. The checker doesn't. No runtime check can establish it.**
>
> Narrowing is exhausted — not because you wrote it badly, but because there is nothing left to narrow *on*.

## `cast` — "treat this as that"

Said in plain English, what you want is: *trust me, this is a `ToolCall`.* That sentence has a spelling.

```python
13  def handle(payload: dict[str, object]) -> str:
14      call = cast(ToolCall, payload)
15      return dispatch(call)
```

```
$ mypy eh4.py
Success: no issues found in 1 source file
```

```
$ python3 eh4.py
search({'q': 'hi'})
```

Read line 14 in the order you'd say it out loud — *treat `payload` as a `ToolCall`*. The type comes first, the value second. From line 15 onward mypy believes it.

## `cast` does nothing

The whole character of the tool is in what happens when the claim is false. Same code; the payload now arrives with no `args` key:

```python
13  def handle(payload: dict[str, object]) -> str:
14      call = cast(ToolCall, payload)
15      print("survived the cast:", call)
16      return dispatch(call)
17
18
19  print(handle({"name": "search"}))
```

```
$ mypy eh5.py
Success: no issues found in 1 source file
```

```
$ python3 eh5.py
survived the cast: {'name': 'search'}
Traceback (most recent call last):
  File "eh5.py", line 19, in <module>
  File "eh5.py", line 16, in handle
  File "eh5.py", line 10, in dispatch
    return f"{call['name']}({call['args']})"
KeyError: 'args'
```

**Line 15 printed.** The cast waved through a dictionary that plainly is not a `ToolCall`, and the program carried on.

It does not validate, it does not convert, it does not fill anything in. Here is `cast` in the standard library, complete:

```python
def cast(typ, val):
    """Cast a value to a type.

    This returns the value unchanged.  To the type checker this
    signals that the return value has the designated type, but at
    runtime we intentionally don't check anything (we want this
    to be as fast as possible).
    """
    return val
```

`return val`. That is the entire implementation — a no-op that exists purely to be **read** by the checker. The same trick as an annotation, in function form.

> [!warning] The word is borrowed from languages where it means something else. A cast in C or Java can convert, or can fail loudly. Python's `cast` does neither. Nothing is checked and nothing is changed; only the checker's opinion moves.

### It relocates the failure

Look at where that traceback lands. Not line 14, where the false claim was made — line 10, inside `dispatch`, two frames away.

`cast` never fails. It **moves** the failure to somewhere that no longer mentions the assumption that caused it. The line that lied is not in the traceback at all. That is what makes a wrong cast expensive: the crash tells you the data was bad, and says nothing about who decided it was fine.

> [!important] `cast` is `18-Narrowing`'s ending with the pretence removed. There, `TypeIs` at least *looked* like a check — it had a body, it returned a bool. `cast` drops the costume: it is an assertion, it is unverified, and it is honest about being both.

## The error with no value in it

`cast` covers one situation: *this value is a `T`, take my word for it.* Plenty of errors aren't shaped like that. The most common one you will ever hit:

```python
1  import hrms_sdk
2
3
4  def fetch(employee_id: int) -> str:
5      return hrms_sdk.get_employee(employee_id)
```

```
$ mypy ig0.py
ig0.py:1: error: Cannot find implementation or library stub for module named "hrms_sdk"  [import-not-found]
```

The code is fine. It runs in production, where the SDK is installed; mypy simply has no type information for it.

Now try to fix that with `cast`. **What would you cast, and to what?** There is no value on line 1 — it is an import statement. `cast` doesn't merely fail here, it structurally does not apply.

What is needed is a tool that acts on a **line** rather than a value.

## `# type: ignore` — "drop whatever you were going to say"

```python
1  import hrms_sdk  # type: ignore
...
5      reveal_type(hrms_sdk)
6      reveal_type(hrms_sdk.get_employee)
```

```
$ mypy ig1.py
ig1.py:5: note: Revealed type is "Any"
ig1.py:6: note: Revealed type is "Any"
Success: no issues found in 1 source file
```

A comment, and mypy complies.

Lines 5 and 6 are the honest accounting, though: `hrms_sdk` is now `Any`, and so is everything reached through it. You did not acquire types for the SDK — you acquired permission to stop asking for them. Getting the real ones is `22-Third-Party-Libraries`.

### The brackets are the whole difference

Here is a line carrying **two independent problems** — a `str | None` used as though it were a `str`, and the result assigned to an `int`:

```python
1  def get_name() -> str | None:
2      return "alice"
3
4
5  value: int = get_name().upper()
```

```
$ mypy ig2.py
ig2.py:5: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
ig2.py:5: error: Incompatible types in assignment (expression has type "str | Any", variable has type "int")  [assignment]
```

Two errors, two different codes, sharing a line by coincidence.

**Bare:**

```python
5  value: int = get_name().upper()  # type: ignore
```

```
$ mypy ig3.py
Success: no issues found in 1 source file
```

Both silenced. Nothing changed type — a bare `# type: ignore` means *say nothing about this line*, so it takes out **every error code**, including the one you never looked at.

**With the code in brackets:**

```python
5  value: int = get_name().upper()  # type: ignore[union-attr]
```

```
$ mypy ig4.py
ig4.py:5: error: Incompatible types in assignment (expression has type "str | Any", variable has type "int")  [assignment]
ig4.py:5: note: Error code "assignment" not covered by "type: ignore[union-attr]" comment
```

The one you decided about is silenced. The other survives, and mypy says so outright: **`not covered by "type: ignore[union-attr]" comment`**.

> [!important] The two comments make different promises:
>
> - `# type: ignore` — *I have looked at everything on this line, now and forever.*
> - `# type: ignore[union-attr]` — *I have looked at this one thing.*
>
> Only the second is a promise you can keep. The cost of the first is in the "forever": that line gets edited next year, grows a real bug with a different error code, and the bare comment swallows it in silence. Nobody ever sees the error that would have saved them.

**Where do the codes come from?** Mypy prints one at the end of every error message — `[union-attr]`, `[assignment]`, `[import-not-found]`. You copy it out of the error you are silencing. There is nothing to memorise.

### Aside — where that `str | Any` came from

Worth pinning down, because the message looks wrong at first glance. `get_name()` returns `str | None`, so why does the error say `str | Any`?

Split the union into its two halves and run each alone.

**Half A**, the function returns just `str`:

```python
1  def get_name() -> str:
2      return "alice"
3
4
5  reveal_type(get_name().upper())
```

```
half_a.py:5: note: Revealed type is "str"
```

**Half B**, the function returns just `None`:

```python
1  def get_name() -> None:
2      return None
3
4
5  reveal_type(get_name().upper())
```

```
half_b.py:5: error: "None" has no attribute "upper"  [attr-defined]
half_b.py:5: note: Revealed type is "Any"
```

The error is expected. The second line is the answer: mypy still has to say what type the expression *is*, has no real answer, and puts **`Any`** there.

So for the real `str | None`, it works one half at a time:

| half | result of `.upper()` |
|---|---|
| `str` | `str` |
| `None` | error, then `Any` |

Which is `str | Any`. And note `None` never appears in it — the expression being typed is `get_name().upper()`, not `get_name()`. `None` is the type of the thing you called `.upper()` *on*, not of what came back.

> [!tip] When a mypy message contains an `Any` you did not write, look **up the same line for an earlier error**. The `Any` is usually the wreckage of that one, not a separate problem.

## `Any` — the hatch that travels

`08-Any-Object-Never` introduced `Any`. Here it is chosen *deliberately* as an escape hatch, and the thing to measure is how far its effect reaches.

Two files. Line 5 differs by one word; lines 1-4 and 6-14 are byte-identical, unused `Any` import included.

```python
 1  import json
 2  from typing import Any
 3
 4
 5  def load_config(path: str) -> Any:
 6      return json.loads(open(path).read())
 7
 8
 9  cfg = load_config("config.json")
10
11  port: int = cfg["port"]
12  name: str = cfg["port"]
13  cfg.completely_made_up_method()
14  print(cfg + 1)
```

```
$ mypy any0.py
Success: no issues found in 1 source file
```

Lines 11 and 12 assign the **same value** to two different types. Line 13 calls a method that does not exist. Line 14 adds 1 to it. Zero errors.

Now `-> object` instead:

```python
 5  def load_config(path: str) -> object:
```

```
$ mypy any1.py
any1.py:11: error: Value of type "object" is not indexable  [index]
any1.py:12: error: Value of type "object" is not indexable  [index]
any1.py:13: error: "object" has no attribute "completely_made_up_method"  [attr-defined]
any1.py:14: error: Unsupported operand types for + ("object" and "int")  [operator]
```

Four errors. One word.

Both annotations mean *"I don't know what this is"*, and they draw opposite conclusions:

- **`object`** — I don't know what this is, so you may do **nothing** with it.
- **`Any`** — I don't know what this is, so you may do **anything** with it.

But the reason `Any` is the bluntest of the three hatches is **where the effect lands**. The word is on line 5. The errors it suppressed are on lines 11, 12, 13 and 14 — a different function, further down, and in every other file that ever calls `load_config`.

`cast` acts on the value you hand it. `# type: ignore` acts on the line it sits on. **`Any` leaves through the `return` and keeps suppressing wherever the value travels**, for as long as it is passed around. That is how a typed codebase quietly stops being typed: not by removing annotations, but by one `Any` at a boundary.

## The three, by reach

| | reach | verified at runtime? |
|---|---|---|
| `cast(T, v)` | one value | no |
| `# type: ignore[code]` | one line, one error code | no |
| `# type: ignore` | one line, **every** code, forever | no |
| `Any` | every line the value reaches | no |

Not one of them checks anything. They differ only in how much they switch off, and for how long — which is why the right instinct is always to reach for the narrowest one that solves the problem in front of you.

## When each one is right

Go back to the crash. `eh5.py` cast a dictionary that wasn't a `ToolCall` and blew up two frames later with `KeyError: 'args'`. There are two readings, and they lead to entirely different code:

1. `cast` was the right tool used correctly — the input was bad, bad input crashes, nothing to change.
2. `cast` was the wrong tool for that spot — something else belonged on that line.

It's the second. But the tempting reason is wrong, and worth getting straight: it is **not** that the bug should have been caught at check time. It could not have been. The dictionary arrives while the program is running, from a network call or a file or another service; mypy never sees it. No type system can inspect data that does not exist yet.

It should have been caught at the **boundary, at runtime** — the instant the data entered, not two frames later.

### Validate first, then `cast`

Same function, two checks added in front:

```python
13  def handle(payload: dict[str, object]) -> str:
14      if not isinstance(payload.get("name"), str):
15          raise ValueError(f"name must be a string, got {payload.get('name')!r}")
16      if not isinstance(payload.get("args"), dict):
17          raise ValueError(f"args must be a dict, got {payload.get('args')!r}")
18      call = cast(ToolCall, payload)
19      return dispatch(call)
20
21
22  print(handle({"name": "search", "args": {"q": "hi"}}))
23  print(handle({"name": "search"}))
```

```
$ mypy eh6.py
Success: no issues found in 1 source file
```

```
$ python3 eh6.py
search({'q': 'hi'})
Traceback (most recent call last):
  File "eh6.py", line 23, in <module>
  File "eh6.py", line 17, in handle
    raise ValueError(f"args must be a dict, got {payload.get('args')!r}")
ValueError: args must be a dict, got None
```

| | `eh5.py` | `eh6.py` |
|---|---|---|
| crashes at | line 10, inside `dispatch` | line 17, inside `handle` |
| says | `KeyError: 'args'` | `args must be a dict, got None` |
| distance from the bad data | two frames | zero |

Now the part worth sitting with. **Line 18 is the identical `cast` that lied in `eh5.py`** — character for character, still a no-op, still `return val`.

What changed is what sits above it. Lines 14-17 *establish* the claim, so line 18 stops being a guess and becomes a **record of a check that already happened**.

And it must be a `cast`, because this rung opened by proving narrowing cannot reach a `TypedDict`. You did the check by hand; `cast` is the only way to tell the checker you did.

> [!important] **`cast` is what you write *after* you validate, not *instead of* validating.**
>
> The same test applies to all three. A hatch is legitimate when it **records** a fact you established some other way, and illegitimate when it **substitutes** for establishing it.

### The decision procedure

Before reaching for any hatch, one question: *why does the checker disagree with me?* There are only a few answers, and each points somewhere different.

| the answer | what to do |
|---|---|
| It's right, I'm wrong | Fix the code. Most common case by far. |
| It can't see data that doesn't exist yet | **Validate at the boundary**, then `cast` |
| It has no type information for a library | Stubs (`22-Third-Party-Libraries`); `# type: ignore[import-untyped]` only if none exist |
| It has a genuine limitation here | `# type: ignore[code]`, with a comment saying why |
| I don't want to deal with this right now | `Any` — the one that charges interest |

## The best hatch is the one you don't need

Row two of that table said *validate at the boundary*. Hand-writing `isinstance` ladders is one way; at a real boundary there is a better one.

A `@dataclass` is **not** it — `25-Choosing-A-Structured-Data-Type` established that it generates `__init__`, `__repr__` and `__eq__` from the annotations and validates none of them. A validating model is:

```python
 1  from pydantic import BaseModel
 2
 3
 4  class ToolCall(BaseModel):
 5      name: str
 6      args: dict[str, str]
 7
 8
 9  def dispatch(call: ToolCall) -> str:
10      return f"{call.name}({call.args})"
11
12
13  def handle(payload: dict[str, object]) -> str:
14      call = ToolCall.model_validate(payload)
15      return dispatch(call)
```

```
$ mypy eh7.py
Success: no issues found in 1 source file
```

```
$ python3 eh7.py
search({'q': 'hi'})
...
pydantic_core._pydantic_core.ValidationError: 1 validation error for ToolCall
args
  Field required [type=missing, input_value={'name': 'search'}, input_type=dict]
```

**No `cast`, no `isinstance` ladder, no hatch of any kind.**

| | line 14 | on bad input |
|---|---|---|
| `eh5.py` | `cast(ToolCall, payload)` | `KeyError: 'args'`, two frames away |
| `eh6.py` | four `isinstance` lines, then `cast` | `ValueError: args must be a dict, got None` |
| `eh7.py` | `ToolCall.model_validate(payload)` | names the field, the reason, and the input it received |

`model_validate` **returns** a `ToolCall`. It is a real object of a real class, so mypy picks the type up from the return annotation in the ordinary way. No assertion is needed because a genuine check happened and produced a genuinely typed thing.

> [!important] Every hatch on this rung exists because the checker lacks information. Sometimes the fix is not to overrule it — it is to arrange for the information to actually exist.
>
> At a trust boundary that is nearly always the right move: **validate, don't assert.**

## What this concept claims

**The escape hatches are three ways to overrule the checker; not one of them checks anything, and they differ only in how much they switch off and for how long.**

Five things to carry:

1. Narrowing runs out when there is nothing on the object to test. A `TypedDict` is a plain `dict` at runtime — the class never stamps itself on what it builds — so `isinstance` against one is refused by mypy *and* by Python. That gap is what `cast` exists to fill.
2. `cast` is literally `return val`: a no-op that exists to be read by the checker, the same trick as an annotation in function form. It never validates, converts, or fails. A wrong one doesn't crash where you wrote it — it **relocates** the failure to a frame that no longer mentions the assumption that caused it.
3. `# type: ignore` acts on a **line**, not a value, which is why it handles errors with no value in them at all — a missing import being the common one. Bare, it silences every error code on that line forever, including ones that appear years later; write the code in brackets, which mypy prints at the end of every error so you never have to know them in advance.
4. `Any` is the bluntest because it **travels**. The word sits on one line; the suppression follows the value into every function and file that touches it. `Any` and `object` both mean *"I don't know what this is"* and draw opposite conclusions — `object` permits nothing, `Any` permits everything.
5. A hatch is legitimate when it **records** a fact established some other way, and illegitimate when it **substitutes** for establishing it. At a trust boundary the fact cannot be established at check time at all, so the answer is runtime validation — after which you usually need no hatch, because a validating model returns a genuinely typed object.
