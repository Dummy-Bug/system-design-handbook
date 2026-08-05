#python #type-hints #typing #python-utils #syllabus

# 01 · Type Hints — Syllabus

18 concepts. **Generic** — the language feature, not any one library's use of it.

> Learn the whole typing surface first, *then* notice which parts Pydantic/FastAPI happen to exercise. Deriving the list from "what I've already seen in Pydantic" silently drops `Protocol`, `overload`, and generics — and those are exactly what a typing question in a screen reaches for.

**Why this sits first:** everything downstream reads annotations. Pydantic *is* "annotations, enforced at runtime." FastAPI routes are annotation-driven. `Annotated[...]` — the V2 constraint mechanism already used throughout the Pydantic notes — is a typing feature that was never actually explained there, only used.

**Currency check (2026-08-04):** Python 3.14 is current stable. Three version lines matter here and should be re-verified against the changelog before relying on them: **built-in generics** (`list[str]` over `List[str]`) since 3.9; **`X | None`** union syntax over `Optional[X]` since 3.10; **PEP 695** type-parameter syntax (`def f[T](x: T) -> T`) since 3.12. The big recent one is **deferred/lazy annotation evaluation (PEP 649/749) landing in 3.14** — annotations are no longer eagerly evaluated at definition time, which changes how runtime-introspecting libraries (Pydantic among them) read them and largely retires the `from __future__ import annotations` workaround. Verify current status before writing anything that depends on evaluation timing.

---

## A · The core fact

**1. What a type hint is — and what it categorically is not**
`age: int` is an annotation stored on the function/class object. Python **does not check it at runtime**. Nothing stops `age="old"`. Internalise this before anything else, because every other concept here is either a static tool built on top of it, or a runtime library choosing to read it.

**2. Why bother, if nothing enforces them**
Three separate payoffs that get conflated: editor autocomplete and inline docs; a static checker catching a class of bug before runtime; and libraries that *opt in* to reading annotations and enforcing them themselves. Pydantic is the third kind — that's the whole trick.

**3. Static type checkers**
`mypy` (the reference implementation), `pyright` (what Pylance in VS Code runs), and the newer Rust-based checkers. Strictness levels, `# type: ignore`, and why two checkers disagree on the same file.

**4. Where annotations physically live**
`__annotations__` on functions, classes, and modules. `typing.get_type_hints()` and why it differs from reading `__annotations__` directly (it resolves strings and follows `from __future__ import annotations`).

## B · Composing types

**5. Built-in generics**
`list[str]`, `dict[str, int]`, `tuple[int, ...]`, `set[str]`. What the parameter actually asserts — and why a bare `list` is a strictly weaker claim than `list[str]`.

**6. Unions and optionality**
`str | None` (3.10+) vs the older `Optional[str]` / `Union[str, None]`. The distinction the Pydantic notes leaned on: "optional" meaning *has a default* is not the same as "optional" meaning *can be None*.

**7. `Any`, `object`, and the escape hatches**
`Any` disables checking; `object` accepts anything but permits nothing. Why reaching for `Any` is usually a decision to stop type-checking a region of code, not a description of the data.

**8. `Literal`, `Final`, `ClassVar`**
Restricting to exact values (already used for the `status` field in the Pydantic notes), constants, and class-level vs instance-level attributes.

**9. `Callable` and `ParamSpec`**
Typing a function *as a value* — the thing you need the moment you write a decorator (folder 03) or a `default_factory` (already seen in Pydantic).

**10. `TypedDict`**
Dicts with a known key schema. The natural comparison point against a Pydantic model: static-only checking, zero runtime cost, no validation.

## C · Generics and abstraction

**11. `TypeVar` and generic functions**
"Returns the same type it was given." Both the classic `TypeVar` form and the 3.12+ `def f[T](...)` syntax, since real codebases contain both.

**12. Generic classes**
`class Repository[T]` — the pattern behind every typed container and every `Response[T]`-shaped API wrapper.

**13. `Protocol` — structural typing**
Duck typing, made checkable. "Anything with a `.read()` method" expressed as a type, with no inheritance required. Sets up the `Protocol` vs ABC comparison that belongs to folder 02.

**14. `@overload`**
One function, several legitimate signatures. Why the implementation signature is invisible to callers.

**15. Narrowing — `isinstance`, `TypeGuard`, `TypeIs`**
How a checker learns that inside `if isinstance(x, str):` the variable is a `str`, and how to teach it the same thing about a custom predicate function.

## D · Runtime interaction — the part that matters for Pydantic

**16. `Annotated` — metadata attached to a type**
`Annotated[int, Field(gt=0)]` reads as *"an `int`, plus some metadata"*. Static checkers see only the `int`; runtime libraries read the extras. This is the mechanism the whole Pydantic constraints note was built on and never explained.

**17. Deferred evaluation and forward references**
String annotations, `from __future__ import annotations`, quoted `"BlogPost"` self-references, and the `if TYPE_CHECKING:` guard for imports that exist only for the checker. Then the 3.14 change (PEP 649/749) that reworks this whole area.

**18. Common traps**
Mutable defaults; invariance vs covariance (why `list[Dog]` is *not* a `list[Animal]`); annotating `self`; and the perennial one — believing a hint is a guarantee.

---

## Deferred

| Topic | Goes to |
|---|---|
| `@classmethod` / `@property` / ABCs — the OOP side | 02 |
| Writing decorators that preserve signatures | 03 |
| `Annotated` as Pydantic *uses* it (constraints, `Field`) | 09 (written) |
| `dataclass` vs `BaseModel` comparison | 02 or 09 |

## Where this already shows up in these notes

`09-Pydantic/03` and `/04` use `Annotated`, `Literal`, `list[str]`, and `X | None` heavily — all correct, none explained as typing features. `08-Async` annotates coroutines throughout. A pass back over those after this folder is written should feel like recognition, not new information.

## Interview hooks

Sarvam's Stage 2 screen covers foundational Python; Pydantic v2 strict schema enforcement is named explicitly under agent orchestration. The answer that separates people: *"annotations aren't enforced — Pydantic enforces them, by reading them at runtime."*

## Sources to verify against

- [`typing` — standard library docs](https://docs.python.org/3/library/typing.html)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) · [PEP 593 — `Annotated`](https://peps.python.org/pep-0593/) · [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/) · [PEP 649 — Deferred Annotations](https://peps.python.org/pep-0649/)
- [mypy documentation](https://mypy.readthedocs.io/)
