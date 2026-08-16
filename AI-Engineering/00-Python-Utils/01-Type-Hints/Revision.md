#python #type-hints #typing #revision #python-utils

# Type Hints — Revision

One sweep over all 26 concepts. **Built for retrieval, not re-reading** — the drill sections ask before they tell, and the answers are collapsed. Open one only after you've answered out loud.

Order of use: **the spine** (2 min) → **the recall grid** (5 min, scan) → **the drills** (the actual work) → **traps / hooks / index** (before an interview).

---

## The spine

Everything in this folder is a consequence of one sentence:

> **A type hint is a claim you wrote down, not a constraint the language enforces.**

Python evaluates the annotation, stores it in `__annotations__`, and never looks at it again. That single fact generates the whole folder in three directions:

| direction | concepts | the question it answers |
|---|---|---|
| **A separate program reads the text** | 3, 5–19 | what can the claim *express*? |
| **A library reads the stored dictionary** | 1, 4, 20, 25 | what can be *built* on the claim? |
| **The claim is sometimes wrong on purpose** | 22, 23, 24, 26 | what does it cost to *live with* a checker? |

And the corollary that closes the folder: **at a trust boundary, a claim is not enough — something has to validate.**

---

## The recall grid

One row per concept, `#` being the note number. **Cover the right column, answer the question out loud, then uncover.**

| #   | Ask yourself                                                                                     | The answer                                                                                                                                                                                          |
| --- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `add(a: int, b: int)` called as `add("a","b")` returns `"ab"`. Why?                              | Because Python checks types at the level of **operations**, never declarations — joining two strings is valid. Delete both annotations and the behaviour is **identical**                              |
| 2   | A comment and an annotation are both unenforced. Why write the annotation?                       | Only one is **recoverable**. `__annotations__` hands back `<class 'int'>`, the real class; there is no `__comment__`, nothing anywhere. **A comment is prose; an annotation is grammar**              |
| 3   | What is a static checker, and what limits how much it can find?                                  | A separate program reading your code **at rest**, never running it. **Its reach is exactly the reach of your annotations** — on an unannotated file, `Success` is a false all-clear                    |
| 4   | `name: str` in a class body — does `Employee.name` exist?                                        | **No — `AttributeError`.** `= 30` is an assignment; `: str` is not. Two independent registers, neither a subset of the other, and anything wanting the full picture must read **both**                |
| 5   | How many integers does `tuple[int]` allow?                                                       | **Exactly one.** `tuple` types **positions**, left to right; every other container types a *typical element*. So length is part of a tuple's type and of no other container's                         |
| 6   | A function only loops over `names`. Why is `list[str]` the wrong annotation?                     | It rejects the tuple, the set and the generator for requirements the body never had — **three errors on a program with no bugs**. Annotate the weakest type the body needs; return the most specific   |
| 7   | What decides whether `f()` is legal, and what decides whether `f(None)` is?                      | **Two independent switches.** The **default** decides whether the argument may be *omitted*; **`\| None`** decides whether `None` is an *allowed value*. `str = None` is a contradiction               |
| 8   | `Any` and `object` both accept anything. Which one flags the body — and which one crashes?       | **`object` is flagged; `Any` is silent — and `Any` is the one that crashes.** `object` constrains what you may *do* and stays contained; **`Any` switches checking off and travels with the value**    |
| 9   | What can `Literal`, `Final` and `ClassVar` say that a plain type cannot?                         | Which **values** are permitted, whether it may be **reassigned**, whether instances ever get their **own copy**. All three are claims a checker verifies — the reassignment still happens              |
| 10  | What does bare `Callable` fail to catch?                                                         | Everything except "this isn't a function" — it means `Callable[..., Any]`. **A function's type is its whole signature, arity included**, so a decorator typed that way flattens every call site        |
| 11  | `user: User = json.loads(raw)` with a string age and a missing key. What does mypy say?          | **`Success`** — `json.loads` returns `Any`, so that line is an *assertion*, not a check. A `TypedDict` is a plain **`dict`** at runtime, validates nothing, and `isinstance` against it is refused    |
| 12  | Why doesn't `ThreadId = str` catch a swapped thread id and run id?                               | It is a **second spelling of `str`** — `reveal_type` says `str`, the name is never remembered. **An alias renames a type; `NewType` creates one**, and only the second keeps two things apart          |
| 13  | `list[Any] -> Any` and `list[T] -> T` both look vague. What's the difference?                    | **`Any` is two unknowns that never meet; `T` is one unknown mentioned twice** — which is how a return type gets tied to an argument. A bound also keeps the specific **subclass**                     |
| 14  | Why can't a method-level `TypeVar` fix a `Store` that forgets its element type?                  | Because **the type was decided at construction, not at the call** — so the placeholder must belong to the object: `class Store[T]`. A method-level `T` is scoped to that method and has nothing to infer from |
| 15  | `Dog` is an `Animal`. Why isn't `list[Dog]` a `list[Animal]`?                                    | **Because a `list[Animal]` can be written to** — the callee may append a `Cat` while doing nothing wrong. Unsafe the other way too, for the *opposite* reason (reading). Two dangers = **invariant**   |
| 16  | You need "any object with a `.score`", including classes from a library. Why won't a base class do? | Qualifying would require `(Scored)` typed in **their** file, which isn't yours. **An ABC asks "did you declare it?"; a `Protocol` asks "do you have it?"** — nothing is registered anywhere         |
| 17  | Why can't a `TypeVar` express "returns `str` unless `stream=True`"?                               | `True` and `False` are both `bool` — nothing at the type level tells them apart — and **Python has no conditional types**. `Literal` creates the distinction; `@overload` enumerates the cases         |
| 18  | Factoring `isinstance(...)` into `def is_tool(...) -> bool` kills narrowing. Why not read the body? | **A call site is checked from the signature alone**, and `bool` records neither which check nor which variable. State the result in the return type — `TypeIs`, or `TypeGuard`. Neither is verified   |
| 19  | What's wrong with `def clone(self) -> "Agent"` inside `class Agent`?                             | It hard-codes where the method was **written** instead of what it was **called on**, so every subclass degrades to the base type. `Self` is the check-time twin of `type(self)`                       |
| 20  | Where do you put "an `int`, and at least 1" so a library can find it?                            | **In the annotation** — `Annotated[int, Ge(1)]`. Checkers see plain `int`; a library calls `get_type_hints(..., include_extras=True)` and **recognises the objects it put there itself**               |
| 21  | mypy passes; `python3` raises `NameError` on import. What did you write?                          | **`-> Agent` inside `class Agent`.** A `class` statement is *executed*, and defining a function evaluates its annotations right there — the name is bound only after the body finishes                 |
| 22  | A `.pyi` says `-> str`; the real `.py` returns an `int`. Who wins?                                | **The stub.** It is read *instead of* the source, and nothing enforces that they agree — so a hand-written stub is **all-or-nothing**. `py.typed` is zero bytes: **permission, not types**             |
| 23  | What does `cast(T, v)` do at runtime?                                                             | **`return val`** — that is the entire implementation. It never validates, converts or fails; it **relocates** the crash two frames away. **Not one of the three hatches checks anything**              |
| 24  | "Just turn on strict mode" on a 400-function service — what happens?                             | ≈**1600 errors on day one** (one per def, ~three per call site), CI red, and a team that learns to ignore the checker. **Strict by default with a shrinking exemption list**, plus one flag at a time  |
| 25  | Five ways to say "an object with these fields". What decides between them?                       | Already a dict → `TypedDict`. Needs methods → not `TypedDict`. Must be hashable or frozen → `NamedTuple`. **Arrived from outside → a validating model, and that question outranks the other three**    |
| 26  | `log: list[str] = []`, fully typed, `Success` from mypy. What happens on the second call?         | It inherits the first call's entries — **there was never a second list.** Defaults are evaluated **once**, when the `def` runs. Most typing traps are Python's execution model showing through          |

---

## Drill A · The core fact (1–4)

> [!question]- `add(a: int, b: int)` is called as `add("hello", "world")`. It returns `helloworld` with no error. Then `add(5, "world")` raises `TypeError`. Why the difference?
> Nothing to do with the annotation in either case. **Python checks types at the level of operations, not declarations.** At `a + b` it asks *"can these two objects be added?"* — two strings, yes; an int and a str, no.
>
> Proof: delete the annotations entirely and `add(5, "world")` raises the **identical** error. The hint contributed nothing.
>
> Corollary — `get_name(["name"])` on a function annotated `user: dict` complains *"list indices must be integers"*, **not** "you promised me a dict."

> [!question]- Where do annotations go, and what is legal in that slot?
> Into an `__annotations__` dictionary on the function, class, or module — built when the `def` **executes**, once, reused by every later call.
>
> Anything is legal, because Python evaluates the expression and files the result without vetting it:
> ```python
> def nonsense(x: 'banana', y: 12345) -> ['not', 'a', 'type']: ...
> # {'x': 'banana', 'y': 12345, 'return': ['not', 'a', 'type']}
> ```
> `x: 2 + 2` stores `4`. **"Kept and ignored" is not "removed"** — and that survival is exactly what makes runtime libraries possible.

> [!question]- Why write an annotation rather than a comment? Both are unenforced.
> Ask Python for the claim back. `add_a.__annotations__` on the commented version is `{}` — there is no `__comment__`, nothing anywhere. The claim is unrecoverable by any program.
>
> The annotated version gives you `<class 'int'>` — the **real class**, callable, comparable, storable.
>
> **A comment is prose. An annotation is grammar.** A tool can find `a: int` because its position is part of the language; to read `# a is an int` a program would have to read English.

> [!question]- Three lines in a class body: `name: str`, `age: int = 30`, `company = 'Repute'`. Which exist on the class?
> `age` and `company`. **`Employee.name` raises `AttributeError`** — not `None`, not an empty slot; it does not exist.
>
> `= 30` is an assignment; `: str` is not. Two independent registers, neither a subset of the other:
>
> | field | in `__annotations__` | has a value |
> |---|---|---|
> | `name` | yes | **no** |
> | `age` | yes | yes |
> | `company` | **no** | yes |
>
> Anything wanting a complete picture must read **both**.

> [!question]- `__annotations__` vs `get_type_hints()` — and what does resolving actually check?
> `__annotations__` is what was literally written: cheap, never fails, may hand you a string. `get_type_hints()` looks the strings up: returns real objects, and is therefore the only one that can raise.
>
> It checks **nothing** about sense. Resolution is *recursive* — it chases strings until it hits a non-string:
> - `NeverDefined = "abc"` → `NameError: name 'abc' is not defined` (went round again)
> - `NeverDefined = int` → `{'thing': <class 'int'>}`
> - `NeverDefined = 42` → **`{'thing': 42}`, no error**
>
> Storing is safe; resolving is where reality gets checked — and only the reality of *findability*.

> [!question]- What does `Success: no issues found` actually assert?
> **A statement about the claims you gave the checker, not about your code.** On an unannotated file it is a false all-clear over code that provably crashes — which makes that file *worse* than having no checker, because you'd have run it feeling covered.
>
> The demo: `fetch_cart` unannotated → `Success`, then `TypeError` at runtime. Annotate it `-> list[str]`, change nothing else → precise `[arg-type]` error. **One annotation is the entire difference.**

**Telling the two programs apart on sight:**

| output | who | when |
|---|---|---|
| `file.py:8: error: … [arg-type]` | **checker** | you ran `mypy` |
| `note: Revealed type is "…"` | **checker** | `reveal_type()`, checker-only |
| `SyntaxError: invalid syntax` | **Python, compiling** | before any line runs |
| `Traceback … TypeError: …` | **Python, executing** | when it reached that line |

Bracketed `[codes]` are always mypy — Python never prints them. A `Traceback` is always Python — a checker never runs your program.

---

## Drill B · Composing types (5–12)

> [!question]- `tuple[int]` — how many integers?
> **Exactly one.** `tuple` types *positions*, left to right, so naming one position allows one element. `(10,)` passes; `(10, 20)` fails.
>
> The "any number" form is `tuple[int, ...]` — three literal dots.
>
> | | the brackets say |
> |---|---|
> | `list[str]` / `set[str]` | **every** element is a `str`, however many |
> | `dict[str, int]` | every key a `str`, every value an `int` |
> | `tuple[str, int]` | **position 0** is `str`, **position 1** is `int`. Exactly two |
>
> **Length is part of a tuple's type and of no other container's** — it falls out of naming a type per position.

> [!question]- Why does `dict[str, str \| int \| None]` for a user record produce the worst possible outcome?
> Because one `V` slot describes every value, so the checker must assume the worst for all of them:
> - `user["name"].upper()` — **flagged**, and it works (`int` and `None` have no `.upper`)
> - `user["age"] = "thirty"` — **silent**, and it's a bug (`str` is in the union)
> - `user["emial"]` — **silent**, `KeyError` at runtime (the key is a string, as promised)
>
> It complains about the only correct line and misses both bugs. Not a defect in `dict[K,V]` — a **record** is a different thing wearing a dictionary's clothes, and that's `TypedDict`.

> [!question]- A function only loops over `names` and calls `.upper()`. What should the parameter be, and what does `list[str]` cost?
> `Iterable[str]` from `collections.abc`. `list[str]` produces **three errors on a program with no bugs** — the tuple, the set and the generator are all rejected, none of which the body ever needed.
>
> The rule comes from **reading the body**, not from what you happen to pass in.
>
> | the body… | annotate |
> |---|---|
> | only loops | `Iterable[T]` |
> | indexes / takes `len` / needs order | `Sequence[T]` |
> | looks up by key, doesn't change | `Mapping[K, V]` |
> | **changes** it | `list[T]` / `dict[K, V]` |
>
> The `Mutable*` names exist but aren't worth typing: `MutableSequence` is `list` (+`bytearray`), `MutableMapping` is `dict`.
>
> **The trap:** a plain `str` *is* an `Iterable[str]` — pass one name where a collection was meant and it gets shouted a letter at a time, with no complaint from anyone.

> [!question]- Why does the rule invert for return types?
> **Accept abstract, return concrete.** The rule doesn't reverse — the audience does.
> - **Parameter — weak is generous.** You describe what you'll *accept*; looser lets more callers in.
> - **Return — weak is stingy.** You describe what they *get*; looser hands back less than you built.
>
> `-> Iterable[str]` on a function that returns a list is honest and useless: the caller can't index it, `len` it, or append to it, and autocomplete offers one method on a value supporting thirty.

> [!question]- Is `-> str` true for a function that returns `dict.get(...)`?
> No. **An annotation is a claim about every possible run, not the typical one.** One path returning something else makes it false, however rare.
>
> Unlike Java, where `null` is a member of every reference type and `String f() { return null; }` compiles — the hole that produces `NullPointerException`. In Python `None` is the sole value of `NoneType`; `isinstance(None, str)` is `False`. Two types, so say so.
>
> mypy flags **line 3, the `return`** — not the crash site, not the call sites. It caught the lie, visible with no caller in existence.

> [!question]- All four combinations of "optional" — recite the grid.
> |  | `f()` — omit it | `f(None)` |
> |---|---|---|
> | `name: str` | **error** | **error** |
> | `name: str = "friend"` | fine | **error** |
> | `name: str \| None` | **error** | fine |
> | `name: str \| None = None` | fine | fine |
>
> **Two independent switches.** A default decides whether the argument may be *omitted* — nothing to do with types. `\| None` decides whether `None` is an *allowed value* — nothing to do with defaults.
>
> **Row three is the one nobody thinks of:** must be passed, and `None` is a legitimate thing to pass. *"Tell me explicitly, even if the answer is nothing."*
>
> `str = None` is a contradiction. Old mypy silently rewrote it (**implicit Optional**) and that was removed precisely because it erased the difference between rows 2 and 4.

> [!question]- `x: Any` and `x: object` — same statement in the body, one error. Which, and why?
> **`object` is flagged; `Any` is silent — and `Any` is the one that crashes.**
>
> | | who may be passed in | what you may do with it |
> |---|---|---|
> | `Any` | anything | **anything** — every operation allowed |
> | `object` | anything | **almost nothing** — only what every value supports |
>
> `object` describes the data and forces you to narrow. **`Any` is not a type at all — it's a switch** saying *stop checking*.
>
> The `object` error means: *"you promised `x` could be any object, and this line is not safe for every object."* Reported once, at the definition, with no caller in existence.

> [!question]- One `Any` on line 5. How far does the damage reach?
> Everywhere the value goes. **Every operation on an `Any` yields another `Any`** — indexing, attribute access, arithmetic — with no step where the checker recovers.
>
> ```python
> def load_config() -> Any: ...
> cfg = load_config()
> retries = cfg["retries"]        # Any
> timeout = retries.upper()       # Any  ← .upper() on a number
> delay = timeout + [1, 2, 3]     # Any  ← list + string
> print(delay.nonexistent_method())
> ```
> **`Success: no issues found`.** Change line 5 to `-> dict[str, int]` and the first genuinely wrong operation is caught.
>
> `object` is permissive and **contained**; `Any` is permissive and **contagious**. That's how a typed codebase quietly stops being typed — not by removing annotations, but by one `Any` at a boundary.
>
> `Any` at a *real* boundary is correct (`json.loads` genuinely has no single honest type). The discipline is **typing the boundary**: convert at the point of entry so it can't spread inward.

> [!question]- `-> None` vs `-> Never`.
> `-> None` means *"it returns, and the value is nothing."* `-> Never` means *"it does not return."* Only the second lets the checker eliminate a branch.
>
> With `crash(...) -> Never`, a call to it ends that branch, so `return port` is reachable only where `port is None` was false — and `port` is an `int` there. With `-> None`, the checker believes control falls through and correctly complains.
>
> It's a true description of behaviour the code already had, and it **is** verified: declare `-> Never` with a path that returns and you get `Return statement in function which does not return [misc]`.

> [!question]- `Literal` vs `Enum` — and what does `assert_never` actually do?
> | | `Literal` | `Enum` |
> |---|---|---|
> | enforcement | checker only | checker **and** runtime |
> | value at runtime | the plain string | a `Status` object; `.value` for the string |
> | JSON / HTTP / DB | already right | convert at every boundary |
>
> `Literal` when the value is already a string flowing through your system; `Enum` when you want a real object or runtime enforcement.
>
> **`assert_never`'s whole trick is its signature: `(arg: Never) -> Never`.** So the call type-checks only if the checker believes the variable has no possible values left. Every case handled → `Never` → valid. One case missed → that value is still live → error **naming the case you forgot**: `Argument 1 to "assert_never" has incompatible type "Literal['failed']"`.
>
> Without it, the same omission is completely silent — no check-time error, no runtime error, just a blank field in a log six weeks later.

> [!question]- `Final` and `ClassVar` — what does each actually catch, and what still happens?
> **`Final`** flags the reassignment. **The reassignment still happens** — `MAX_RETRIES = 0` on line 12 still makes `range(0)` loop zero times. Adjust from Java: there the compiler enforces it; here it's a claim a checker verifies.
>
> Capitals do nothing. Python has no `const`; `MAX_RETRIES` and `max_retries` are the same kind of name.
>
> **`ClassVar` does not mean "declared in the class body"** — every line there is. It means *"this belongs to the class, and no instance ever gets its own."* Mark `name` (which `__init__` assigns per instance) and you get `Cannot assign to class variable "name" via instance` on the constructor line.
>
> What it catches: `a.total_created = 500` **silently creates a shadowing attribute on `a`** rather than updating the shared counter. `a` reads 500; `b` and the class still read 99. Reading through an instance is fine; writing is almost always a bug.

> [!question]- Bare `Callable` — what does it check, and what slips through?
> It expands to `Callable[..., Any]`: *any arguments, returns something I won't examine.* It catches a string passed where a function was wanted and **nothing else** — a `Callable[[str], str]` passed into something that will call it with `5` sails through.
>
> `Callable[[int], int]` — arguments in their **own list** because a function may take zero or nine; one return type because there is always exactly one. `Callable[int, int]` doesn't parse.
>
> **Arity is part of the type.** `add(a, b)` is rejected for a `Callable[[int], int]` slot with nothing wrong about its types at all.
>
> `...` and `Any` relax **different axes**: `Callable[..., Any]` is unconstrained in count; `Callable[[Any], Any]` is fixed at **exactly one** parameter — the stricter of the two.

> [!question]- What does a decorator annotated `Callable[..., Any] -> Callable[..., Any]` do to its callers?
> Flattens them. `reveal_type` on the decorated function gives `def (*Any, **Any) -> Any` where the undecorated one gives `def (name: str, times: int) -> str`.
>
> **Adding a decorator silently switches off checking at every call site of that function.** Wrong argument counts, wrong types, `.upper()` on a non-string — all unflagged, `Success` throughout. Nothing warns you; the only symptom is errors that stop being found.
>
> The fix is `def logged[**P, R](fn: Callable[P, R]) -> Callable[P, R]` — the same `P`, the same `R`, whatever they turn out to be. `P.args`/`P.kwargs` in the wrapper tie it together.
>
> **Why no `**R`:** a Python function returns exactly one object (`return "a", 30` builds a tuple). Parameters are a variable-length list and need `**`; a return is always one thing. A `ParamSpec` may only appear as the first argument to `Callable`.

> [!question]- `TypedDict` — what is it at runtime, and what does it validate?
> `type(user)` is literally **`dict`**. `User.__mro__` is `(User, dict, object)` — the class genuinely exists and inherits from `dict`, **and it never stamps itself on the object it builds.** You go in through `User` and come out holding a plain dictionary with no memory of it.
>
> Consequence: `isinstance(user, User)` is refused **twice** — by mypy (`Cannot use isinstance() with TypedDict type`) and by Python itself. There's no mark to look for; two dicts with identical contents are indistinguishable.
>
> It validates **nothing**. `user: User = json.loads(raw)` with a string age, an unknown key, and a missing key gets `Success` and crashes four lines later — because `json.loads` returns `Any`, so that line is an *assertion*, not a check.
>
> **Absent keys use `NotRequired`, not a default.** A `TypedDict` cannot have defaults — there's nothing to attach one to, since the dict was built by a `{...}` literal with no involvement from `User` at all.

> [!question]- Why doesn't `ThreadId = str` catch a swapped thread id and run id?
> Because it's a **second spelling of `str`**. `reveal_type` on both says `str` — the checker never even remembers the names. It buys readability and **zero** checking. (Parameter names buy nothing either; they're not part of a type.)
>
> `ThreadId = NewType("ThreadId", str)` makes a distinct type. Two errors appear:
> - the **swap** — the point of the exercise
> - a **plain string literal**, and that's the half that surprises people
>
> The second has to work that way, or the guarantee leaks: every `json.loads` result and URL parameter would silently qualify. Requiring `ThreadId("...")` means **the place a raw string becomes a meaningful identifier is written down.**
>
> It flows **one way**: a `ThreadId` goes anywhere a `str` is wanted; a `str` goes nowhere a `ThreadId` is wanted. `thread.upper()` gives back a plain `str` — the tag doesn't survive operations. Runtime: `type(thread)` is `str`, no object created.

---

## Drill C · Generics and abstraction (13–19)

> [!question]- `list[Any] -> Any` and `list[T] -> T` both look vague. What's the difference?
> **`Any` is two unknowns that never meet. `T` is one unknown, mentioned twice.**
>
> With `Any`, mypy knew perfectly well the argument was a `list[str]` and threw it away — both results reveal `Any`, and everything downstream goes unchecked. With `T`, one call site reveals `str` and another `dict[str, str]`, resolved separately per call with no explicit type argument.

> [!question]- Bound vs constraints.
> | | `T: Message` (bound) | `T: (Candidate, ToolCall)` (constraints) |
> |---|---|---|
> | written as | one type | a tuple of types |
> | means | that type **or a subclass** | **exactly** one of these |
> | open to new types | yes | no — closed list |
>
> A bound **keeps the specific subclass**: `last([HumanMessage(...)])` reveals `HumanMessage`, not `Message`, so `.user_id` resolves. Annotating `list[Message] -> Message` would also reject the strings *and* throw the subclass away.
>
> Both are declared **once**, after the function name — `def last[T: Message](...)`. Put the bound at the use site and `T` was never introduced (a plain `NameError` from Python); it also makes two contradictory bounds on one placeholder expressible.
>
> Reaching for constraints because several unrelated classes share a *method* is the signal for `Protocol`.

> [!question]- Why can't a method-level `TypeVar` fix a `Store` that forgets its element type?
> Two failures, and the second is structural. A method-level declaration is **scoped to that method**, so `__init__` can't see it. And `get[T](self, i: int) -> T` has nothing in the call to work `T` out from — *"a function returning a TypeVar should receive at least one argument containing the same TypeVar."*
>
> **The type was decided when the store was created, not when `get` was called**, so the placeholder has to belong to the object: `class Store[T]`.
>
> `T` is fixed at construction — inferred if `__init__` receives something that determines it, otherwise write `Store[str]`. **Bare `Store()` gives `Need type annotation` and silently becomes `Store[Any]`**, and a later `add("search")` does not rescue it.
>
> Runtime: `Store[str]()` produces a plain `Store`; `type(a) is type(b)` for differently-parameterised stores. **This is exactly Java's erasure** — of generic type parameters, which `age: int` never was.

> [!question]- Why is `list[Dog]` not a `list[Animal]`, when `Dog` is an `Animal`?
> Because **a `list[Animal]` can be written to.** A function holding that parameter may append a `Cat` — doing nothing wrong, since a `Cat` really is an `Animal` — and your next loop crashes on an attribute the base class doesn't have.
>
> Nothing in a signature distinguishes *"I will read this"* from *"I will replace its contents"*, so the checker assumes the worst.
>
> And `list` is unsafe in **both** directions for **two different reasons**:
> - `list[Sub]` → `list[Base]` parameter: **the danger is writing**
> - `list[Base]` → `list[Sub]` parameter: **the danger is reading** (`.user_id` on a plain `Message`)
>
> That's what *invariant* means: `list[X]` matches `list[X]` and nothing else, ever.

> [!question]- State the three variance rules without arrows.
> Two words, defined once: **wider** covers more kinds of thing (the base class); **narrower** covers fewer and therefore guarantees more attributes.
>
> Each rule phrased identically — *you have this; can you pass it where that is wanted?*
>
> 1. **A read-only container: you may pass a narrower one.** `Sequence[HumanMessage]` → `Sequence[Message]`. *Why:* it will read and get a `HumanMessage`; it expected a `Message`; a `HumanMessage` is one. → **covariant**
> 2. **A function's parameter: you may pass one that accepts a wider type.** `Callable[[Message], None]` → `Callable[[HumanMessage], None]`. *Why:* it will be called with a `HumanMessage`, and yours copes with any `Message`. → **contravariant**
> 3. **A function's return: you may pass one that returns a narrower type.** *Why:* the caller will use it as a `Message`. → **covariant**
>
> Rules 1 and 3 are the same rule — **what you receive may be narrower than promised.** Rule 2 is its mirror — **what you accept may be wider.**
>
> So `Callable` is contravariant in its parameters and covariant in its return, in one type.
>
> | | which types |
> |---|---|
> | **invariant** | `list`, `dict`, `set` — anything mutable |
> | **covariant** | `Sequence`, `Iterable`, `Mapping`, `tuple` — read-only |

> [!question]- Why does a common base class not solve "any object with a `.score`"?
> Because qualifying requires the words `(Scored)` to be typed **in the implementing class's own file** — and that file isn't yours when the class came from a library. That's **nominal** typing, and making the bound open-ended doesn't help.
>
> Wrapping works and costs a different object on every hop, plus a class whose entire job is to satisfy a type checker.
>
> `class Scored(Protocol)` changes the question the checker asks:
>
> | | asks |
> |---|---|
> | base class / ABC | did this class **declare** it is a `Scored`? |
> | `Protocol` | does this class **have** what `Scored` describes? |
>
> Nothing is registered anywhere — mypy re-reads the class definition at each place the question arises, and neither file ever names the other.

> [!question]- `Protocol` at runtime: what can you do with it?
> Almost nothing, and that's diagnostic.
> - It **is** a genuine class with an `__mro__` — not checker-only like `Literal`.
> - **Cannot be instantiated** — `TypeError: Protocols cannot be instantiated`, raised by Python.
> - **`isinstance` refuses to answer.** `RetrievedDoc.__mro__` is `(RetrievedDoc, object)`; `Scored` isn't in it and never will be, because the whole match happened inside mypy.
>
> `@runtime_checkable` opts in — and it is **strictly weaker than the static check**. It does one `hasattr` per member and never inspects types, so an object whose `score` is the string `"not a number"` returns **`True`**. That gap is why it's opt-in: you have to ask for the weaker check having been told it's weaker.

> [!question]- `Protocol` vs ABC — the one-line answer.
> **An ABC points from the implementer to the abstraction; a `Protocol` points from the consumer to it.**
>
> | | ABC | `Protocol` |
> |---|---|---|
> | how you qualify | inherit, by name | have the members |
> | classes you don't own | can't use it | works |
> | enforced when | **runtime** — can't instantiate an incomplete class | check time only |
> | shared implementation | inherited free | **one more requirement** unless you inherit |
>
> That fourth row surprises people: a method implemented *inside a protocol* is not a gift. A class that merely matches gets rejected for **not having** it.
>
> Own the hierarchy, incomplete implementations must be impossible → **ABC**. Describing a boundary that third-party objects and test doubles arrive at → **`Protocol`**. (`Retriever`, `LLMClient`, `Checkpointer` are protocols — a vendor SDK is never going to inherit from anything you wrote.)
>
> **Member variance follows the container rule:** a plain attribute (`score: float`) is writable, therefore **invariant** — it demands an exact `float`. A read-only `@property` is **covariant** — `int` is accepted. If your protocol only reads a value, declare it read-only.

> [!question]- Why can't a `TypeVar` express "returns a `str` unless `stream=True`"?
> Two reasons, and either alone is fatal.
> 1. **`stream=True` and `stream=False` are both `bool`** — at the type level there is nothing to tell them apart.
> 2. To express the answer you'd need *"if `T` is `Literal[True]` then `AsyncIterator[str]`, otherwise `str`"* — and **Python's type system has no conditional types.** A `TypeVar` carries a type through *unchanged*; it cannot map one type onto a different one.
>
> `Literal` is what creates the distinction — `09`'s *"this exact value, not merely this type"* paying off. It turns two calls differing in a **value** into two calls differing in **type**.
>
> Structure: the `@overload`-decorated defs are **pure signature with `...` bodies** and are all a caller sees; the final undecorated def is the implementation — wide parameter types, union return, the only one that runs.

> [!question]- Overloads on `Literal[True]`/`Literal[False]`, called with a runtime `bool`. What happens?
> **mypy rejects it; pyright accepts it.** Same file, opposite verdicts — the second verified checker disagreement in this folder.
>
> The premise *"a `bool` is only ever `True` or `False`"* is correct: `bool` and `Literal[True] | Literal[False]` are mutually assignable and both checkers agree. What breaks is the **resolution algorithm** — it must pick exactly one variant because it must produce exactly one return type, and a plain `bool` is assignable to **neither literal alone**. mypy stops.
>
> Pyright does **argument type expansion**: split the `bool` into its literals, resolve once per piece, union the results → `AsyncIterator[str] | str`.
>
> **The portable fix is an explicit catch-all overload, placed last** — checkers take the first matching variant, so a `bool` variant first would swallow both literal cases.

> [!question]- Factoring `isinstance(msg, ToolMessage)` into `def is_tool(...) -> bool` destroys narrowing. Why won't the checker just read the body?
> **A call site is checked from the signature alone**, and `bool` records neither *which* check nor *which variable*. `is_tool(msg)` and `len(x) > 0` have the same type.
>
> Two reasons that isn't a shortcut:
> - **Often there is no body** — a `Callable` parameter is supplied by the caller; an untyped import has no source.
> - **Reading bodies would make editing one break its callers invisibly**, silently altering what type-checks in every file that calls it, including other packages.
>
> `isinstance` inline narrows **both** branches — inside to what you tested for, outside to whatever the union has left. That second half is what people miss.

> [!question]- `TypeIs` vs `TypeGuard`, and is either verified?
> | | `TypeGuard[T]` | `TypeIs[T]` |
> |---|---|---|
> | `if` branch | narrows to `T` | narrows to `T` |
> | `else` branch | **unchanged** | narrows to the rest of the union |
> | `T` must be a subtype of the input | no | **yes** |
> | since | 3.10 | 3.13 |
>
> `TypeIs` needs the subtype relationship *because* it narrows both branches — "on `False`, subtract `T` from the input" means nothing if `T` was never part of the input.
>
> `TypeGuard` survives for exactly that third row: `list[object]` → `list[str]` is rejected by `TypeIs` (`list` is invariant — `15-Variance`) and accepted by `TypeGuard`. So: **`TypeIs` as the default; `TypeGuard` when the narrowed type isn't a subtype, which in practice means containers.**
>
> **Neither is verified.** A body of `return True` earns a clean `Success`, and every call site then narrows on a lie. Keep the body to a real check — an `isinstance`, a tag comparison, a key test.

> [!question]- What exactly is wrong with `def clone(self) -> "Agent"` inside `class Agent`?
> It hard-codes where the method was **written** rather than what it was **called on**, so every subclass degrades to the base type the moment a value passes through it. `SearchAgent("s").clone()` reveals `Agent`, and `.search` is refused on an object that genuinely has it.
>
> Overriding in each subclass is **legal** (`15-Variance` permits a narrower return) and still wrong: it duplicates the body, must be repeated forever, and **breaks again one level down** — each override merely relocates the hard-coded name.
>
> `Self` is the **check-time twin of `type(self)`**: one is what the object *is* at runtime, the other what the checker calls it. One method in the base class then serves every depth.
>
> It matters most where values flow back out — alternative constructors, `clone`-style copies, and **fluent chains**, where the damage compounds: one base-class method annotated with the base class name flattens everything downstream.

---

## Drill D · Runtime interaction (20–21)

> [!question]- Why can't "at least 1" be a type, and why is a side dict the wrong home for it?
> `Literal` can only **enumerate**, and "at least 1" is infinitely many. `NewType(name, supertype)` has **no slot** for a rule. And `max_retries: int > 0` is not even a syntax error — an annotation is an evaluated expression, so it's `TypeError: '>' not supported between instances of 'type' and 'int'`.
>
> A `CONSTRAINTS = {...}` dict alongside works and fails twice: it **drifts** on a rename, and it **doesn't travel** with the object the way an annotation does — hand your function to a library and it can read `__annotations__` but has no way to know your rules exist.

> [!question]- What do a checker and a runtime library each see in `Annotated[int, Ge(1)]`?
> The checker sees **`int`** — `reveal_type` doesn't mention the wrapper at all. So a wrong *type* is still caught and a violated *constraint* is not.
>
> The library sees whatever it asks for:
> - `get_type_hints(fn)` → `{'max_retries': <class 'int'>}` — **extras stripped by default**, so adding `Annotated` breaks nothing that already reads annotations
> - `get_type_hints(fn, include_extras=True)` → `typing.Annotated[int, Ge(1)]`
>
> The object itself: `__origin__` is the type, `__metadata__` is a **plain tuple** of everything after it. Extras are arbitrary objects — a string, an `int` and a list side by side are all legal, because `Annotated` doesn't interpret them, it stores them.
>
> **How enforcement actually works** (the interview sentence): a runtime library calls `get_type_hints(..., include_extras=True)` and **recognises the objects it put there itself**. It's concept 1's answer one level up.

> [!question]- Why must a LangGraph reducer live in the annotation rather than in the merge code?
> Because the behaviour is **per key**. `{**state, **update}` overwrites — which is exactly right for `step` and destroys the user's question in `messages`. Two keys, one merge, two behaviours needed.
>
> - **In the merge code** — that code is the framework's, generic across every agent, and has never heard of your keys.
> - **In a side dict** — drifts, doesn't travel.
> - **Attached to the key** — `messages: Annotated[list[str], operator.add]`, where the merge finds it while reading the type it already has to read.
>
> Nothing new about `Annotated` is involved: the extras are arbitrary objects and a function is an object. Earlier the extra *described* a rule; here it *performs* one. **You write the annotation; the framework writes the reader.**

> [!question]- `mypy` passes, `python3` crashes with `NameError`. What did you write?
> `-> Agent` inside `class Agent` — and the direction is the reverse of everything else in this folder. The checker reads the file as text and sees `Agent` plainly; the interpreter has to actually *have* it.
>
> **A `class` statement is executed, not declared.** Print statements in a class body run. The order:
> 1. Python begins executing the class body
> 2. every line runs — the `def` among them, and defining a function **evaluates its annotations right there**
> 3. the body finishes
> 4. **only now** is the name `Agent` bound
>
> The annotation happens at step 2; the name exists at step 4. And the module never imports — this is not a bug that waits for the method to be called.

> [!question]- Quotes vs `from __future__ import annotations` — what does each store?
> | written as | Python evaluates | stores |
> |---|---|---|
> | `-> Agent` | a **name lookup** | the class object — needs it to exist |
> | `-> "Agent"` | a **string literal** | `'Agent'` — needs nothing |
> | future import | nothing | `'Agent'`, and **every** annotation as text |
>
> Quoting is surgical; the import is blanket. Both are safe because **annotations are never enforced** (concept 1), so degrading one to a string costs nothing behaviourally.
>
> Watch "evaluate" happen: make the annotation a function call. Without the import, the print fires **between** "about to define" and "defined" — before any call — and `<class 'int'>` is stored. With it, the print never fires and `'make_type()'` is stored, characters and all.
>
> **The cost of the import:** runtime readers (Pydantic, anything built on `Annotated`) receive strings and must re-resolve them with `get_type_hints()`, which needs the defining module's globals. Both designs are flawed; 3.14's PEP 649/749 lazy evaluation is the attempt to have both.

> [!question]- Circular imports: why does the future import alone not fix them?
> Because they are **two problems wearing one error message**, and each fix addresses only one.
>
> | problem | fix |
> |---|---|
> | the annotation needs a name that isn't importable | future import, or quotes |
> | **the import statement itself deadlocks** | `if TYPE_CHECKING:` |
>
> Add the future import alone and the crash moves to *the `import` line*, not an annotation. You made the annotations not need `AgentState` and then imported it anyway.
>
> **`TYPE_CHECKING` is an ordinary constant that is `False` at runtime.** The import sits inside `if False:` — Python skips it, checkers hard-code the opposite and walk in.
>
> **Both halves are load-bearing.** Remove `if TYPE_CHECKING:` → Python deadlocks on the import. Remove the future import → Python crashes on the *annotation*, because the name was never imported.

---

## Drill E · Living with a checker (22–25)

> [!question]- A `.pyi` says `-> str`; the real `.py` says `-> int`. Who wins, and what does that tell you?
> **The stub.** mypy reveals `str`; Python returns an `int`. When a `.pyi` exists the checker reads it **instead of** the source, not in addition to it, and nothing enforces that the two agree.
>
> That's why a hand-written stub is **all-or-nothing**: it is the complete truth about that module. Declare one of two functions and `close()` **stops existing** for the checker while running perfectly fine. Stub one function from a large library and you have just deleted the other four hundred.

> [!question]- `py.typed` — what's in it?
> **Nothing. Zero bytes.** It is **permission to use the types that were already there.** Delete it from an installed, fully-annotated package and the same code goes from `int` to `Any` — the annotations never moved; mypy simply stopped trusting them.
>
> Two routes to a typed library, one from outside and one from inside:
>
> | | who writes the types | where they live |
> |---|---|---|
> | **stub package** | outsiders (`types-requests`) | a separate PyPI package |
> | **`py.typed`** | the library's own authors | inline, in the real `.py` files |
>
> Also worth holding: mypy **reads an installed dependency's whole body but reports no errors inside it** — a deliberate split, since surfacing them would bury you in errors in code you can't fix. For a local project file it does report them.

> [!question]- A dependency has no type hints. Rank the options.
> First ask **which case it is**:
> - **annotated but unmarked** → `follow_untyped_imports`, scoped per-module in config. Never as a global flag — that trusts every untyped dependency you have.
> - **a stub package exists** → install it.
> - **genuinely untyped** → the ranking below.
>
> | | what you get | when |
> |---|---|---|
> | `# type: ignore` on the import | silence; everything `Any` | never, if avoidable |
> | `ignore_missing_imports` | the same, written down | you accept it |
> | `follow_untyped_imports` per-module | the library's real annotations | it **is** annotated, just unmarked |
> | your own `.pyi` via `mypy_path` | types you wrote | small surface, or no other option |
> | **a thin typed wrapper module** | types you wrote, `Any` in one file | **the usual right answer** |
> | install a stub package | curated, maintained | one exists |
>
> The wrapper wins because there's no stub to keep in sync, no risk of deleting four hundred functions you never declared, and the untyped surface of the whole project is one file you can point at in review.

> [!question]- `cast` — what does it do at runtime?
> ```python
> def cast(typ, val):
>     return val
> ```
> That is the **entire** implementation. It never validates, converts, or fails — a no-op that exists purely to be read by the checker. The word is borrowed from languages where it means something else; a C or Java cast can convert or fail loudly.
>
> The expensive part: a wrong cast doesn't crash where you wrote it. It **relocates** the failure — the traceback lands two frames away, inside the function you handed the value to, and **the line that lied is not in the traceback at all.**
>
> Why it's needed at all: narrowing runs out when there's nothing on the object to test. `isinstance` against a `TypedDict` is refused by mypy *and* Python, and `isinstance(payload, dict)` is true of every dictionary ever made, so the checker learns nothing from it.

> [!question]- Bare `# type: ignore` vs `# type: ignore[union-attr]`.
> A line carrying **two independent errors**: bare silences both, including the one you never looked at. With the code in brackets, the other survives and mypy says so — `Error code "assignment" not covered by "type: ignore[union-attr]" comment`.
>
> The two comments make different promises:
> - `# type: ignore` — *I have looked at everything on this line, now and forever.*
> - `# type: ignore[code]` — *I have looked at this one thing.*
>
> Only the second is a promise you can keep. The cost of the first is in the "forever": that line grows a real bug with a different code next year and the bare comment swallows it in silence.
>
> **Where the codes come from:** mypy prints one at the end of every error. Copy it out. Nothing to memorise.
>
> It also handles what `cast` structurally cannot — an error with **no value in it**, like a failed import. There's nothing on that line to cast.

> [!question]- Rank the three hatches by reach, and give the test for legitimacy.
> | | reach | verified? |
> |---|---|---|
> | `cast(T, v)` | one **value** | no |
> | `# type: ignore[code]` | one **line**, one code | no |
> | `# type: ignore` | one line, **every** code, forever | no |
> | `Any` | **every line the value reaches** | no |
>
> `Any` is bluntest because it **travels** — the word sits on line 5; the suppression follows the value into every function and file that touches it.
>
> **The test: a hatch is legitimate when it *records* a fact you established some other way, and illegitimate when it *substitutes* for establishing it.** The identical `cast(ToolCall, payload)` is a lie on one line and a record of a check on another; what changed is the four lines above it.
>
> And the sharper move: at a **trust boundary** the fact can't be established at check time at all — so **validate, don't assert.** `ToolCall.model_validate(payload)` returns a genuinely typed object and needs no hatch of any kind.

> [!question]- "How would you introduce typing to a large untyped service?" What's wrong with "turn on strict mode"?
> **One** unannotated function produces **two** errors — one for defining it, one per call site. A service with 400 of them called from three places each:
> - 400 × `[no-untyped-def]` + 1200 × `[no-untyped-call]` ≈ **1600 errors on day one**
>
> And the number is the problem, not the work: nobody reviews 1600 lines, it can't land in one PR without touching every file, and **CI is red from day one, so the team learns to ignore the checker** — worse than never turning it on.
>
> **Dial one — scope by module.** Strict by default plus an explicit exemption list that only shrinks. (A date-based boundary can't work: mypy sees files, not history.)
>
> **The rule the surviving error teaches:** a per-module setting applies where the error is **reported**, not to the module being referenced. Exempting `legacy.*` leaves a call site in `core` still red — and that is a *feature*: those surviving errors are exactly the typed/untyped boundary, i.e. the work queue.
>
> **Dial two — scope by check.** `--strict` is **thirteen named flags** under one name. Turn one on repo-wide, fix that class, keep it, move to the next.
>
> The answer: **"strict by default with a shrinking exemption list"** — plus the second dial. CI green from day one, new code strictly checked, and you annotate a function when you have a reason to.

> [!question]- Five ways to say "an object with these fields". What decides?
> | | plain `dict` | `TypedDict` | `NamedTuple` | `@dataclass` | validating model |
> |---|---|---|---|---|---|
> | at runtime | `dict` | `dict` | `tuple` | normal object | normal object |
> | per-field static types | no | yes | yes | yes | yes |
> | methods on it | no | **no** | yes | yes | yes |
> | mutable | yes | yes | **no** | yes | yes |
> | set / dict key | no | no | **yes** | no | no |
> | **checks values at runtime** | no | no | no | no | **yes** |
>
> Four questions:
> 1. **Already a dict?** → `TypedDict` costs nothing and changes no code.
> 2. **Needs behaviour?** → rules out `TypedDict` outright; the instance is a plain dict with nowhere to put a method.
> 3. **Must be a key, or must not change?** → `NamedTuple`. **Immutable, therefore hashable** — the same fact twice.
> 4. **Did it come from outside?** → **a validating model, and this question outranks the other three.**
>
> Short form: **`TypedDict` for dicts you already have, `@dataclass` for objects you create, `NamedTuple` when it must be hashable or frozen, a validating model for anything arriving from outside.**

> [!question]- `@dataclass` generates code from annotations. Does that enforce them?
> **No.** `RetrievedDoc("u1", "hello", "not a number")` constructs fine and stores the string; `type(bad.score)` is `str`. The generated `__init__` **assigns** — it read the annotation to learn each field's name and position and never compares the value against it.
>
> And it fails **where the value is first used**, not where it entered.
>
> The gap only matters when there's no construction site for mypy to check — which is exactly the boundary case. `RetrievedDoc(**json.loads(raw))` gets `Success`, because `json.loads` returns `Any`, so it's unchecked *by construction*. **Every guarantee in the file is gone at the one place data actually enters.**
>
> Swap `@dataclass` for a `BaseModel` and `"0.9"` becomes `0.9`, `type(doc.score)` is `float`, and unparseable input raises **at the boundary**, naming the field, the reason, and the value it received. Same bad data, same eventual failure — **the difference is where you find out**, and placement is the entire value.
>
> Three appearances of one mechanism: `@dataclass` reads annotations to **generate** code, a validating model reads them to **check values**, `Annotated` carries payload for either. The language enforces nothing in any of the three.

---

## Drill F · Traps (26)

> [!question]- `def run_tool(name: str, log: list[str] = []) -> list[str]` — fully typed, `Success` from mypy. What happens on the second call?
> It inherits the first call's work: `['ran search', 'ran summarise']`. Asking the function for its default afterwards shows the polluted list. **There was never a second list.**
>
> The reason is `21`'s rule applied to defaults: **a `def` is executed, and executing it evaluates the defaults — once, at definition.** Make the default a function call and its print fires *before* either call, and fires *once*.
>
> `= []` reads like an instruction (*"when nobody passes a log, make an empty one"*). It is a **value computed once** and stored on the function object for the lifetime of the program.
>
> In agent code: `messages: list[Message] = []` on a conversation handler means turn 400 arrives carrying 399 strangers' messages.
>
> Fix: `log: list[str] | None = None`, then build the real list **in the body**, which runs per call.

**The four spellings:**

| | means | optional to *pass*? | may be `None`? |
|---|---|---|---|
| `log: list[str]` | must be a list | **no** | no |
| `log: list[str] = []` | must be a list | yes | no — but **shared across calls** |
| `log: list[str] \| None = None` | list or `None` | yes | yes |
| `log: list[str] = None` | **contradiction** | — | — |

> [!question]- Does `self` need an annotation? Does `cls`?
> No. mypy infers it from the class the method is written in — `reveal_type(self)` gives `tr4.Agent` with nothing written. `self: Agent` can only ever restate what the checker already worked out.
>
> Why it can infer it: `self` is an **ordinary first parameter holding the very object the method was called on** — same memory address as the variable outside. `Agent.who()` fails with `missing 1 required positional argument: 'self'`. It is never `None`, because a method can't run without an object to run on.
>
> **But the return type behind it is a real bug** — `-> "Agent"` degrades every subclass. That's `19-Self`.

> [!question]- When is an annotation on a variable noise, and when is it necessary?
> The rule is a question: **would the checker have got there on its own?**
>
> | | |
> |---|---|
> | `name: str = "search"` | **noise** — the value says `str` |
> | `results: list[str] = []` | **necessary** — `[]` says nothing about contents |
> | `cache: dict[str, int] = {}` | necessary — same reason |
> | `config: Config \| None = None` | necessary — `None` alone tells you nothing |
>
> mypy asks by name for the ones it needs: `Need type annotation for "results"`. Without it you get `list[Any]`, and concept 8's spreading applies to everything that comes out.
>
> Over-annotating isn't merely harmless: **it trains readers to skim annotations**, which costs you on the lines carrying real information.

**The last trap, proved rung by rung:**

| rung | the demonstration |
|---|---|
| `01` | annotations are inert data; nothing reads them unless a library chooses to |
| `11` | a `TypedDict` never validates — hand it the wrong types and it stores them |
| `18` | `TypeIs` with a body of `return True` earns a clean `Success`, then `AttributeError` |
| `21` | an annotation can be the string `'Agent'` and the function still returns a real one |
| `22` | a `.pyi` can flatly contradict the source it describes; the checker believes the stub |
| `23` | `cast` is `return val` — an assertion with no check anywhere behind it |
| `25` | a `@dataclass` annotated `float` will hold `"0.9"` all day |

> [!warning] A type hint is a **claim about intent**, checked by a separate program you have to actually run. It is never a runtime guarantee — and every escape hatch in the language exists because sometimes the claim is wrong on purpose.

---

## The seven interview hooks

Say the **sharp form**, not the textbook form.

| Question | The sharp answer |
|---|---|
| *"Are type hints enforced at runtime?"* | **No — and Pydantic enforces them by *choosing to read them* at runtime.** The separation is the whole design. |
| *"`Protocol` or ABC?"* | Directional: **an ABC points from the implementer to the abstraction; a `Protocol` points from the consumer to it.** Own the hierarchy and incomplete implementations must be impossible → ABC (enforced at instantiation). A boundary third-party objects and test doubles arrive at → `Protocol`. |
| *"Why isn't `list[Dog]` a `list[Animal]`?"* | **Because a `list[Animal]` can be written to** — the callee may append a `Cat` while doing nothing wrong. And it's unsafe the other way too, for the opposite reason (reading). Two dangers pointing opposite ways = invariant. |
| *"Why `Sequence[str]` rather than `list[str]`?"* | Same question in everyday clothes. `list` rejects a tuple, set, generator and dict-keys for requirements the body never had — **and the signature now says whether the function will modify what you gave it.** |
| *"How would you add typing to a large untyped codebase?"* | **Not "turn on strict mode"** — that's ~1600 errors on a 400-function service, CI red on day one, and a team that learns to ignore the checker. **Strict by default with an explicit per-module exemption list that only shrinks**, plus the second dial: `--strict` is thirteen flags, so one check can go repo-wide at a time. The surviving errors mark the typed/untyped boundary — that's the work queue. |
| *"What about a dependency with no type hints?"* | Ask which case. Annotated-but-unmarked → `follow_untyped_imports` **scoped to that module**. Stub package exists → install it. Genuinely untyped → **a thin typed wrapper of your own** that absorbs the `Any` in one reviewable file. A hand-written `.pyi` is the fallback, because **a stub is the complete truth about its module** — anything omitted stops existing for the checker while still running fine. |
| *"`TypedDict` vs dataclass vs Pydantic model?"* | `TypedDict` for dicts you already have, `@dataclass` for objects you create, `NamedTuple` when it must be hashable or frozen, **a validating model for anything arriving from outside — and that last question outranks the others**, because the argument for validation is *where* the failure surfaces, not whether one happens. |

---

## Error-code index

What mypy is actually telling you.

| code | means | usual cause |
|---|---|---|
| `[arg-type]` | wrong type passed | the everyday one |
| `[return-value]` | the `return` doesn't match the annotation | a `\| None` you didn't declare |
| `[assignment]` | incompatible assignment | includes `str = None` |
| `[attr-defined]` | no such attribute | `object`, a union member, or a wrong `Self` |
| `[union-attr]` | attribute missing on **one member** of a union | narrow it |
| `[list-item]` | wrong element type in a literal | one error per bad element |
| `[typeddict-item]` | wrong value type, or an unknown/missing key | prints *"Did you mean …?"* |
| `[type-var]` | value violates a bound or constraints | |
| `[valid-type]` | not usable as a type at all | `Callable[int, int]`, `int > 0` |
| `[var-annotated]` | *Need type annotation* | an empty container with nothing to infer from |
| `[call-overload]` | no overload variant matches | lists every variant it tried |
| `[index]` / `[call-arg]` / `[misc]` | not indexable / wrong arity / everything else | |
| `[no-untyped-def]` / `[no-untyped-call]` | strict-mode only | the 1-to-3 ratio behind the 1600 |
| `[import-not-found]` / `[import-untyped]` | no stub / no `py.typed` | `22` |
| `[narrowed-type-not-subtype]` | `TypeIs` where the types aren't related | use `TypeGuard` |

---

## Version boundaries

Worth stating precisely — a wrong version claim is expensive in a screen.

| feature | since |
|---|---|
| built-in generics — `list[str]` | **3.9** |
| `X \| None` | **3.10** |
| `TypeGuard` | 3.10 |
| `Self`, `Never`, `assert_never` | **3.11** |
| PEP 695 — `def f[T]()`, `class C[T]`, `type X = ...` | **3.12** |
| `TypeIs` (PEP 742) | **3.13** |
| **PEP 649/749 — lazy annotation evaluation** | **3.14** |

Two more worth carrying:
- **`collections.abc` is the modern home** for `Iterable`/`Sequence`/`Mapping`/`Callable`; the `typing.` versions are deprecated aliases.
- **PEP 649 is the big one.** Annotations stop being eagerly evaluated at definition time, which changes how runtime-introspecting libraries read them and largely retires `from __future__ import annotations`. **This folder's notes were verified on 3.13.3 with mypy 2.x** — `21-Deferred-Evaluation`'s central `NameError` demo is version-bound and should be re-run before you rely on it.

---

## Where the checkers disagree

Two verified cases in this folder. Both make *"which checker are you running?"* a real question — and it matters because **pyright is what VS Code's Pylance runs**, so your editor and a mypy-based CI can reach opposite verdicts on the same file.

| case | mypy | pyright |
|---|---|---|
| a protocol implementer **renames a parameter** (`text` vs `query`) | **accepts** — then `TypeError` at runtime on the keyword call | **rejects**, naming the mismatch |
| overloads on `Literal[True]`/`Literal[False]`, called with a runtime `bool` | **rejects** `[call-overload]`; reveals `Any` | **accepts** via argument type expansion → `AsyncIterator[str] \| str` |

Portable fixes: `/` in the protocol signature to declare parameters positional-only; an explicit catch-all overload placed **last**.
