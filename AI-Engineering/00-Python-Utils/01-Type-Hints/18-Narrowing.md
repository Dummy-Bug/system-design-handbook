#python #type-hints #typing #narrowing #typeis #python-utils


`07-Unions-And-Optionality` introduced narrowing on one case — `if text is None:` — and left the general form open. This is that form: how a checker learns a variable's type inside a branch, and how to teach it the same thing about a check of your own.

## A union that can't be read

Two message types, the shape of any agent's message handling:

```python
 1  class HumanMessage:
 2      def __init__(self, text: str) -> None:
 3          self.text = text
 4
 5
 6  class ToolMessage:
 7      def __init__(self, tool_name: str, result: str) -> None:
 8          self.tool_name = tool_name
 9          self.result = result
10
11
12  def render(msg: HumanMessage | ToolMessage) -> str:
13      return msg.text
```

```
$ mypy nr0.py
nr0.py:13: error: Item "ToolMessage" of "HumanMessage | ToolMessage" has no attribute "text"  [union-attr]
```

The message names the offending member — `Item "ToolMessage" of "HumanMessage | ToolMessage"` — and `[union-attr]` is the error code for exactly this. A union permits only what **every** member permits, and `ToolMessage` has no `.text`.

> [!info] A `Protocol` does not fix this. It would let `render` accept anything with a `.text`, but then `ToolMessage` fails to qualify at all — it has `tool_name` and `result`, and describing shapes cannot give it a `.text` it doesn't have.
>
> The problem isn't *what do these share*. It's that they genuinely differ and each needs its own code.

## `isinstance` narrows both branches

```python
 1  class HumanMessage:
 2      def __init__(self, text: str) -> None:
 3          self.text = text
 4
 5
 6  class ToolMessage:
 7      def __init__(self, tool_name: str, result: str) -> None:
 8          self.tool_name = tool_name
 9          self.result = result
10
11
12  def render(msg: HumanMessage | ToolMessage) -> str:
13      reveal_type(msg)
14      if isinstance(msg, HumanMessage):
15          reveal_type(msg)
16          return msg.text
17      reveal_type(msg)
18      return f"{msg.tool_name} -> {msg.result}"
```

```
$ mypy nr1.py
nr1.py:13: note: Revealed type is "nr1.HumanMessage | nr1.ToolMessage"
nr1.py:15: note: Revealed type is "nr1.HumanMessage"
nr1.py:17: note: Revealed type is "nr1.ToolMessage"
Success: no issues found in 1 source file
```

One variable, three types, three places in one function.

- **13** — before the check: the full union.
- **15** — inside the `if`: `HumanMessage`.
- **17** — after it: `ToolMessage`.

Line 17 is the half people miss. `isinstance` narrows **both** branches: inside, `msg` is what you tested for; outside, it's everything else the union allowed. Two members, one ruled out, one left — which is why line 18 reads `.tool_name` with no check of its own.

`Never` would be the answer only if every member had been eliminated.

## Factoring the check out breaks it

Real code names a check once and calls it from three places:

```python
 1  class HumanMessage:
 2      def __init__(self, text: str) -> None:
 3          self.text = text
 4
 5
 6  class ToolMessage:
 7      def __init__(self, tool_name: str, result: str) -> None:
 8          self.tool_name = tool_name
 9          self.result = result
10
11
12  def is_tool(msg: HumanMessage | ToolMessage) -> bool:
13      return isinstance(msg, ToolMessage)
14
15
16  def render(msg: HumanMessage | ToolMessage) -> str:
17      if is_tool(msg):
18          reveal_type(msg)
19          return msg.result
20      return msg.text
```

Line 13 is the identical check, moved into a function.

```
$ mypy nr2.py
nr2.py:18: note: Revealed type is "nr2.HumanMessage | nr2.ToolMessage"
nr2.py:19: error: Item "HumanMessage" of "HumanMessage | ToolMessage" has no attribute "result"  [union-attr]
nr2.py:20: error: Item "ToolMessage" of "HumanMessage | ToolMessage" has no attribute "text"  [union-attr]
```

**Line 18 is still the full union**, and both branches now fail — the same two errors the concept opened with.

The difference is **what the checker can see on line 17**.

With the check written inline, it sees the literal form `isinstance(msg, ToolMessage)` and knows what that implies about `msg`. With the check in a function, line 17 is a call, and to interpret it mypy looks at what `is_tool` is *declared* to return: `bool`.

And a `bool` says only `True` or `False`. It doesn't say **which** check produced it or **which variable** it concerned. `is_tool(msg)` and `len(x) > 0` have the same type; there is nothing to tell them apart.

The check still ran — Python branched correctly the whole time. Only the checker lost track, because the annotation stopped describing what the function establishes.

### Why the checker won't just read the body

The obvious objection is that a human reading `is_tool` can see what it does. Two reasons mypy doesn't use that.

**Often there is no body.**

```python
 1  from collections.abc import Callable
 2
 3
 4  class HumanMessage:
 5      def __init__(self, text: str) -> None:
 6          self.text = text
 7
 8
 9  class ToolMessage:
10      def __init__(self, tool_name: str, result: str) -> None:
11          self.tool_name = tool_name
12          self.result = result
13
14
15  def render(
16      msg: HumanMessage | ToolMessage,
17      check: Callable[[HumanMessage | ToolMessage], bool],
18  ) -> str:
19      if check(msg):
20          return msg.result
21      return msg.text
```

```
$ mypy nr4.py
nr4.py:20: error: Item "HumanMessage" of "HumanMessage | ToolMessage" has no attribute "result"  [union-attr]
nr4.py:21: error: Item "ToolMessage" of "HumanMessage | ToolMessage" has no attribute "text"  [union-attr]
```

`check` is a **parameter** — the caller supplies whatever function they like, and there is no body anywhere to inspect. The same holds for anything imported from a library you don't have source for.

**And if it did read bodies, editing one would break its callers invisibly.** Narrowing at a call site would then depend on the current implementation, so a change inside `is_tool` would silently alter what type-checks in every file that calls it, including files in other packages.

> [!important] **A call site is checked from the signature alone.** So anything callers need to know has to be *in* the signature.
>
> Same lesson as `13-TypeVar-And-Generic-Functions`, where `list[Any] -> Any` was true and useless while `list[T] -> T` put the relationship where callers could use it.

## `TypeIs` puts it back in the signature

One change — the return type:

```python
 1  from typing import TypeIs
 2
 3
 4  class HumanMessage:
 5      def __init__(self, text: str) -> None:
 6          self.text = text
 7
 8
 9  class ToolMessage:
10      def __init__(self, tool_name: str, result: str) -> None:
11          self.tool_name = tool_name
12          self.result = result
13
14
15  def is_tool(msg: HumanMessage | ToolMessage) -> TypeIs[ToolMessage]:
16      return isinstance(msg, ToolMessage)
17
18
19  def render(msg: HumanMessage | ToolMessage) -> str:
20      if is_tool(msg):
21          reveal_type(msg)
22          return msg.result
23      reveal_type(msg)
24      return msg.text
```

Line 16 is untouched; the function still returns `True` or `False` at runtime. The annotation now says one thing more: **when this returns `True`, the argument is a `ToolMessage`.**

```
$ mypy nr3.py
nr3.py:21: note: Revealed type is "nr3.ToolMessage"
nr3.py:23: note: Revealed type is "nr3.HumanMessage"
Success: no issues found in 1 source file
```

```
$ python3 nr3_run.py
hi
3 results
```

Line 21 is `ToolMessage`, line 23 is `HumanMessage` — identical to the inline `isinstance` version, both branches narrowed. The runtime behaviour never changed at any point in this note; only the annotation did.

That is the sentence `-> bool` could not express: not merely that something is true, but **what** is true and **about which argument**.

## `TypeGuard` — the older one, and what it leaves out

`TypeIs` arrived in 3.13. Before it there was `TypeGuard`, which you'll meet in existing code. Same file as above, one word different:

```python
 1  from typing import TypeGuard
 2
 3
 4  class HumanMessage:
 5      def __init__(self, text: str) -> None:
 6          self.text = text
 7
 8
 9  class ToolMessage:
10      def __init__(self, tool_name: str, result: str) -> None:
11          self.tool_name = tool_name
12          self.result = result
13
14
15  def is_tool(msg: HumanMessage | ToolMessage) -> TypeGuard[ToolMessage]:
16      return isinstance(msg, ToolMessage)
17
18
19  def render(msg: HumanMessage | ToolMessage) -> str:
20      if is_tool(msg):
21          reveal_type(msg)
22          return msg.result
23      reveal_type(msg)
24      return msg.text
```

```
$ mypy nr5.py
nr5.py:21: note: Revealed type is "nr5.ToolMessage"
nr5.py:23: note: Revealed type is "nr5.HumanMessage | nr5.ToolMessage"
nr5.py:24: error: Item "ToolMessage" of "HumanMessage | ToolMessage" has no attribute "text"  [union-attr]
```

**Line 21 narrows; line 23 does not.** Inside the `if` it behaves exactly like `TypeIs`. The `else` side stays the full union, so line 24 fails.

`TypeGuard` claims *"if this returns `True`, the argument is a `ToolMessage`"* — and says nothing about `False`. So when the check fails, the checker still considers `ToolMessage` possible: it knows the predicate said no, not that the type was excluded.

| | `TypeGuard[T]` | `TypeIs[T]` |
|---|---|---|
| `if` branch | narrows to `T` | narrows to `T` |
| `else` branch | **unchanged** | narrows to everything else in the union |
| requires `T` to be a subtype of the input | no | **yes** |
| since | 3.10 | 3.13 |

### Why `TypeGuard` still exists

`TypeIs` does strictly more in the case above, so the third row is what keeps `TypeGuard` alive:

```python
4  def all_strings_is(items: list[object]) -> TypeIs[list[str]]:
5      return all(isinstance(i, str) for i in items)
...
8  def all_strings_guard(items: list[object]) -> TypeGuard[list[str]]:
9      return all(isinstance(i, str) for i in items)
...
13     if all_strings_guard(items):
14         reveal_type(items)
15         print(" ".join(items))
16     reveal_type(items)
```

```
$ mypy nr6.py
nr6.py:4: error: Narrowed type "list[str]" is not a subtype of input type "list[object]"  [narrowed-type-not-subtype]
nr6.py:14: note: Revealed type is "list[str]"
nr6.py:16: note: Revealed type is "list[object]"
```

**Line 4 is rejected**, and the reason is `15-Variance`: `list` is invariant, so `list[str]` is not a subtype of `list[object]`, however obviously every element is a string.

`TypeIs` needs that subtype relationship *because* it narrows both branches. To say "on `False`, subtract `T` from the input type", the two have to be related — subtracting something that was never part of the input means nothing.

`TypeGuard` carries no such requirement, and lines 14 and 16 show it working: narrowed to `list[str]` inside, untouched `list[object]` outside. Claiming only the `True` case lets it narrow to any type at all.

> [!important] **`TypeIs` for a genuine subtype — which is nearly always, so make it the default.** `TypeGuard` when the narrowed type isn't a subtype of the input, which in practice means containers: `list[object]` → `list[str]`, `dict[str, Any]` → a `TypedDict`.

## Neither is verified

```python
 1  from typing import TypeIs
 2
 3
 4  class HumanMessage:
 5      def __init__(self, text: str) -> None:
 6          self.text = text
 7
 8
 9  class ToolMessage:
10      def __init__(self, tool_name: str, result: str) -> None:
11          self.tool_name = tool_name
12          self.result = result
13
14
15  def is_tool(msg: HumanMessage | ToolMessage) -> TypeIs[ToolMessage]:
16      return True
17
18
19  def render(msg: HumanMessage | ToolMessage) -> str:
20      if is_tool(msg):
21          return msg.result
22      return msg.text
23
24
25  print(render(HumanMessage("hi")))
```

Line 16 returns `True` for anything. Line 25 passes a `HumanMessage`. The `reveal_type` calls are gone, which is why `return msg.result` has moved up to line 21.

```
$ mypy nr7.py
Success: no issues found in 1 source file
```

```
$ python3 nr7.py
Traceback (most recent call last):
  File "nr7.py", line 25, in <module>
    print(render(HumanMessage("hi")))
  File "nr7.py", line 21, in render
    return msg.result
AttributeError: 'HumanMessage' object has no attribute 'result'
```

`Success`, then a crash. mypy checked nothing about the body — `return True` satisfies `TypeIs[ToolMessage]` as far as it is concerned, and every call site then narrows on a lie.

> [!important] `TypeIs` and `TypeGuard` are **promises you make**, not facts the checker verifies. The body must actually establish what the annotation claims, and nothing confirms that it does.
>
> The practical rule is short: **keep the body to a real check** — an `isinstance`, a tag comparison, a key test. Once the body gets clever, you have built a hole with a type annotation over it.

## What this concept claims

**Narrowing is the checker tracking a variable's type through branches, and it works on forms it can see — so a check you factor into a function has to state its result in the signature.**

Four things to carry:

1. A union permits only what every member permits; reading an attribute that isn't on all of them is `[union-attr]`. `isinstance` narrows **both** branches — inside to what you tested for, outside to whatever the union has left.
2. Wrapping that same check in a function returning `bool` destroys the narrowing, because a call site is checked from the signature alone and `bool` records neither which check nor which variable.
3. That rule isn't an implementation shortcut: the body often doesn't exist to be read (a `Callable` parameter, an untyped import), and reading bodies would make a change inside a function silently alter what type-checks in every file that calls it.
4. `TypeIs[T]` puts the fact back in the signature and narrows both branches; `TypeGuard[T]` narrows only the positive one but accepts a narrowed type that isn't a subtype of the input. Neither is verified against its body — they are assertions, in the same family as the escape hatches.
