#python #type-hints #typing #mypy #stubs #python-utils


Your annotations only reach as far as your own code. The moment a value comes back from a library, the checker needs that library to be annotated too — and many aren't.

## What an untyped dependency does

```python
import requests

r = requests.get('https://example.com', timeout=5)
status = r.status_code
status = 'ok'
```

The last line is a real mistake: a status code is a number, and this reassigns it to a string. Running the checker:

```
error: Library stubs not installed for "requests"  [import-untyped]
note: Hint: "python3 -m pip install types-requests"
note: (or run "mypy --install-types" to install all missing stub packages)
```

One complaint, and it isn't about the bug. Because `requests` carries no type information, everything coming out of it is unknown — `r` is unknown, so `r.status_code` is unknown, so reassigning it to a string contradicts nothing.

This is the spreading problem. An untyped library doesn't just fail to help; **it produces values that switch checking off wherever they travel.** Annotate your own code carefully, then feed it a value from an untyped dependency, and the guarantees quietly stop at that boundary.

## Stub packages

A stub package supplies the missing annotations from outside — signatures only, no implementation. They're distributed separately and named predictably: `types-` followed by the package name.

```
types-requests
types-redis
types-PyYAML
```

With that installed, the same file:

```
error: Incompatible types in assignment
(expression has type "str", variable has type "int")  [assignment]
```

The complaint about missing stubs is gone, and the actual bug is found. Nothing about your code changed — the checker simply learned that `status_code` is an `int` and could then see that assigning `'ok'` to it is wrong.

> [!info] Stubs are a checking-time dependency only. They contain no runtime code, are never imported by your program, and belong in a dev-dependency group rather than alongside the packages your application actually needs to run.

## Libraries that ship their own

Many modern libraries annotate their own source, so no separate package is needed. The way a library declares this is an empty marker file named `py.typed` in its package directory.

That file is the whole mechanism, and it's opt-in for a reason: annotating a library is a promise about its interface. Until the maintainers place that marker, checkers ignore any hints in the source, on the assumption they were never intended as guarantees.

So a dependency falls into one of three states:

| | What to do |
|---|---|
| ships `py.typed` | nothing — it already works |
| has a `types-` package | install it as a dev dependency |
| neither | decide, per below |

## When there's nothing available

For the third case the honest options are narrow, and they trade off against each other:

- **Wrap it.** Put the untyped library behind a small module of your own with annotated functions. One place where the unknown values enter and become known, rather than everywhere the library is called. The most work, and the only one that actually confines the damage.
- **Silence the import.** `# type: ignore[import-untyped]` on the import line, or the equivalent per-module setting in your checker's config. Honest and local: you're stating that this dependency is unchecked.
- **Write partial stubs.** A `.pyi` file covering just the handful of functions you call. Reasonable when the surface you touch is small and the library is stable; a maintenance burden otherwise.

> [!warning] The one to avoid is switching off the missing-import error globally and forgetting. It removes the reminder without removing the blindness — and the blindness is not confined to that library. Every value it returns carries the hole into your code.
