#python #type-hints #typing #variance #python-utils

## A substitution that should obviously work

```python
 1  class Message: ...
 2  class HumanMessage(Message): ...
 3  class AIMessage(Message): ...
 4
 5
 6  def count(msgs: list[Message]) -> int:
 7      return len(msgs)
 8
 9
10  def one_message(m: Message) -> str:
11      return type(m).__name__
12
13
14  human_msgs: list[HumanMessage] = [HumanMessage(), HumanMessage()]
15
16  print(one_message(HumanMessage()))
17  print(count(human_msgs))
```

`HumanMessage` **is** a `Message` — line 2 says so — and `count` only takes a length.

```
$ mypy var0.py

var0.py:17: error: Argument 1 to "count" has incompatible type "list[HumanMessage]"; expected "list[Message]"  [arg-type]

var0.py:17: note: "list" is invariant -- see https://mypy.readthedocs.io/en/stable/common_issues.html#variance

var0.py:17: note: Consider using "Sequence" instead, which is covariant
```

**Line 16 passes. Line 17 fails.**

The ordinary subclass rule works fine on line 16 — a `HumanMessage` goes anywhere a `Message` is wanted. It stops applying the moment the value is inside a `list`. `HumanMessage` is a subtype of `Message`; `list[HumanMessage]` is **not** a subtype of `list[Message]`.

mypy names it: **`list` is invariant.**

## Why — the danger has to be findable

`count` only calls `len`, which is harmless. But the checker isn't reading the body, it's reading the **type** — and `list[Message]` permits appending. Here is a different function with the identical signature:

```python
 1  class Message:
 2      def __init__(self, text: str) -> None:
 3          self.text = text
 4
 5
 6  class HumanMessage(Message):
 7      def __init__(self, text: str, user_id: str) -> None:
 8          super().__init__(text)
 9          self.user_id = user_id
10
11
12  class AIMessage(Message):
13      def __init__(self, text: str, model: str) -> None:
14          super().__init__(text)
15          self.model = model
16
17
18  def add_reply(msgs: list[Message]) -> None:
19      msgs.append(AIMessage("hello", "opus"))
20
21
22  human_msgs: list[HumanMessage] = [HumanMessage("hi", "u1")]
23  add_reply(human_msgs)          # type: ignore[arg-type]
24
25  for m in human_msgs:
26      print(m.user_id)
```

A separate file, and the classes have grown. `var0.py`'s were empty — `class HumanMessage(Message): ...` — because nothing there needed a field. Here the crash *is* a missing field, so each subclass gets a real one: `user_id` on `HumanMessage`, `model` on `AIMessage`, and neither has the other's.

`add_reply` is legal on its own terms: an `AIMessage` **is** a `Message`, so appending one to a `list[Message]` is fine.

Silence the one error on line 23 and run it:

```
$ mypy var1.py
Success: no issues found in 1 source file
```

```
$ python3 var1.py
u1
Traceback (most recent call last):
  File "var1.py", line 26, in <module>
    print(m.user_id)
AttributeError: 'AIMessage' object has no attribute 'user_id'
```

`u1` from the genuine `HumanMessage`, then the loop reaches the `AIMessage` that `add_reply` put there.

> [!important] **`list[HumanMessage]` is not a `list[Message]` because a `list[Message]` can be written to.** Allowing it would let any function holding that parameter drop an `AIMessage` into your list of human messages — while doing nothing wrong, since an `AIMessage` really is a `Message`.
>
> Nothing in the signature distinguishes *"I will read this"* from *"I will replace its contents"*, so the checker assumes the worst. Same reasoning as unions in `07-Unions-And-Optionality`.

## All four combinations

One example proves one direction. Four near-identical functions, each differing in exactly one thing, prove the rest:

```python
 1  from collections.abc import Sequence
 2
 3
 4  class Message: ...
 5  class HumanMessage(Message): ...
 6
 7
 8  def takes_list_of_base(x: list[Message]) -> None: ...
 9  def takes_list_of_sub(x: list[HumanMessage]) -> None: ...
10  def takes_seq_of_base(x: Sequence[Message]) -> None: ...
11  def takes_seq_of_sub(x: Sequence[HumanMessage]) -> None: ...
12
13
14  list_of_base: list[Message] = []
15  list_of_sub: list[HumanMessage] = []
16
17  takes_list_of_base(list_of_sub)
18  takes_list_of_sub(list_of_base)
19
20  takes_seq_of_base(list_of_sub)
21  takes_seq_of_sub(list_of_base)
```

Lines 8–11 do nothing — `...` is an empty body. They exist only to have four different parameter types: a **list** of the base, a **list** of the sub, a **Sequence** of the base, a **Sequence** of the sub.

Lines 14–15 are two real variables, both empty. Only their declared types matter.

Lines 17–21 try one combination each.

```
$ mypy var3.py

var3.py:17: error: ... "list[HumanMessage]"; expected "list[Message]"  [arg-type]

var3.py:18: error: ... "list[Message]"; expected "list[HumanMessage]"  [arg-type]

var3.py:21: error: ... "list[Message]"; expected "Sequence[HumanMessage]"  [arg-type]
```

Rows are what you *have*, columns are what the function *wants*:

| have ↓ / wants → | `list[Message]` | `list[HumanMessage]` | `Sequence[Message]` | `Sequence[HumanMessage]` |
|---|---|---|---|---|
| `list[Message]` | — | **✗ 18** | — | **✗ 21** |
| `list[HumanMessage]` | **✗ 17** | — | **✓ 20** | — |

**One cell out of four works.** Each failure has its own concrete danger.

### Line 17 — `list[Sub]` into a `list[Base]` parameter · rejected

The parameter is a `list[Message]`, so the function may **append** any `Message` — including an `AIMessage`. Your `list[HumanMessage]` then holds something that isn't one, and the next loop crashes on `.user_id`.

**The danger is writing.** This is the crash demonstrated above.

### Line 18 — `list[Base]` into a `list[Sub]` parameter · rejected

The parameter is a `list[HumanMessage]`, so the function may **read** and expect `.user_id` on everything it finds. You handed it a list of plain `Message` objects, which have none.

**The danger is reading** — the exact mirror image.

> So `list` is unsafe in **both** directions for **two different reasons**. That is what *invariant* means: `list[X]` matches `list[X]` and nothing else, ever.

### Line 20 — `Sequence[Sub]` into a `Sequence[Base]` parameter · **accepted**

`Sequence` has no `append`, so line 17's danger cannot arise. Only reading is possible, and reading yields a `HumanMessage` where the function expects a `Message`.

**A `HumanMessage` is a `Message`.** Safe. This is covariance.

### Line 21 — `Sequence[Base]` into a `Sequence[Sub]` parameter · rejected

Still read-only, so no writing danger — but reading yields a `Message` where the function expects a `HumanMessage`.

**A `Message` is not a `HumanMessage`.** Unsafe.

## The rule that generates all of it

Line 20 and line 21 side by side:

| | reading gives you | function wants | ok? |
|---|---|---|---|
| line 20 | `HumanMessage` | `Message` | **yes** — a sub is always acceptable as a base |
| line 21 | `Message` | `HumanMessage` | no — a base is not acceptable as a sub |

**Reading is safe in exactly one direction: sub to base.** That's the same direction ordinary values follow — `one_message(HumanMessage())` worked in the very first demo — which is why covariance feels natural. It's the normal subclass rule surviving the trip through a container.

**Writing runs the other way.** Anything that can put values *in* accepts a `Base`, and a `Base` is precisely what must not end up in a container of `Sub`.

So:

- **read-only container** → only the read rule applies → sub-to-base is safe → **covariant**
- **writable container** → both rules apply, pointing opposite ways → nothing is safe → **invariant**

| | means | which types |
|---|---|---|
| **invariant** | `X[Sub]` is **not** an `X[Base]`, nor the reverse | `list`, `dict`, `set` — anything mutable |
| **covariant** | `X[Sub]` **is** an `X[Base]` | `Sequence`, `Iterable`, `Mapping`, `tuple` — read-only |

And the practical instruction, which is concept 6's advice with a reason attached:

> **Annotate a parameter `Sequence[Message]` when you're only going to read it.** You get every caller holding a list of any subclass for free, and the annotation simultaneously documents that you won't modify their data.

## The third kind — contravariance

Containers can only show two of the three. The third needs a function.

```python
 1  from collections.abc import Callable
 2
 3
 4  class Message: ...
 5  class HumanMessage(Message): ...
 6  class AIMessage(Message): ...
 7
 8
 9  def on_human_message(handler: Callable[[HumanMessage], None]) -> None:
10      handler(HumanMessage())
11
12
13  def handle_any(m: Message) -> None: ...
14  def handle_human(m: HumanMessage) -> None: ...
15  def handle_ai(m: AIMessage) -> None: ...
16
17
18  on_human_message(handle_any)
19  on_human_message(handle_human)
20  on_human_message(handle_ai)
```

Line 9 registers a callback; line 10 shows the only thing that will ever happen to it — **it gets called with a `HumanMessage`**. Lines 13–15 are three candidates differing only in what each accepts.

```
$ mypy var4.py

var4.py:20: error: Argument 1 to "on_human_message" has incompatible type "Callable[[AIMessage], None]"; expected "Callable[[HumanMessage], None]"  [arg-type]
```

**Lines 18 and 19 pass. Only line 20 fails.**

`handle_any`, which takes the **base** class, is accepted where a handler for the subclass was requested. That's the direction that looks wrong — and line 10 explains it:

- **`handle_any(m: Message)`** — receives a `HumanMessage`. Its parameter says `Message`, and a `HumanMessage` is one. It copes. ✓
- **`handle_human(m: HumanMessage)`** — receives exactly what it asked for. ✓
- **`handle_ai(m: AIMessage)`** — receives a `HumanMessage`. Its parameter says `AIMessage`, and a `HumanMessage` is not one. It would reach for `.model` and crash. ✗

> [!important] **A callback may accept *more* than it will be given, never less.** `handle_any` handles every `Message`, so it certainly handles the `HumanMessage` about to arrive. `handle_ai` handles less than will arrive.

That's **contravariance**: in the *parameter* position, substitution runs the opposite way — the base class is accepted where the subclass was expected.

It is the same read/write rule seen from the other end. A function's parameter is a place values get **written into**, and writing was always the direction that ran backwards.

## The three rules without arrows

Two words, defined once:

- **Wider** — covers more kinds of thing. `Message` is wider than `HumanMessage`: every human message is a message, *and* so are AI messages, *and* so are plain ones.
- **Narrower** — covers fewer kinds, and therefore guarantees more attributes. `HumanMessage` is narrower, and it's the only one with `.user_id`.

The base class is always the wider one. Each rule is phrased identically — *you have this; can you pass it where that is wanted?*

**1. A read-only container: you may pass a narrower one.**
You have `Sequence[HumanMessage]`; the function wants `Sequence[Message]`. **Yes.**
*Why:* it will read and get a `HumanMessage`. It expected a `Message`. A `HumanMessage` is one.

**2. A function's parameter: you may pass one that accepts a wider type.**
You have `Callable[[Message], None]`; the function wants `Callable[[HumanMessage], None]`. **Yes.**
*Why:* it will be called with a `HumanMessage`. Yours accepts any `Message`, so it copes.

**3. A function's return: you may pass one that returns a narrower type.**
You have `Callable[..., HumanMessage]`; the function wants `Callable[..., Message]`. **Yes.**
*Why:* the caller will use the result as a `Message`. You handed back a `HumanMessage`, which is one.

Rules 1 and 3 are the same rule — **the thing you receive may be narrower than promised.** Rule 2 is its mirror — **the thing you accept may be wider than promised.**

### Both rules at once

```python
 1  from collections.abc import Callable
 2
 3
 4  class Message: ...
 5  class HumanMessage(Message): ...
 6  class AIMessage(Message): ...
 7
 8
 9  def sink(handler: Callable[[HumanMessage], Message]) -> None: ...
10
11
12  def h1(m: Message) -> HumanMessage: ...
13  def h2(m: HumanMessage) -> Message: ...
14  def h3(m: AIMessage) -> HumanMessage: ...
15
16
17  sink(h1)
18  sink(h2)
19  sink(h3)
```

```
$ mypy var5.py

var5.py:19: error: Argument 1 to "sink" has incompatible type "Callable[[AIMessage], HumanMessage]"; expected "Callable[[HumanMessage], Message]"  [arg-type]
```

(mypy also reports `Missing return statement` three times, because `...` bodies don't return. Noise.)

| | its parameter | vs `HumanMessage` | its return | vs `Message` | verdict |
|---|---|---|---|---|---|
| `h1` | `Message` | **wider** ✓ rule 2 | `HumanMessage` | **narrower** ✓ rule 3 | **accepted** |
| `h2` | `HumanMessage` | same ✓ | `Message` | same ✓ | **accepted** |
| `h3` | `AIMessage` | **narrower** ✗ | `HumanMessage` | narrower ✓ | **rejected** |

`h1` is better than required on both counts — it takes anything that could be thrown at it and returns something more specific than needed. That's exactly why it's safe, and it's the case that feels wrong until checked against what actually happens.

`h3`'s return is fine. It fails purely on the parameter: it will be handed a `HumanMessage` and only knows how to handle an `AIMessage`.

So `Callable` is **contravariant in its parameters and covariant in its return** — a single type expressing both directions at once.

## What this concept claims

**One rule generates all three names: values you receive may be narrower than promised, values you accept must be wider.**

Four things to carry:

1. The ordinary subclass rule stops at the container boundary. `HumanMessage` is a `Message`; `list[HumanMessage]` is not a `list[Message]`.
2. `list`, `dict` and `set` are **invariant** because they can be both read and written, and those two dangers point in opposite directions. `list[X]` matches `list[X]` and nothing else.
3. `Sequence`, `Iterable`, `Mapping` and `tuple` are **covariant** because they can only be read — so a container of a subclass is safely a container of the base.
4. Function parameters are **contravariant**: a handler accepting `Message` is valid where one accepting `HumanMessage` was asked for, because it will only ever be handed a `HumanMessage` and it copes with more than that.

The everyday consequence is one line: **when a parameter is only read, annotate it `Sequence[...]` or `Iterable[...]` rather than `list[...]`** — and now you can say why, which is the form the question takes in an interview.
