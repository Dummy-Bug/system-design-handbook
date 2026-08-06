#python #type-hints #typing #python-utils #syllabus

# 01 · Type Hints — Syllabus

26 concepts. **Generic** — the language feature, not any one library's use of it.

> Learn the whole typing surface first, *then* notice which parts Pydantic/FastAPI happen to exercise. Deriving the list from "what I've already seen in Pydantic" silently drops `Protocol`, `overload`, and generics — and those are exactly what a typing question in a screen reaches for.

**Why this sits first:** everything downstream reads annotations. Pydantic *is* "annotations, enforced at runtime." FastAPI routes are annotation-driven. `Annotated[...]` — the V2 constraint mechanism already used throughout the Pydantic notes — is a typing feature that was never actually explained there, only used.

**Revised 2026-08-06,** from 18 concepts to 26. Eight were added after checking the list against what interviews actually ask and against a current tutorial: **6** (abstract collection types), **12** (aliases and `NewType`), **15** (variance, promoted from a one-line trap), **19** (`Self`), and the whole of **section E** — stubs, escape hatches, gradual adoption, and choosing a structured-data type. Section E is the one worth noticing: the original list covered *what the type system can express* and nothing about *living with a type checker on a real codebase*, which is where the senior-level questions actually sit.

**Currency check (2026-08-06):** this machine runs Python 3.13.3; 3.14 is current stable, and **mypy is on 2.x** — worth knowing, because most written material still assumes 1.x. Version lines to re-verify before relying on them: **built-in generics** (`list[str]`) 3.9+; **`X | None`** 3.10+; **`TypeGuard`** 3.10+; **`Self`**, **`Never`**, **`assert_never`** 3.11+; **PEP 695** type parameters and the `type X = ...` alias statement 3.12+; **`TypeIs`** (PEP 742) 3.13+. The big one is **deferred annotation evaluation (PEP 649/749) in 3.14** — annotations are no longer eagerly evaluated at definition time, which changes how runtime-introspecting libraries read them and largely retires the `from __future__ import annotations` workaround. Also note `collections.abc` is the modern home for `Iterable`/`Sequence`/`Mapping`; the `typing.` versions are deprecated aliases.

---

## A · The core fact

**1. What a type hint is — and what it categorically is not**
`age: int` is an annotation stored on the function/class object. Python **does not check it at runtime**. Nothing stops `age="old"`. Internalise this before anything else, because every other concept here is either a static tool built on top of it, or a runtime library choosing to read it.

**2. Why bother, if nothing enforces them**
Three separate payoffs that get conflated: editor autocomplete and inline docs; a static checker catching a class of bug before runtime; and libraries that *opt in* to reading annotations and enforcing them themselves. Pydantic is the third kind — that's the whole trick.

**3. Static type checkers**
`mypy` (the reference implementation), `pyright` (what Pylance in VS Code runs), and the newer Rust-based checkers. How you actually run one — editor extension versus command line versus CI — and why two checkers disagree on the same file.

**4. Where annotations physically live**
`__annotations__` on functions, classes, and modules. `typing.get_type_hints()` and why it differs from reading `__annotations__` directly (it resolves strings and follows `from __future__ import annotations`).

## B · Composing types

**5. Built-in generics**
`list[str]`, `dict[str, int]`, `tuple[int, ...]`, `set[str]`. What the parameter actually asserts — and why a bare `list` is a strictly weaker claim than `list[str]`.

**6. Abstract collection types — `Iterable`, `Sequence`, `Mapping`**
The everyday best practice, and the one most people never learn: **annotate parameters with the weakest type the function actually needs.** A function that only loops over its argument should say `Iterable[str]`, not `list[str]` — annotated as `list`, it rejects a tuple, a set, a `range`, and a generator, none of which is a real requirement. The rule of thumb that falls out: **accept abstract, return concrete.** It sounds like style advice until concept 15 explains why the checker genuinely cannot let a `list[Dog]` through where a `list[Animal]` is asked for — and `Sequence` is the thing that fixes it.

**7. Unions and optionality**
`str | None` (3.10+) vs the older `Optional[str]` / `Union[str, None]`. The distinction the Pydantic notes leaned on: "optional" meaning *has a default* is not the same as "optional" meaning *can be None*. All four combinations are expressible and mean different things.

**8. The extreme types — `Any`, `object`, `Never`**
`Any` disables checking; `object` accepts anything but permits nothing; `Never` (3.11+, formerly `NoReturn`) is the type with no values at all — what a function that always raises "returns". Reaching for `Any` is a decision to stop type-checking a region of code, not a description of the data. `Never` earns its place through `assert_never()`, which turns "did I handle every case?" into a question the checker answers for you.

**9. `Literal`, `Final`, `ClassVar`**
Restricting to exact values (already used for the `status` field in the Pydantic notes), constants, and class-level vs instance-level attributes. `Literal` is also what makes the exhaustiveness check in concept 8 possible.

**10. `Callable` and `ParamSpec`**
Typing a function *as a value* — the thing you need the moment you write a decorator (folder 03) or a `default_factory` (already seen in Pydantic). `ParamSpec` is what lets a decorator preserve the signature of what it wraps instead of flattening it to `(*args, **kwargs)`.

**11. `TypedDict`**
Dicts with a known key schema. The motivating comparison: `dict[str, str | int | None]` types every value as the same union, so nothing catches an `age` that became a string during processing; a `TypedDict` types each key separately and does. Then the natural comparison against a Pydantic model — static-only checking, zero runtime cost, no validation.

**12. Type aliases and `NewType`**
Two different jobs that look alike. A **type alias** (`type UserId = int`, 3.12+; or `UserId: TypeAlias = int` before that) is a *new name for the same type* — pure readability, and the checker treats the two as interchangeable. **`NewType`** creates a genuinely *distinct* type over the same representation. The example that makes the difference obvious: RGB and HSL are both `tuple[int, int, int]`, so with aliases nothing stops you passing one where the other belongs — a bug that runs perfectly and produces the wrong colour. With `NewType`, the checker rejects it and the conversion has to be written down.

## C · Generics and abstraction

**13. `TypeVar` and generic functions**
"Returns the same type it was given." A function picking a random element from a list must not be annotated `list[Any] -> Any` — that runs fine and destroys autocomplete at every call site. Both the classic `T = TypeVar('T')` form and the 3.12+ `def f[T](...)` syntax, since real codebases contain both.

**14. Generic classes**
`class Repository[T]` — the pattern behind every typed container and every `Response[T]`-shaped API wrapper.

**15. Variance — covariant, contravariant, invariant**
Why `list[Dog]` is **not** a `list[Animal]`, and why `Sequence[Dog]` **is** a `Sequence[Animal]`. The one-sentence reason: a mutable container has to work in both directions, so allowing the substitution would let someone put a `Cat` into your list of dogs. Read-only containers have no such problem, which is why the abstract types from concept 6 behave differently from the concrete ones. Plain `TypeVar`s are invariant by default; `covariant=`/`contravariant=` were how you said otherwise before PEP 695, which infers it. Asked directly in interviews, and one of the few typing questions where a wrong answer is obvious.

**16. `Protocol` — structural typing**
Duck typing, made checkable. "Anything with a `.read()` method" expressed as a type, with no inheritance required — which is the only option when the class is one you don't own. `@runtime_checkable` and its limits. The comparison that gets asked: **`Protocol` vs ABC** — an ABC enforces at runtime and forbids instantiating an incomplete class, a Protocol enforces at check time and requires nothing of the implementer.

**17. `@overload`**
One function, several legitimate signatures. Why the implementation signature is invisible to callers, and how it differs from a `TypeVar` — `TypeVar` ties the output type *to* the input, `@overload` enumerates unrelated input/output pairings.

**18. Narrowing — `isinstance`, `TypeGuard`, `TypeIs`**
How a checker learns that inside `if isinstance(x, str):` the variable is a `str`, and how to teach it the same thing about a custom predicate function. `TypeIs` (3.13+) narrows in both branches where `TypeGuard` only narrows the positive one — the difference that makes `TypeIs` the better default for most predicates.

**19. `Self`**
A method that returns "the class it was actually called on", not the class it was defined in. Annotating a builder method or an alternative constructor `-> Self` instead of `-> Employee` is what keeps the subclass's return type correct — otherwise every fluent chain on a subclass silently degrades to the base type.

## D · Runtime interaction

**20. `Annotated` — metadata attached to a type**
`Annotated[int, Field(gt=0)]` reads as *"an `int`, plus some metadata"*. Static checkers see only the `int`; runtime libraries read the extras. This is the mechanism the whole Pydantic constraints note was built on and never explained, and the same mechanism behind FastAPI's `Depends`.

**21. Deferred evaluation and forward references**
String annotations, `from __future__ import annotations`, quoted `"BlogPost"` self-references, and the `if TYPE_CHECKING:` guard for imports that exist only for the checker. Then the 3.14 change (PEP 649/749) that reworks this whole area.

## E · Living with a type checker

*Everything above is what the type system can express. This section is what it costs to actually run one on a codebase that already exists — which is where the senior-level questions are.*

**22. Third-party libraries — stubs and `py.typed`**
Most of your annotations are worthless if the libraries you call are untyped: the checker treats every value coming out of them as `Any`, and `Any` spreads. Stub packages (`types-requests`, `types-redis`) supply the missing annotations from outside; a library that ships its own includes an empty `py.typed` marker file to say so. Includes the honest case — a library with neither, and what your options are.

**23. Escape hatches — `cast`, `# type: ignore`, and `Any`**
Three ways to tell the checker you know better, in increasing order of bluntness. `cast()` asserts a type without any runtime effect; `# type: ignore[code]` silences one specific error on one line; `Any` switches checking off for a region. When each is legitimate, and why an un-coded bare `# type: ignore` is the one to avoid — it silences future errors you never saw.

**24. Gradual adoption and strict mode**
Type hints are explicitly designed to be added incrementally — annotate the function you're already touching, commit, move on. What `--strict` actually turns on (`disallow_untyped_defs` and friends), why enabling it on an existing codebase produces hundreds of errors at once, and the per-module configuration that lets you hold a strict core alongside an untyped edge. **The question this answers: "how would you introduce typing to a large untyped service?"** — and "all at once" is the wrong answer.

**25. Choosing a structured-data type**
Once several ways exist to say "an object with these fields", the decision has to be made deliberately: plain `dict`, `TypedDict`, `NamedTuple`, `@dataclass`, or a Pydantic `BaseModel`. The axes that decide it — is the data already a dict, does it need methods, does it need mutability, is it crossing a trust boundary — and the general shape of the answer: `TypedDict` for dicts you already have, `dataclass` for objects you're creating, `BaseModel` for anything arriving from outside. Mechanics live in 02 and 09; the *choice* is a typing question and is asked as one.

## F · Traps

**26. Common traps**
Mutable defaults; annotating `self`; the `Optional` vs default confusion from concept 7; over-annotating obvious assignments until the noise outweighs the signal; and the perennial one — believing a hint is a guarantee.

---

## Coverage — what is written and what is not

| # | Concept | Note |
|---|---|---|
| 1 | What a hint is / is not | `01-Hinting-Vs-Checking-Vs-Validation` |
| 2 | Why bother | `01-Hinting-Vs-Checking…` |
| 3 | Static type checkers | `01-Hinting-Vs-Checking…` — described, not run |
| 4 | Where annotations live | `01-Hinting-Vs-Checking…` — `__annotations__` only |
| 5–26 | everything else | — |

**3.5 of 26 written.** Concept 3 is marked partial deliberately: that section was written without a checker installed on this machine, so it describes the error output rather than showing a captured run. Installing `mypy` and re-running the note's examples would close it.

## Deferred

| Topic | Goes to |
|---|---|
| `@classmethod` / `@property` / ABCs as OOP constructs | 02 |
| `dataclass` and `NamedTuple` mechanics | 02 |
| Writing decorators that preserve signatures | 03 |
| `Annotated` as Pydantic *uses* it (constraints, `Field`) | 09 (written) |
| Runtime validation, coercion, `ValidationError` | 09 (written) |
| Typing async code, `Coroutine`/`Awaitable` annotations | 08 |

## Where this already shows up in these notes

`09-Pydantic/03` and `/04` use `Annotated`, `Literal`, `list[str]`, and `X | None` heavily — all correct, none explained as typing features. `08-Async` annotates coroutines throughout. `03-Decorators/06` hits concept 10's territory the moment `@wraps` appears. A pass back over those after this folder is written should feel like recognition, not new information.

## Interview hooks

Seven questions that recur, now each with a concept behind it:

- *"Are type hints enforced at runtime?"* — concept 1, and the answer that separates people is **"no — Pydantic enforces them, by choosing to read them at runtime."**
- *"`Protocol` or ABC — which and why?"* — concept 16. Runtime enforcement vs check-time, and whether you own the class.
- *"Why isn't `list[Dog]` a `list[Animal]`?"* — concept 15.
- *"Why would you annotate a parameter `Sequence[str]` rather than `list[str]`?"* — concept 6, and it's really concept 15 wearing everyday clothes.
- *"How would you add typing to a large untyped codebase?"* — concept 24.
- *"What do you do about a dependency with no type hints?"* — concept 22.
- *"When would you use `TypedDict` over a dataclass over a Pydantic model?"* — concept 25.

Sarvam's Stage 2 screen covers foundational Python, and Pydantic v2 strict schema enforcement is named explicitly under agent orchestration.

## Sources to verify against

- [`typing` — standard library docs](https://docs.python.org/3/library/typing.html) · [the typing spec](https://typing.python.org/en/latest/spec/) — now the authoritative home, better than the stdlib page for concepts 15 and 16
- [mypy documentation](https://mypy.readthedocs.io/) — the *cheat sheet* page for B, *more types* for C, *existing code* for concept 24
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) · [PEP 483 — The Theory of Type Hints](https://peps.python.org/pep-0483/), which is where variance is actually explained
- [PEP 593 — `Annotated`](https://peps.python.org/pep-0593/) · [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/) · [PEP 742 — `TypeIs`](https://peps.python.org/pep-0742/) · [PEP 649 — Deferred Annotations](https://peps.python.org/pep-0649/)
