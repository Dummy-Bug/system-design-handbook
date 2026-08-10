#python #type-hints #typing #typeddict #python-utils


`05-Built-In-Generics` ended on a failure it couldn't fix. A function returning a user record, annotated as honestly as `dict[K, V]` allows:

```python
 1  def create_user(name: str, age: int) -> dict[str, str | int | None]:
 2      return {"name": name, "age": age, "email": None}
 3
 4
 5  user = create_user("alice", 30)
 6
 7  print(user["name"].upper())     # flagged — and it works
 8  user["age"] = "thirty"          # silent — and it's a bug
 9  print(user["emial"])            # silent — KeyError at runtime
```

Three fields, three different types, and one `V` slot to describe them all. The result complained about the only correct line and said nothing about either bug.

The problem was never the syntax. `dict[K, V]` describes a mapping where **all values are alike**, and a record — fixed keys, each with its own type — is a different thing wearing a dictionary's clothes.

## Each key gets its own type

```python
 1  from typing import TypedDict
 2
 3
 4  class User(TypedDict):
 5      name: str
 6      age: int
 7      email: str | None
 8
 9
10  def create_user(name: str, age: int) -> User:
11      return {"name": name, "age": age, "email": None}
12
13
14  user = create_user("alice", 30)
15
16  print(user["name"].upper())
17  user["age"] = "thirty"
18  print(user["emial"])
```

Written as a class — but line 11 still returns a plain dictionary literal. No constructor call, no `User(...)`.

```
$ mypy td0.py

td0.py:17: error: Value of "age" has incompatible type "str"; expected "int"  [typeddict-item]

td0.py:18: error: TypedDict "User" has no key "emial"  [typeddict-item]
td0.py:18: note: Did you mean "email"?
```

**Line 16 is silent.** `user["name"].upper()` is correct code and no longer produces a complaint, because `"name"` is known to hold a `str` specifically rather than "one of three things".

**Line 17 is caught** — `"age"` expects an `int`.

**Line 18 is caught**, and it guesses the fix. The set of legal keys is known, so a typo is a type error rather than a runtime surprise.

Every verdict flipped:

| | `dict[str, str \| int \| None]` | `User` |
|---|---|---|
| `user["name"].upper()` — correct | **error** | fine |
| `user["age"] = "thirty"` — bug | fine | **error** |
| `user["emial"]` — typo | fine | **error** |

## At runtime it is a plain dict

```python
print(type(user))
print(isinstance(user, dict))
print(user)
print(User.__mro__)
```

```
$ python3 td1.py

<class 'dict'>
True
{'name': 'alice', 'age': 30, 'email': None}
(<class '__main__.User'>, <class 'dict'>, <class 'object'>)
```

`type(user)` is literally `dict`. Not a `User`, not a wrapper — the same dictionary you would have had anyway, printing the same way, costing the same.

The `class User(TypedDict)` syntax is a **description the checker reads**. Nothing is constructed at runtime and nothing is added to the object.

Read the last two lines together, because they say opposite-sounding things. `User.__mro__` proves the class genuinely exists and genuinely inherits from `dict` — and yet `type(user)` is `dict`, not `User`. Both are true: **the class is a construction-time convenience, and it never stamps itself on the object it builds.** You go in through `User`, you come out holding a plain dictionary that has no memory of it.

### Which is why you can never ask "is this a `User`?"

```python
12  print(isinstance(user, User))
```

```
$ mypy td_iso.py

td_iso.py:12: error: Cannot use isinstance() with TypedDict type  [misc]
```

```
$ python3 td_iso.py

TypeError: TypedDict does not support instance and class checks
```

Refused twice — by the checker *and* by Python itself, which is unusual; normally the checker objects to things Python would happily run.

The reason is the paragraph above. There is no mark on the object to look for. Two dictionaries with identical contents are indistinguishable, so the question has no answer to give. And `isinstance(user, dict)` — which *is* legal — returns `True` for every dictionary ever made, so it tells you nothing.

> [!important] A `TypedDict` is the one shape you cannot test for at runtime. Checking it properly would mean walking every key and every value, which is not what `isinstance` does — it follows `__mro__`, and `__mro__` has nothing to follow here.
>
> This is the gap that `23-Escape-Hatches` exists to fill: when you *know* a dict is a `User` and no check can prove it, `cast` is how you say so.

## It describes a shape; it never enforces one

Which matters most when the data arrives from outside:

```python
 1  import json
 2  from typing import TypedDict
 3
 4
 5  class User(TypedDict):
 6      name: str
 7      age: int
 8      email: str | None
 9
10
11  raw = '{"name": "alice", "age": "thirty", "shoe_size": 9}'
12  user: User = json.loads(raw)
13
14  print("loaded:", user)
15  print("keys:", list(user.keys()))
16  print(user["age"] + 1)
```

```
$ mypy td2.py

Success: no issues found in 1 source file
```

```
$ python3 td2.py

loaded: {'name': 'alice', 'age': 'thirty', 'shoe_size': 9}
keys: ['name', 'age', 'shoe_size']

Traceback (most recent call last):
  File "td2.py", line 16, in <module>
    print(user["age"] + 1)
TypeError: can only concatenate str (not "int") to str
```

Sitting in a variable annotated `User`:

- `age` is `'thirty'` — a string where the declaration says `int`
- `shoe_size` is present — a key `User` has never heard of
- `email` is **missing entirely** — a declared key with no value

Three violations, `Success` from the checker, and a crash four lines later.

The reason is the one from `08-Any-Object-Never`: `json.loads` returns `Any`, so `user: User = <Any>` is an **assertion**, not a check. That's the weakest of the three ways to type a boundary — it moves the lie into a single visible line without verifying anything.

> [!warning] **`TypedDict` describes a shape and never enforces one.** No object is constructed, no keys are inspected, no types are compared. Everything caught in the previous section was mypy reading source text, and none of it survives contact with data that arrives while the program is running.

That boundary is what makes the choice between `TypedDict` and something that validates at runtime a real decision rather than a preference — and that decision is its own rung.

## Keys that may be absent

Real records have fields that are sometimes not there at all — not a key holding `None`, but no key:

```python
 4  class User(TypedDict):
 5      name: str
 6      age: int
 7      email: str | None
 8
 9
10  a: User = {"name": "alice", "age": 30, "email": None}
11  b: User = {"name": "bob", "age": 25}
```

```
$ mypy td3.py

td3.py:11: error: Missing key "email" for TypedDict "User"  [typeddict-item]
```

`b` is rejected — and read the error: **`Missing key`**, not "wrong value". `str | None` made the *value* nullable and said nothing about whether the key has to exist.

### There are no defaults

The natural first attempt:

```python
7  email: str | None = None
```

```
$ mypy td4.py

td4.py:7: error: Right hand side values are not supported in TypedDict  [misc]
```

**A `TypedDict` cannot have defaults**, and it isn't an omission. There is nothing for a default to attach to: `User` never runs and never constructs anything, and the dictionary was built by a plain `{...}` literal with no involvement from `User` at all. **A default needs something doing the constructing**.

### `NotRequired`

The real mechanism marks the **key** optional rather than giving the value a default:

```python
 1  from typing import TypedDict, NotRequired
 2
 3
 4  class User(TypedDict):
 5      name: str
 6      age: int
 7      email: NotRequired[str | None]
 8
 9
10  a: User = {"name": "alice", "age": 30, "email": None}
11  b: User = {"name": "bob", "age": 25}
12  c: User = {"name": "carol", "age": 40, "email": "c@x.com"}
13  d: User = {"name": "dave"}
```

```
$ mypy td5.py

td5.py:13: error: Missing key "age" for TypedDict "User"  [typeddict-item]
```

Lines 10–12 all pass: email present as `None`, absent, or present as a string. Line 13 fails because `age` was never marked optional.

This is the two switches from `07-Unions-And-Optionality`, in a new setting:

|                | on a parameter           | on a `TypedDict` key     |
| -------------- | ------------------------ | ------------------------ |
| may be omitted | a **default**            | **`NotRequired`**        |
| may be `None`  | **\| None ** in the type | **\| None ** in the type |

- `email: str | None` — the key **must** be there; its value may be `None`.
- `email: NotRequired[str]` — the key may be **absent**; if present it's a `str`.
- `email: NotRequired[str | None]` — both.

Same independence, same trap: "optional field" means two different things and the declaration has to say which.

### The older spelling

`total=False` makes *every* key optional at once, and `Required[...]` marks the exceptions:

```python
 4  class Loose(TypedDict, total=False):
 5      name: Required[str]
 6      age: int
 7      email: str
 8
 9
10  a: Loose = {"name": "alice"}
11  b: Loose = {"age": 30}
```

```
$ mypy td6.py

td6.py:11: error: Missing key "name" for TypedDict "Loose"  [typeddict-item]
```

`a` passes with only `name`; `b` fails without it. Readable enough here, but it inverts the default for the whole class, so a reader has to check the class line before they can interpret any field. **`NotRequired` per key is what you'd write now** — the exception is marked where it applies.

## What this concept claims

**A `TypedDict` gives each key its own type, which is what a record needs and what `dict[K, V]` structurally cannot express — and it does so without creating anything at runtime.**

Four things to carry:

1. `dict[K, V]` is right for a mapping where all values are alike and wrong for a record. Forcing a record through it flags correct code and misses real bugs; `TypedDict` reverses every one of those verdicts, typos included.
2. It is **checker-only**. `type(user)` is `dict`, no object is built, nothing costs anything at runtime — and nothing is verified either.
3. Annotating a value that came from `json.loads` as a `TypedDict` is an assertion, not a check. Wrong types, missing keys and unknown keys all pass silently.
4. A key that may be absent is `NotRequired`, not a default — a `TypedDict` has no defaults, because nothing ever constructs one.
