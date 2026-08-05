#python #decorators #closures #python-utils #syllabus

# 03 · Decorators — Syllabus

14 concepts. **Generic** — the language mechanism, not the specific decorators any framework ships.

> Every framework in this vault is decorator-driven — `@app.get`, `@field_validator`, `@computed_field`, `@pytest.fixture`, `@asynccontextmanager`. All of them have been *used* and none explained. The goal here is that a decorator stops being magic syntax and becomes a function you could have written.

**Why this sits third:** it needs functions-as-objects and closures (covered here from scratch), and it needs `@classmethod`/`@property` from folder 02 as worked examples of decorators that do something genuinely non-obvious.

**Currency check (2026-08-04):** stable area. The one thing worth verifying is typing support — `ParamSpec` (3.10+) is what lets a decorator preserve its wrapped function's signature for a type checker, and `functools.wraps` has never done that job despite frequently being assumed to.

---

## A · What a decorator is built from

**1. Functions are objects**
Assignable, passable, returnable. Nothing about decorators makes sense until this does.

**2. Closures**
An inner function that captures a variable from its enclosing scope, and keeps it alive after the outer call returns. `nonlocal`, and the late-binding-in-a-loop trap.

**3. Higher-order functions**
Functions that take or return functions. A decorator is just this, with syntax.

**4. `@` is syntactic sugar**
`@deco` above `def f` is exactly `f = deco(f)`. Writing it out longhand once permanently demystifies the syntax.

## B · Writing them

**5. The basic function decorator**
`def deco(func): def wrapper(*args, **kwargs): ...; return wrapper`. The `*args, **kwargs` pass-through and why it's non-negotiable for a general-purpose decorator.

**6. `functools.wraps` — the one you must not forget**
Without it, the decorated function's `__name__`, `__doc__`, and `__module__` are silently replaced by the wrapper's. Breaks introspection, debuggers, and anything that reads metadata off functions — *including framework machinery that inspects your handlers.*

**7. Decorators that take arguments**
The three-level nest (`deco(arg)` returns the real decorator). Why `@retry(times=3)` needs one more layer than `@retry`.

**8. Class-based decorators**
Implementing `__call__` instead of nesting. When holding state across calls makes a class the cleaner shape.

**9. Stacking decorators**
Bottom-up application order, and how that explains why `@computed_field` sits *above* `@property` rather than below it — a concrete case already sitting in the Pydantic notes.

**10. Decorating methods, and decorating classes**
The extra wrinkle when `self` is in play; and decorators applied to a whole class.

## C · The ones that ship with Python

**11. `@property`, `@classmethod`, `@staticmethod` revisited**
Now explainable rather than memorisable — they're descriptors (folder 02, concept 15) wearing decorator syntax.

**12. `functools.lru_cache` / `functools.cache`**
Memoisation for free. `maxsize`, `cache_info()`, and the hard requirement that arguments be hashable. The conceptual ancestor of every caching layer.

**13. `contextlib.contextmanager` and `functools.singledispatch`**
Two decorators that do something structurally surprising — one turns a generator into a context manager (the bridge to folders 04 and 05), the other adds type-based dispatch to a plain function.

## D · Doing it properly

**14. Typing a decorator**
`ParamSpec` + `TypeVar` so the checker still sees the original signature through the wrapper. The practical fallback when it gets ugly, and why `functools.wraps` fixes runtime introspection but *not* static types.

---

## Deferred

| Topic | Goes to |
|---|---|
| `@contextmanager` in depth | 05 |
| `@pytest.fixture`, `@pytest.mark.parametrize` | 10 |
| Retry/circuit-breaker decorators | 06 |
| Descriptor protocol itself | 02 (written) |

## Where this already shows up in these notes

`09-Pydantic/06` and `/07` — `@field_validator`, `@model_validator`, `@computed_field`, `@property`, stacked in a specific order. `00-Fast-API` — every route is `@router.get(...)`. `08-Async` — `@asynccontextmanager` for lifespan. All used correctly, none explained.

## Interview hooks

"Write a decorator that retries a function three times with backoff" is a standard screen question, and it exercises closures, `*args/**kwargs`, `wraps`, and decorator-with-arguments in one go. Sarvam's Week 9 names circuit breakers and rate limiting — both idiomatically decorators.

## Sources to verify against

- [`functools`](https://docs.python.org/3/library/functools.html) — `wraps`, `lru_cache`, `cache`, `partial`, `singledispatch`
- [PEP 318 — Decorators for Functions and Methods](https://peps.python.org/pep-0318/)
- [PEP 612 — `ParamSpec`](https://peps.python.org/pep-0612/) for concept 14
