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
`Any` disables checking; `object` accepts anything but permits nothing; `Never` (3.11+, formerly `NoReturn`) is the type with no values at all — what a function that always raises "returns". Reaching for `Any` is a decision to stop type-checking a region of code, not a description of the data. The other half of `Any` is that it **spreads** — every operation on an `Any` yields another `Any`, so one at a boundary disables checking for everything downstream. `Never` here is the return type of a function that always raises; its second use, `assert_never()`, was moved to concept 9 because it needs `Literal` to mean anything.

**9. `Literal`, `Final`, `ClassVar` — and `assert_never`**
Restricting to exact values, constants, and class-level vs instance-level attributes. **`assert_never` lives here, not in concept 8** — the exhaustiveness check only means anything once `Literal` exists, so it was moved rather than taught twice. The demo is derived and verified: a three-state `Literal` with `assert_never` at the bottom passes; adding a fourth state and touching nothing else produces `error: Argument 1 to "assert_never" has incompatible type "Literal['failed']"; expected "Never"`, naming the exact unhandled case; the same omission without `assert_never` reports `Success` and silently does nothing at runtime.

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

**Two kinds of note in this folder, deliberately separated.**

- **At the folder root** — concepts worked through Socratically, then written from what was derived. These are *learned*.
- **In `Video/`** — notes made from watching a tutorial, kept verbatim as anchors. Correct and verified, but **not yet learned**. When a rung is properly worked through, its Socratic note appears at the root and the `Video/` file stays put as the original reference, so re-watching is never necessary.

Counting them together would be the exact accounting trap this vault warns about, so they're counted apart.

| # | Concept | Learned (root) | Anchor (`Video/`) |
|---|---|---|---|
| 1 | What a hint is / is not | `01-What-A-Type-Hint-Is` | `01-Hinting-Vs-Checking…` |
| 2 | Why bother | `02-Why-Bother-If-Nothing-Enforces-Them` | `01-Hinting-Vs-Checking…` |
| 3 | Static type checkers | `03-Static-Type-Checkers` | `01-Hinting-Vs-Checking…` |
| 4 | Where annotations live | `04-Where-Annotations-Live` | `01-Hinting-Vs-Checking…` |
| 5 | Built-in generics | `05-Built-In-Generics` | `05-Built-In-Generics` |
| 6 | Abstract collection types | `06-Abstract-Collection-Types` | — |
| 7 | Unions and optionality | `07-Unions-And-Optionality` | `Video/07-Unions-And-Optionality` |
| 8 | `Any`, `object`, `Never` | `08-Any-Object-Never` | partial — `13-TypeVar…` covers `Any` |
| 9 | `Literal`, `Final`, `ClassVar`, `assert_never` | `09-Literal-Final-ClassVar` | — |
| 10 | `Callable`, `ParamSpec` | `10-Callable-And-ParamSpec` | — |
| 11 | `TypedDict` | `11-TypedDict` | `Video/11-TypedDict` |
| 12 | Type aliases and `NewType` | `12-Type-Aliases-And-NewType` | `Video/12-Type-Aliases-And-NewType` |
| 13 | `TypeVar`, generic functions | `13-TypeVar-And-Generic-Functions` | `Video/13-TypeVar-And-Generic-Functions` |
| 14 | Generic classes | `14-Generic-Classes` | — |
| 15 | Variance | `15-Variance` | — |
| 16 | `Protocol` — structural typing | `16-Protocol` | — |
| 17 | `@overload` | `17-Overload` | — |
| 18 | Narrowing — `isinstance`, `TypeGuard`, `TypeIs` | `18-Narrowing` | — |
| 19 | `Self` | `19-Self` | — |
| 20 | `Annotated` | `20-Annotated` | — |
| 21 | Deferred evaluation | `21-Deferred-Evaluation` | — |
| 22 | Stubs and `py.typed` | `22-Third-Party-Libraries` | `22-Stubs-And-Third-Party-Types` |
| 23 | `cast`, `# type: ignore`, `Any` | `23-Escape-Hatches` | — |
| 24 | Gradual adoption and strict mode | `24-Gradual-Adoption` | — |
| 25 | Choosing a structured-data type | `25-Choosing-A-Structured-Data-Type` | partial — `11-TypedDict` |
| 26 | Common traps | `26-Common-Traps` | — |

**Learned: 26 of 26 — the folder is complete, closed 2026-08-08.** Every section A through F is done, and every `Video/` anchor has a derived root note behind it; nothing remains anchor-only.

**Example convention, adopted 2026-08-07 from concept 12 onward:** examples are drawn from **generic agent/LangGraph concepts** — thread ids, run ids, tool names, node names, model calls — rather than arbitrary domains or employer-specific internals. The guardrail: the example must stay small enough that the *typing* point is what's visible. When the domain starts needing its own explanation, it has stopped being a good example.

`Video/01-Hinting-Vs-Checking-Vs-Validation`, `Video/05-Built-In-Generics` and `Video/07-Unions-And-Optionality` are now fully superseded as *learning* sources; everything they covered has been derived rather than watched. They stay in `Video/` as the record of what the tutorial said.

**No unlearned rungs remain.** The folder closed on 2026-08-08.

**What is still open, and does not belong to any concept:**

- **`03-Static-Type-Checkers` owes a section on checker disagreement.** Two verified cases are logged in the debt table below — concept 16's protocol parameter-name mismatch, and concept 17's overload argument-expansion split. That note currently asserts checkers disagree; it now has two runnable examples instead.
- **Revision pass planned for Sunday 2026-08-09.** Each note ends with a *"What this concept claims"* section — one sentence plus four or five numbered points. Those are the retrieval surface; re-reading the note bodies is the fluency illusion this vault warns about. See the ordering below; the remaining concepts are not taken in numeric order.

## Learning order for the rest of the folder (decided 2026-08-07)

The stated goal changed: **build production-grade coding / RAG / conversational agents**, learning the typing concepts those agents actually use *first*. Folder *sequence* is unchanged — within a folder, pick by priority.

A two-pass split was drawn up, with 17 / 19 / 24 deferred to a second pass. **That second pass was then folded back in** — three concepts isn't worth a separate sweep, and concept 24 is one of the seven interview hooks. So: **all 26 concepts, full Socratic depth, agent-relevant ones first.** This reorders; it does not abbreviate.

Remaining order: **none — all done.** (17, 18, 19, 20, 21, 22, 23, 24, 25 and 26 all learned; the folder closed 2026-08-08.)

A fast single-demo pass for 26 / 17 / 19 / 24 was floated on 2026-08-07 and **withdrawn the same day.** The reason given was decisive: this is not interview-only prep, and the AI course has barely started, so frontloading fundamentals is correct sequencing — this folder is load-bearing for `02` (dataclasses, properties, ABCs), `03` (decorators), `08` (async annotations) and `09` (annotations enforced at runtime), each of which becomes recognition rather than new material. All remaining concepts get full Socratic depth.

**Agent-code-bearing, taken first:**

| Order | # | Concept | Why it comes first |
|---|---|---|---|
| ~~1~~ | ~~20~~ | ~~`Annotated`~~ | **Done.** `Annotated[list[str], operator.add]` **is** the LangGraph state idiom — the reducer is metadata on a type. Also FastAPI `Depends` and every Pydantic `Field` constraint. |
| ~~2~~ | ~~25~~ | ~~Choosing a structured-data type~~ | **Done.** Decided on four questions: is it already a dict, does it need behaviour, must it be hashable/frozen, did it come from outside — the last outranking the rest. |
| ~~3~~ | ~~18~~ | ~~Narrowing~~ | **Done.** `isinstance` narrows both branches; factoring the check into a `-> bool` function destroys that, because a call site is checked from the signature alone. `TypeIs` (both branches, subtype required) over `TypeGuard` (positive only, no subtype requirement) as the default. |
| ~~4~~ | ~~23~~ | ~~Escape hatches — `cast`, `# type: ignore`~~ | **Done.** Three hatches ranked by *reach*: `cast` one value, `# type: ignore[code]` one line and one code, `Any` every line the value reaches. None verify anything. The test for legitimacy: a hatch may **record** a fact established some other way, never **substitute** for establishing it — so at a trust boundary the answer is validate-then-`cast`, or a validating model and no hatch at all. |
| ~~5~~ | ~~22~~ | ~~Stubs and `py.typed`~~ | **Done.** A `.pyi` stub is a types-only file read *instead of* the source; `py.typed` is an empty marker granting permission to trust the source's own annotations — deleting zero bytes takes an installed annotated package from `int` to `Any`. Six options ranked, and the usual right answer is none of them: a thin typed wrapper module that confines the `Any` to one reviewable file. |
| ~~6~~ | ~~21~~ | ~~Deferred evaluation, `TYPE_CHECKING`~~ | **Done.** A `class` statement is executed, so its own name isn't bound until the body finishes — `-> Agent` inside `class Agent` is a `NameError` at import time while mypy passes. Quotes or the future import fix the annotation; `if TYPE_CHECKING:` (a plain constant, `False` at runtime) fixes the import. Circular imports need **both** — either alone still crashes, just on a different line. |
| ~~7~~ | ~~26~~ | ~~Common traps~~ | **Done.** Not typing bugs — Python's execution model showing through. A `def` evaluates its **defaults** at definition, so `= []` is one shared list forever. `list[str] = None` is a contradiction (implicit `Optional` is dead). "Optional" means two unrelated things: the `=` and the `\| None`. `self` needs no annotation but `-> "Agent"` degrades every subclass → 19. |

**Taken last, and still taken:** ~~**17** `@overload`~~ (**done** — enumerate calling patterns when the return type depends on *how* you call rather than what you pass; `Literal` makes `True` and `False` different *types*, which is what `TypeVar` couldn't do since Python has no conditional types), ~~**19** `Self`~~ (**done** — names the class a method was *called on*, not the one it was *written in*; the check-time twin of `type(self)`. Per-subclass overrides are legal by `15-Variance`'s covariant returns but duplicate the body and break again one level down), ~~**24** gradual adoption and strict mode~~ (**done** — and keeping it in was right: `--strict` turns out to be **thirteen flags** under one name, which gives a second migration dial alongside per-module overrides. The answer to the hook is *"strict by default with a shrinking exemption list"*, and the surviving errors mark the typed/untyped boundary, i.e. the work queue).

**Vocabulary note for concept 15:** the note deliberately avoids arrow notation (`sub → base`), which proved ambiguous when taught — it reads as both "substitute this for that" and "this becomes that". It uses **wider** / **narrower** instead, defined once, with every rule phrased identically as *"you have this; can you pass it where that is wanted?"*

`14-Generic-Classes` also settles the Java-erasure question raised back in concept 1: `Store[str]()` produces a plain `Store`, `type(a) is type(b)` for differently-parameterised stores, so erasure applies to **generic type parameters** exactly as in Java — `age: int` was never that case.

Concept 11's own thread — that `TypedDict` never validates, and choosing between it and a runtime-validating model is a real decision — is **closed by `25-Choosing-A-Structured-Data-Type`**. Concept 10 introduced the decorator syntax `@logged` ≡ `greet = logged(greet)` as one line of vocabulary. The mechanics — `functools.wraps`, decorators with arguments, class decorators — remain deferred to folder 03, which should now feel like recognition.

**Depth decision (2026-08-07).** A three-way triage was proposed — full depth for the four interview hooks, a fast single-demo pass for six, anchor-only for seven — on the grounds that seventeen more rungs at concepts 1–9's depth is expensive against a Jan-2027 target with `02-Observability` through `06-Agent-Reliability` still empty.

**Overruled deliberately: all 26 concepts in this folder get the full Socratic treatment.** The pace question is deferred to the *rest* of `00-Python-Utils` — folders 02, 03, 08 and 09 — and will be decided when this folder closes, not before.

**Convention adopted 2026-08-07:** every output block in this folder is prefixed with the command that produced it — `$ mypy file.py` or `$ python3 file.py`. All 9 existing notes were retrofitted (32 blocks). `03-Static-Type-Checkers` now carries the reference table for telling checker output from Python output by shape: bracketed `[error-codes]` are always mypy, `Traceback`/`…Error` is always Python.

Threads left hanging on purpose, each owed to a later rung:

| Left by | Owed to | What |
|---|---|---|
| ~~5~~ | ~~11~~ | **Closed.** `11-TypedDict` opens on concept 5's three lines and reverses every verdict. |
| ~~6~~ | ~~15~~ | **Closed.** `15-Variance` gives the real reason: a writable container is unsafe in both directions, a read-only one is safe sub-to-base. |
| ~~7~~ | ~~18~~ | **Closed.** `18-Narrowing` opens on concept 7's `is None` case and generalises it — `isinstance` on both branches, then `TypeIs`/`TypeGuard` for predicates of your own. |
| ~~5, 7~~ | ~~22~~ | **Closed.** `22-Third-Party-Libraries` builds a stub from scratch — `.pyi`, types-only, signatures with `...` bodies, read *instead of* the real source — and proves which one wins by making the two disagree on purpose. |
| ~~11~~ | ~~23~~ | **Closed, backfilled 2026-08-08.** Concept 11 showed `type(user)` is `dict` but never drew the consequence that you therefore cannot ask *"is this a `User`?"* at all. `23-Escape-Hatches` needed exactly that gap to motivate `cast`, so `11-TypedDict` gained a section for it — the `__mro__`-says-yes / `type()`-says-no pair read together, the double refusal by mypy **and** Python, and a forward pointer to 23. |
| ~~13~~ | ~~16~~ | **Closed.** Constraints reached for because unrelated classes share a *method* — `16-Protocol` is that tool, and `Candidate`/`ToolCall`/`RetrievedDoc` is the same example carried over. |
| 16 | — | **Open, unowned.** mypy accepts a protocol whose implementer renames a parameter; pyright rejects it by name. Verified on the same file. No later rung owns this — it belongs to `03-Static-Type-Checkers`, which now has a concrete case for its "why two checkers disagree" claim. |
| 17 | — | **Open, unowned — second instance.** Given overloads on `Literal[True]`/`Literal[False]`, a call passing a runtime `bool` is a `[call-overload]` error in mypy and **accepted** by pyright, which does *argument type expansion* (split the `bool` into its literals, resolve once per piece, union the results → `AsyncIterator[str] \| str`). mypy reveals `Any`. Same file, opposite verdicts. Also for `03-Static-Type-Checkers`; the portable workaround is in `17-Overload`. |

**Verification note (2026-08-06).** Every checker message quoted in notes 05, 07, 11, 12, 13, and 22 was captured from a real run of **mypy 2.3.0** on Python 3.13.3 via `uvx mypy`, not written from memory. Runtime behaviour in those notes (`NewType` returning a plain tuple, `TypedDict` instances being real dicts, `__type_params__`, `User.__value__`) was executed and its output pasted. This matters because an earlier version of note 01 asserted that a static checker reads `__annotations__` — it does not, it reads the source text — and that error survived because nothing in the note had been run.

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
- *"`Protocol` or ABC — which and why?"* — concept 16, **answerable now**. The sharpest form of the answer is directional: an ABC points from the implementer to the abstraction, a `Protocol` points from the consumer to it. Own the hierarchy and want incomplete implementations to be impossible → ABC (enforced at runtime, at instantiation). Describing a boundary that third-party objects and test doubles arrive at → `Protocol`.
- *"Why isn't `list[Dog]` a `list[Animal]`?"* — concept 15.
- *"Why would you annotate a parameter `Sequence[str]` rather than `list[str]`?"* — concept 6, and it's really concept 15 wearing everyday clothes.
- *"How would you add typing to a large untyped codebase?"* — concept 24, **answerable now**. Not "turn on strict mode" — that prints ~1600 errors on a 400-function service (one per definition, one per call site), CI goes red on day one, and the team learns to ignore the checker. The answer is **strict by default with an explicit per-module exemption list that only shrinks**, plus the second dial: `--strict` is thirteen named flags, so one check can go on repo-wide at a time. The kicker: a per-module setting applies where the error is *reported*, so exempting `legacy.*` leaves call sites in `core` red — and those surviving errors are exactly the typed/untyped boundary, which is the work queue.
- *"What do you do about a dependency with no type hints?"* — concept 22, **answerable now**. First ask which case it is: annotated but unmarked → `follow_untyped_imports` scoped to that module; a stub package exists → install it; genuinely untyped → a **thin typed wrapper module** of your own that absorbs the `Any` in one file and re-exports behind signatures you wrote. A hand-written `.pyi` is the fallback, and the reason it's a fallback is the sharp bit: a stub is the *complete* truth about its module, so anything you omit stops existing for the checker while still running fine.
- *"When would you use `TypedDict` over a dataclass over a Pydantic model?"* — concept 25, **answerable now**. `TypedDict` for dicts you already have, `@dataclass` for objects you create, `NamedTuple` when it must be hashable or frozen, a validating model for anything arriving from outside — and the last question outranks the others, because the argument for validation is *where* the failure surfaces, not whether one happens.

Sarvam's Stage 2 screen covers foundational Python, and Pydantic v2 strict schema enforcement is named explicitly under agent orchestration.

## Sources to verify against

- [`typing` — standard library docs](https://docs.python.org/3/library/typing.html) · [the typing spec](https://typing.python.org/en/latest/spec/) — now the authoritative home, better than the stdlib page for concepts 15 and 16
- [mypy documentation](https://mypy.readthedocs.io/) — the *cheat sheet* page for B, *more types* for C, *existing code* for concept 24
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) · [PEP 483 — The Theory of Type Hints](https://peps.python.org/pep-0483/), which is where variance is actually explained
- [PEP 593 — `Annotated`](https://peps.python.org/pep-0593/) · [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/) · [PEP 742 — `TypeIs`](https://peps.python.org/pep-0742/) · [PEP 649 — Deferred Annotations](https://peps.python.org/pep-0649/)
