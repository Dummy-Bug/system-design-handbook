#python #type-hints #typing #any #python-utils

## Two ways to say "anything"

```python
 1  from typing import Any
 2
 3
 4  def show_any(x: Any) -> None:
 5      print(x.upper())
 6
 7
 8  def show_obj(x: object) -> None:
 9      print(x.upper())
10
11
12  show_any("hello")
13  show_any(42)
14  show_obj("hello")
15  show_obj(42)
```

Lines 5 and 9 are the same statement. Both parameters accept a string and an integer, so none of the four calls is a type error.

```
$ mypy anyobj.py

anyobj.py:9: error: "object" has no attribute "upper"  [attr-defined]
Found 1 error in 1 file (checked 1 source file)
```

```
$ python3 anyobj.py
HELLO
Traceback (most recent call last):
  File "anyobj.py", line 13, in <module>
    show_any(42)
  File "anyobj.py", line 5, in show_any
    print(x.upper())
AttributeError: 'int' object has no attribute 'upper'
```

**One error, on line 9** — inside `show_obj`, the `object` version. Line 5 is the identical statement inside `show_any` and is never mentioned.

**And line 5 is the one that crashed.** `HELLO` came from line 12; line 13 called `show_any(42)` and died inside line 5, the exact line the checker declined to flag. Lines 14 and 15 never ran.

| line | annotation | mypy | runtime |
|---|---|---|---|
| 5 | `x: Any` | silent | **crashed** |
| 9 | `x: object` | **error** | never reached |

## Same on the way in, opposite on the way out

| | who can be passed in | what you can do with it |
|---|---|---|
| `Any` | anything | **anything** — every operation allowed |
| `object` | anything | **almost nothing** — only what every value supports |

**`object` is the top of the hierarchy.** Every value in Python is one, `None` included. So it accepts everything honestly, and then permits only the operations *every* value supports — `str()`, `repr()`, `==`, `hash()`. Not `.upper()`, because integers exist. It forces you to narrow before doing anything, which is why line 9 is an error and a correct one.

**`Any` is not a type at all — it's a switch.** It says *stop checking this*. Every operation is permitted because none is examined: `x.upper()`, `x + 1`, `x[0]`, `x.fly_to_the_moon()` — all fine, all unexamined.

> [!important] **Reaching for `Any` is a decision to stop type-checking a region of code, not a description of the data.** `object` describes the data. `Any` describes your intention to stop looking.

## What the error on line 9 actually says

It's easy to read `"object" has no attribute "upper"` as *this line is broken*. It isn't. Delete the call that crashed and run the rest:

```python
 1  from typing import Any
 2
 3
 4  def show_any(x: Any) -> None:
 5      print(x.upper())
 6
 7
 8  def show_obj(x: object) -> None:
 9      print(x.upper())
10
11
12  show_any("hello")
13  show_obj("hello")
14  show_obj(42)
```

```
$ mypy anyobj2.py
anyobj2.py:9: error: "object" has no attribute "upper"  [attr-defined]

$ python3 anyobj2.py
HELLO
HELLO
Traceback (most recent call last):
  File "anyobj2.py", line 14, in <module>
    show_obj(42)
  File "anyobj2.py", line 9, in show_obj
    print(x.upper())
AttributeError: 'int' object has no attribute 'upper'
```

Two `HELLO`s. The first is line 12; **the second is line 13, which ran straight through line 9 — the line mypy calls an error — with no problem at all.** Then line 14 passed `42` and line 9 failed.

So the message means:

> **"You promised `x` could be any object, and this line is not safe for every object."**

It's about the gap between what you claimed to accept and what you then did with it — reported once, at the definition, without a single caller existing. Line 9 works for strings and fails for integers, and since the annotation said "any object", both are in scope.

Which sharpens the contrast:

- **Line 9 (`object`)** — flagged once at the definition. You then narrow (`if isinstance(x, str):`) or change the annotation. Both fixes are honest.
- **Line 5 (`Any`)** — never flagged, for any caller, ever. Identical statement, identical risk, silence.

> [!warning] None of this is a *compile-time* error. Compiling asks only *is this well-formed Python?*, and both files compile perfectly. mypy is a separate program you choose to run, reading the text — not a phase of running your file. Skip it, and line 9's error does not exist as far as your program is concerned.
>
> | | when it happens | what it checks |
> |---|---|---|
> | mypy | when you run `mypy file.py` | your claims against your code |
> | compile | every `python3 file.py` | is this well-formed Python |
> | execute | after compiling | does this actually work |

## Where `Any` is the honest answer

`Any` isn't a mistake, and it isn't rare. `json.loads` takes text and returns whatever was in it:

```
$ python3 json_types.py

{"retries": 3}     -> dict
[1, 2, 3]          -> list
"hello"            -> str
42                 -> int
null               -> NoneType
```

One function, five return types, decided entirely by text that arrives while the program runs. A checker reads source; it cannot read a file nobody has opened yet. There is no honest single type to write, so `json.loads` is annotated `-> Any`.

**That is `Any` used correctly** — at a genuine boundary where the type is unknowable until runtime. Every codebase has a few: JSON, YAML, config files, anything off a network.

## `Any` spreads

Which would be fine if it stayed where you put it.

```python
 1  import json
 2  from typing import Any
 3
 4
 5  def load_config() -> Any:
 6      return json.loads('{"retries": 3}')
 7
 8
 9  cfg = load_config()
10  retries = cfg["retries"]
11  timeout = retries.upper()
12  delay = timeout + [1, 2, 3]
13  print(delay.nonexistent_method())
```

`Any` appears exactly once, on line 5. Lines 9–13 carry no annotations at all — ordinary variables, assigned from ordinary operations. Line 11 calls `.upper()` on a number, line 12 adds a list to a string, line 13 calls a method that does not exist.

```
$ mypy spread.py
Success: no issues found in 1 source file
```

**Zero errors.**

Change line 5's return annotation and nothing else:

```python
 1  import json
 2
 3
 4  def load_config() -> dict[str, int]:
 5      return json.loads('{"retries": 3}')
 6
 7
 8  cfg = load_config()
 9  retries = cfg["retries"]
10  timeout = retries.upper()
11  delay = timeout + [1, 2, 3]
12  print(delay.nonexistent_method())
```

```
$ mypy spread2.py
spread2.py:10: error: "int" has no attribute "upper"  [attr-defined]
```

Caught at line 10, the first genuinely wrong operation. One annotation at the boundary, and the whole chain below it became checkable.

The mechanism is mechanical:

| line | expression | its type |
|---|---|---|
| 9 | `load_config()` | `Any` — you said so |
| 10 | `cfg["retries"]` | indexing an `Any` → **`Any`** |
| 11 | `retries.upper()` | attribute on an `Any` → **`Any`** |
| 12 | `timeout + [1, 2, 3]` | arithmetic on an `Any` → **`Any`** |
| 13 | `delay.nonexistent_method()` | attribute on an `Any` → **`Any`** |

**Every operation on an `Any` produces another `Any`.** There is no step where the checker recovers. One `Any` at the top of a chain switches off checking for everything downstream — across function boundaries, through variables nobody annotated — and reports `Success` the whole way.

> [!warning] That's the real cost, and why `Any` is not merely "permissive". `object` is permissive and **contained** — it stops you at the point of use. `Any` is permissive and **contagious** — it removes checking from code you never wrote it on.

You can watch it happen with `reveal_type`, which asks mypy what it believes a value is:

```python
 1  import json
 2
 3
 4  def load_config() -> dict[str, int]:
 5      return json.loads('{"retries": 3}')
 6
 7
 8  cfg = load_config()
 9  reveal_type(cfg)
10
11  retries = cfg["retries"]
12  reveal_type(retries)
13
14  timeout = retries.upper()
15  reveal_type(timeout)
16
17  delay = timeout + [1, 2, 3]
18  reveal_type(delay)
```

```
$ mypy spread3.py

spread3.py:9:  note: Revealed type is "dict[str, int]"
spread3.py:12: note: Revealed type is "int"

spread3.py:14: error: "int" has no attribute "upper"  [attr-defined]

spread3.py:15: note: Revealed type is "Any"
spread3.py:18: note: Revealed type is "Any"

Found 1 error in 1 file (checked 1 source file)
```

Line 9 knows the dict. Line 12 correctly derives `int` from its value type. Line 14 is the one real error — and from line 15 onward everything is `Any` again, so line 17's list-plus-string is **never checked**.

That's the same spreading rule, this time coming from mypy's own error handling: a failed expression becomes `Any` so errors don't cascade. Fix line 14 and the next error appears. You get them one at a time.

## Typing the boundary

The fix is what the two files already showed: `Any` is unavoidable at the edges, where data arrives from outside and its type genuinely isn't knowable from source. The rule is to **let it exist at the edge and nowhere else** — convert it to a real type at the point of entry so everything inward is checkable.

Three ways to spell that, weakest to strongest:

1. **Annotate the variable** — `cfg: dict[str, int] = json.loads(...)`. You assert the shape; nothing verifies it.
2. **`cast()`** — the same assertion, stated explicitly, with no runtime effect. Its own rung later.
3. **Validate it** — hand the `Any` to something that checks at runtime and returns a real object.

Only the third is a guarantee. The first two move the lie from many lines to one line, which is still a large improvement: the assumption is now written down in a single place where a reader can see it and a reviewer can question it.

## `Never` — the type with no values

The third extreme type, and the odd one.

```python
 1  from typing import Never
 2
 3
 4  def crash(msg: str) -> Never:
 5      raise ValueError(msg)
 6
 7
 8  def get_port(cfg: dict[str, int]) -> int:
 9      port = cfg.get("port")
10      if port is None:
11          crash("no port configured")
12      return port
```

```
$ mypy never1.py
Success: no issues found in 1 source file
```

Line 12 returns `port`, which line 9 made `int | None`. Line 10 catches the `None` case — but line 11 doesn't `return` and doesn't `raise`. It just calls a function. And yet the file passes.

Change one word, the return annotation on line 4, and nothing else:

```python
1  def crash(msg: str) -> None:
2      raise ValueError(msg)
3
4
5  def get_port(cfg: dict[str, int]) -> int:
6      port = cfg.get("port")
7      if port is None:
8          crash("no port configured")
9      return port
```

```
$ mypy never2.py

never2.py:9: error: 
Incompatible return value type (got "int | None", expected "int")  [return-value]
```

**With `-> None`:** the checker believes `crash` returns normally having produced nothing. So line 8 runs, control falls out of the `if`, and reaches line 9 with `port` still possibly `None`. A correct complaint, given what it was told.

**With `-> Never`:** the checker knows `crash` never returns at all. Line 11 is therefore the end of that branch — control cannot get from there to line 12. The only way to reach `return port` is the path where `port is None` was false, and on that path `port` is an `int`. That's narrowing, working through a function call.

> [!important] `-> None` means *"it returns, and the value is nothing."* `-> Never` means *"it does not return."* Two completely different claims, and only the second lets the checker eliminate a branch.

`Never` has no values. You cannot make one, no variable can hold one, no function can successfully return one — which sounds useless until you notice that "no value can exist here" is a statement with real content: **this cannot happen.**

### It changes nothing at runtime

The exception behaves exactly as it always did:

```python
 1  from typing import Never
 2
 3
 4  def crash(msg: str) -> Never:
 5      raise ValueError(msg)
 6
 7
 8  def get_port(cfg: dict[str, int]) -> int:
 9      port = cfg.get("port")
10      if port is None:
11          crash("no port configured")
12      print("THIS LINE NEVER RUNS when port is missing")
13      return port
14
15
16  print(get_port({"port": 8080}))
17  print(get_port({}))
```

```
$ python3 neverrun.py

THIS LINE NEVER RUNS when port is missing
8080
Traceback (most recent call last):
  File "neverrun.py", line 17, in <module>
    print(get_port({}))
  File "neverrun.py", line 11, in get_port
    crash("no port configured")
  File "neverrun.py", line 5, in crash
    raise ValueError(msg)
ValueError: no port configured
```

The exception propagates normally — **three frames**: line 17 called `get_port`, line 11 called `crash`, line 5 raised. It travels straight out and kills the program.

And the run confirms the checker's reasoning. Line 16, port present: line 12 printed and line 13 returned `8080`. Line 17, port missing: **line 12 did not print.** Control left at line 11 and never came back.

So `Never` is a *true description of behaviour the code already had*. The function always raises, therefore it never returns, therefore anything after a call to it is unreachable. Without the annotation the checker was assuming `crash` might return normally, which was simply false.

### And it's verified, not trusted

```python
1  from typing import Never
2
3
4  def crash(msg: str) -> Never:
5      if msg == "":
6          return
7      raise ValueError(msg)
```

```
$ mypy liar.py
liar.py:6: error: Return statement in function which does not return  [misc]
```

Declaring `-> Never` and then having a path that returns is a contradiction, and line 6 is caught.

## What this concept claims

**`Any` and `object` both accept everything and are opposites about what you may then do; `Never` accepts nothing and is how you say a thing cannot happen.**

Four things to carry:

1. `object` describes the data — everything is one, and you may only do what every value supports, so it forces you to narrow. `Any` describes your intention to stop checking, and permits every operation because it examines none.
2. `Any` is **contagious**. Every operation on an `Any` yields another `Any`, so a single one at the top of a chain silently disables checking for everything downstream, and the checker reports success throughout.
3. `Any` at a real boundary is correct — JSON, config, network. The discipline is **typing the boundary**: convert it to a real type at the point of entry so it cannot spread inward.
4. `-> None` and `-> Never` are different claims. "Returns nothing" versus "does not return" — and only the second lets the checker rule a branch out.

