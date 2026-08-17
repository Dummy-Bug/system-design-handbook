#python #type-hints #typing #newtype #python-utils


Two ways to give a type a name. They look the same, they're written almost the same, and only one of them changes what the checker will catch.

## A bug that nothing catches

An agent runtime deals in identifiers. A conversation has a thread id; an execution has a run id. Both are strings.

```python
 1  def get_history(thread_id: str) -> list[str]:
 2      return [f"messages in {thread_id}"]
 3
 4
 5  def get_run_status(run_id: str) -> str:
 6      return f"status of {run_id}"
 7
 8
 9  thread = "thread-abc123"
10  run = "run-xyz789"
11
12  print(get_history(run))
13  print(get_run_status(thread))
```

Lines 12 and 13 have them **swapped** — history fetched for a run id, status fetched for a thread id.

```
$ mypy nt0.py

Success: no issues found in 1 source file
```

```
$ python3 nt0.py

['messages in run-xyz789']
status of thread-abc123
```

**No error and no crash.** Both calls succeed and return confident, well-formed, entirely wrong answers.

That's the shape of this bug class. There is nothing for the runtime to object to — a string is a string — and the consequences are real: a store that isolates conversations by thread id, handed the wrong kind of string, is how one user's history ends up in another user's reply.

### Naming the parameters doesn't help

The parameters are already called `thread_id` and `run_id`, which is as clear as English gets. It buys nothing, because **parameter names are not part of a type.** mypy is comparing `str` with `str`; the names are labels for human readers, in the same category as the capitals on `MAX_RETRIES` in `09-Literal-Final-ClassVar`.

## Aliases don't help either

The obvious move is to give each identifier its own name:

```python
 1  ThreadId = str
 2  RunId = str
 3
 4
 5  def get_history(thread_id: ThreadId) -> list[str]:
 6      return [f"messages in {thread_id}"]
 7
 8
 9  def get_run_status(run_id: RunId) -> str:
10      return f"status of {run_id}"
11
12
13  thread: ThreadId = "thread-abc123"
14  run: RunId = "run-xyz789"
15
16  reveal_type(thread)
17  reveal_type(run)
18
19  print(get_history(run))
20  print(get_run_status(thread))
```

```
$ mypy nt1.py

nt1.py:16: note: Revealed type is "str"
nt1.py:17: note: Revealed type is "str"

Success: no issues found in 1 source file
```

Still `Success`, and lines 16–17 say why. Both are **`str`** — not **a `ThreadId`**, not **a `RunId`**. The checker never even remembers the names.

> [!important] A **type alias** is a second name for the same type. `ThreadId = str` works like `x = 5`: afterwards `ThreadId` and `str` are two spellings of one thing, interchangeable everywhere.
>
> It buys readability, and that's genuinely worth having — `dict[str, list[tuple[str, int]]]` written once and referred to by name thereafter. It buys **zero** checking.

The modern spelling is `type ThreadId = str` (3.12+), which states the intent explicitly instead of looking like an ordinary assignment. Same behaviour.

## `NewType` makes a separate type

```python
 1  from typing import NewType
 2
 3  ThreadId = NewType("ThreadId", str)
 4  RunId = NewType("RunId", str)
 5
 6
 7  def get_history(thread_id: ThreadId) -> list[str]:
 8      return [f"messages in {thread_id}"]
 9
10
11  thread = ThreadId("thread-abc123")
12  run = RunId("run-xyz789")
13
14  print(get_history(run))
15  print(get_history("thread-abc123"))
16  print(get_history(thread))
```

Line 11 now **calls** `ThreadId(...)` rather than only annotating.

```
$ mypy nt2.py

nt2.py:14: error: Argument 1 to "get_history" has incompatible type "RunId"; expected "ThreadId"  [arg-type]

nt2.py:15: error: Argument 1 to "get_history" has incompatible type "str"; expected "ThreadId"  [arg-type]
```

**Line 14** — the swap, caught. That's what the whole exercise was for.

**Line 15** — a plain string literal, also caught, and this is the half that surprises people.

It has to work that way. If raw strings flowed in freely the guarantee would leak immediately: every `json.loads` result, every URL parameter, every database column would silently qualify as a `ThreadId`. Requiring the conversion means **the place a raw string becomes a meaningful identifier is written down**, and that place is exactly the boundary you wanted to be deliberate about.

Line 16, passing the real `thread`, is fine.

### At runtime it is still a string

```python
 1  from typing import NewType
 2
 3  ThreadId = NewType("ThreadId", str)
 4
 5
 6  thread = ThreadId("thread-abc123")
 7
 8  print(type(thread))
 9  print(isinstance(thread, str))
10  print(thread.upper())
11  print(thread + "-suffix")
12  print(thread == "thread-abc123")
```

```
$ python3 nt3.py

<class 'str'>
True
THREAD-ABC123
thread-abc123-suffix
True
```

`type(thread)` is `str`. It has `.upper()`, it concatenates, and it compares equal to the plain string it was made from. **No object is created** — `ThreadId(...)` at runtime is essentially a function that returns its argument unchanged.

Same pattern as every rung in this folder: **the distinction exists for the checker and costs the running program nothing**.

| | `ThreadId = str` (alias) | `ThreadId = NewType("ThreadId", str)` |
|---|---|---|
| what the checker sees | `str` — the name is forgotten | a **distinct** type |
| plain `str` accepted? | yes | **no** — conversion required |
| runtime object | `str` | `str` |
| runtime cost | none | none |
| what it buys | readability | a bug class becomes impossible |

## It only flows one way

If a `ThreadId` were separate from `str` in both directions it would be unusable — you couldn't log it, slice it, or use it as a dict key without unwrapping.

```python
 1  from typing import NewType
 2
 3  ThreadId = NewType("ThreadId", str)
 4
 5
 6  def log_line(text: str) -> None:
 7      print(text)
 8
 9
10  def get_history(thread_id: ThreadId) -> list[str]:
11      return [f"messages in {thread_id}"]
12
13
14  thread = ThreadId("thread-abc123")
15
16  log_line(thread)          # ThreadId → str parameter
17  log_line(thread.upper())
18
19  raw: str = thread         # ThreadId → str variable
20  get_history(raw)          # str → ThreadId parameter
```

```
$ mypy nt4.py

nt4.py:20: error: Argument 1 to "get_history" has incompatible type "str"; expected "ThreadId"  [arg-type]
```

```
$ python3 nt4.py
thread-abc123
THREAD-ABC123
```

**Only line 20.** Lines 16, 17 and 19 all pass.

> [!important] **A `ThreadId` goes anywhere a `str` is wanted; a `str` goes nowhere a `ThreadId` is wanted.**
>
> Same shape as a subclass — a `ThreadId` **is a** `str` — so logging it, formatting it, and putting it in a `dict[str, X]` all work without ceremony. Only the reverse direction has to be written down.

Two details visible in that file:

**Line 17.** `thread.upper()` gives back a plain `str`, not a `ThreadId`. The tag doesn't survive operations, which is correct — an uppercased thread id isn't a thread id.

**Line 19.** Assigning to a `str` variable launders the value, and from then on nothing remembers it was ever a `ThreadId`. Not a hole, since somebody had to type it — but it's the thing to look for when swaps stop being caught.

## What this concept claims

**An alias renames a type; `NewType` creates one. Only the second makes the checker keep two things apart.**

Four things to carry:

1. Parameter names are documentation. Two parameters annotated `str` are the same type however carefully they're named, and swapping them is invisible to every tool.
2. `ThreadId = str` is a second spelling of `str`. `reveal_type` will say `str`, and every swap still passes.
3. `NewType` produces a distinct type, and requires the conversion to be written explicitly — which is the feature, because it forces the raw-string boundary to be marked.
4. It costs nothing at runtime: `type(x)` is still `str`, and the relationship is one-way, so nothing downstream needs changing.
