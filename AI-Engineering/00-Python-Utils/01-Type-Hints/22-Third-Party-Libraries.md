#python #type-hints #typing #stubs #py-typed #python-utils


Everything so far has been about annotating code you wrote. A real project is mostly code you didn't — and importing one library with no type information stops mypy at the front door:

```
app.py:1: error: Cannot find implementation or library stub for module named "hrms_sdk"  [import-not-found]
```

There is a crude way to silence that: `# type: ignore` on the import line. It works by making the entire module `Any`, so everything reached through it goes unchecked — a fallback rather than an answer, and `23-Escape-Hatches` takes it apart properly.

This note is the answer. Where library types actually come from, and how to get real ones.

## mypy reads the library's source

Two files. `mylib.py` plays the part of the library:

```python
1  async def fetch(url: str) -> int:
2      return 200
```

`app.py` uses it:

```python
 1  import asyncio
 2
 3  from mylib import fetch
 4
 5
 6  async def main() -> None:
 7      status = await fetch("http://x")
 8      reveal_type(status)
 9
10
11  asyncio.run(main())
```

```
$ mypy app.py
app.py:8: note: Revealed type is "int"
Success: no issues found in 1 source file
```

Line 8 says `int`, and the unremarkableness is the point: **mypy learned that by opening `mylib.py` and reading `-> int` off line 1.** To know anything about a library, it reads that library.

Which raises the obvious question — what happens when the library has nothing to read?

## A stub is a types-only file

Add a third file. Same module name, `.pyi` extension instead of `.py`:

```
app.py
mylib.py       ← the real code:  async def fetch(url: str) -> int:  return 200
mylib.pyi      ← the stub:       async def fetch(url: str) -> str: ...
```

The stub is one line, and two things about it matter. It says `-> str`, deliberately disagreeing with the real source. And its body is literally `...` — **no code at all**.

```
$ mypy app.py
app.py:8: note: Revealed type is "str"
```

```
$ python3 -c "from mylib import fetch; print(type(asyncio.run(fetch('http://x'))))"
<class 'int'>
```

mypy says `str`. Python returns an `int`.

> [!important] **A stub is a types-only file** — same module name, `.pyi` extension, signatures with no bodies. When one exists, the checker reads it **instead of** the real source.
>
> The `.py` is what runs. The `.pyi` is what gets type-checked. Nothing enforces that the two agree; they were made to disagree above purely to show which one wins.

This is what *"Library stubs not installed"* means in a mypy error. Translated: **nobody has given me a `.pyi` file for this library.**

## Why they exist: source you cannot edit

If a library already annotates its own code, why would anyone write a separate file of types for it?

Because the case that matters is the one where it doesn't. `mylib.py`, rewritten the way most older libraries look:

```python
1  async def fetch(url):
2      return 200
```

No annotations anywhere. **With `mylib.pyi` present:**

```python
1  async def fetch(url: str) -> int: ...
```

```
$ mypy app.py
app.py:8: note: Revealed type is "int"
```

**With `mylib.pyi` deleted:**

```
$ mypy app.py
app.py:8: note: Revealed type is "Any"
```

Same untouched `mylib.py` in both runs. The types came **entirely from the stub**.

That is the reason stubs exist, and it is a practical one rather than a technical one: you depend on a library, it has no annotations, and you cannot add them — it is not your code. A `.pyi` lets types be supplied **from outside the library, by someone who is not its author.**

`types-requests` is exactly that: a separate package on PyPI, maintained by different people from `requests`, containing nothing but `.pyi` files. It is why mypy's error suggests installing a *second* package rather than telling you to go fix the first one.

## Two ways a library ends up typed

| | who writes the types | where they live |
|---|---|---|
| **stub package** | outsiders | a separate package — `types-requests`, `types-redis` |
| **`py.typed`** | the library's own authors | inline, in the real `.py` files |

A modern library annotates its own source, so it needs no stub. It only needs to *announce* that its annotations are meant for you to rely on — and that announcement is an empty file called **`py.typed`**, one per package, at the package root. Zero bytes; its presence is the whole message.

## What mypy does with a library's body

Two questions fall out of that, and both are worth answering by experiment rather than assertion: does mypy read the whole function or only the signature, and is an empty file really the entire switch?

The test needs a **properly installed package**, not a local file — the two behave differently, which is itself the answer to the first question. `agentlib` is a real built-and-installed package whose one function is annotated *and* contains a deliberate error:

```python
1  async def fetch(url: str) -> int:
2      broken: int = "this is not an int"
3      return 200
```

```python
 1  import asyncio
 2
 3  from agentlib import fetch
 4
 5
 6  async def main() -> None:
 7      status = await fetch("http://x")
 8      reveal_type(status)
 9      print(status.totally_made_up)
10
11
12  asyncio.run(main())
```

The same `app.py` as before with `mylib` swapped for `agentlib` and one line added at 9.

**With `src/agentlib/py.typed` present:**

```
app.py:8: note: Revealed type is "int"
app.py:9: error: "int" has no attribute "totally_made_up"  [attr-defined]
Found 1 error in 1 file (checked 1 source file)
```

**With that same empty file deleted, nothing else touched:**

```
app.py:3: error: Skipping analyzing "agentlib": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app.py:8: note: Revealed type is "Any"
```

### Whose errors are your problem

Note what is *missing* from the first run: line 2 of `agentlib` is plainly wrong, and mypy never mentions it. Run the identical code as a local file in the project instead and it does:

```
mylib.py:2: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
```

| the library is | reads the body | reports errors found inside it |
|---|---|---|
| a local file in your project | yes | **yes** |
| an installed package | yes | **no** |

The split is deliberate. Your dependencies' internal mistakes are not your build's problem — surfacing them would bury you in thousands of errors in code you cannot fix. mypy takes their **signatures** and stays quiet about their **insides**.

### `py.typed` is permission, not types

The second run is the one to remember. Deleting **zero bytes** turned the same installed, fully-annotated package from `int` into `Any`. The annotations never moved; mypy simply stopped trusting them.

> [!important] `py.typed` does not contain types. It is **permission to use the types that were already there.**
>
> A library can be annotated from top to bottom and still be useless to you if its authors never shipped that marker — without it, annotations are treated as the authors' private notes rather than a public contract you may rely on.

## When the annotations exist but the marker doesn't

`agentlib` with `py.typed` deleted is a real and common situation: the library **is** annotated, you can open the file and read `-> int` with your own eyes, and mypy hands you `Any`.

The obvious wish — *read them anyway* — is a supported flag:

```
$ mypy app.py                            ← default
app.py:8: note: Revealed type is "Any"

$ mypy --follow-untyped-imports app.py

app.py:8: note: Revealed type is "int"
app.py:9: error: "int" has no attribute "totally_made_up"  [attr-defined]
```

`int`, and the bug caught, with no marker anywhere.

You almost never want it as a **command-line flag**, though, because it applies to every untyped dependency in the project at once — trusting annotations you have never read, written by authors who specifically declined to promise they are right. Name the library instead:

```toml
[[tool.mypy.overrides]]
module = "agentlib.*"
follow_untyped_imports = true
```

```
$ mypy app.py          ← no flag, config only
app.py:8: note: Revealed type is "int"
app.py:9: error: "int" has no attribute "totally_made_up"  [attr-defined]
```

One library, opted in deliberately, with a line in version control saying you decided it.

> [!info] That `[[tool.mypy.overrides]]` block is the shape of nearly all real mypy configuration — a rule scoped to a module pattern rather than a switch thrown over the whole project. `24-Gradual-Adoption` is built entirely on it: a strict core and an untyped edge, held apart by exactly this mechanism.

## Writing the stub yourself

The case that actually eats an afternoon is the one where nothing above applies: **no annotations, no marker, no stub package on PyPI.** Nothing to read and nothing to install.

`agentlib`, rewritten to look its worst:

```python
1  async def fetch(url):
2      return 200
3
4
5  async def close():
6      return None
```

```
$ mypy app.py
app.py:8: note: Revealed type is "Any"
```

Since a stub supplies types **from outside** a library, nothing stops the outsider being you. One file of your own, in a directory that mirrors the package layout:

```
stubs/agentlib/__init__.pyi
```

```python
1  async def fetch(url: str) -> int: ...
```

```toml
[tool.mypy]
mypy_path = "stubs"
```

```
$ mypy app.py
app.py:8: note: Revealed type is "int"
app.py:9: error: "int" has no attribute "totally_made_up"  [attr-defined]
```

`int`, and the bug caught, from a library containing no type information at all. `mypy_path` means only *"also look in here for `.pyi` files."*

### The trap: a stub is all-or-nothing

The library has two functions. The stub above declares one. Call the other:

```python
3  from agentlib import close, fetch
...
9      await close()
```

```
$ mypy app.py
app.py:3: error: Module "agentlib" has no attribute "close"  [attr-defined]
```

```
$ python run.py
fetch returned: 200
close() ran fine
```

**mypy says the function does not exist. Python calls it happily.** `close()` is right there in the real source; the stub simply never mentioned it.

This follows from the rule established at the top of the note — when a `.pyi` exists the checker reads it **instead of** the real source, not in addition to it.

> [!warning] **A stub is the complete truth about that module, as far as the checker is concerned. Anything you leave out does not exist.**
>
> That flips how writing one feels. It looks like *"annotate the bits I care about"*; it is really *"declare the module's entire public surface, or lose the parts you skipped."* Stub the one function you need from a large library and you have just deleted the other four hundred.

## The option to reach for first

Which is why there is a fifth answer, and in practice it beats a partial stub:

```python
# my_agentlib.py — my code, fully typed, in my project
from agentlib import close, fetch   # type: ignore[import-untyped]


async def get_status(url: str) -> int:
    return await fetch(url)


async def shutdown() -> None:
    await close()
```

One module of your own that imports the untyped library, absorbs the `Any` **in exactly one place**, and re-exports it behind signatures you wrote. Every other file imports *your* module and is fully checked.

No stub to keep in sync as the library changes, no risk of deleting four hundred functions you never declared, and the untyped surface of the whole project is one file you can point at in review.

## The options, worst to best

| | what you get | when |
|---|---|---|
| `# type: ignore` on the import | silence; everything `Any` | never, if avoidable |
| `ignore_missing_imports` in config | the same, but written down | the library is genuinely unannotated and you accept it |
| `follow_untyped_imports` per-module | the library's real annotations | it **is** annotated, just unmarked |
| your own `.pyi` via `mypy_path` | types you wrote | small surface, or no other option |
| **a thin typed wrapper module** | types you wrote, `Any` confined to one file | the usual right answer |
| install a stub package | curated types, maintained by others | one exists — `types-requests` and friends |

## What this concept claims

**Your annotations are only as good as your dependencies'. An untyped library makes everything reached through it `Any`, and every fix is a question of who wrote the types and how far you trust them.**

Five things to carry:

1. mypy learns a library's types by **reading that library**. There are two ways it is allowed to: a `.pyi` **stub** — a types-only file, signatures with `...` bodies, read *instead of* the source — or a **`py.typed`** marker granting permission to trust the source's own annotations. One route from outside the library, one from inside.
2. `py.typed` contains nothing. Deleting zero bytes turns a fully annotated, installed package from `int` into `Any`. It is not the types — it is **permission to use the types that were already there**.
3. mypy reads an installed dependency's whole body but **reports no errors inside it**; for a local project file it reports them. Your dependencies' internal mistakes are not your build's problem.
4. When a library is annotated but unmarked, `follow_untyped_imports` scoped to that module gets you the real types. Scoped per-module in config, never as a global flag — a global one trusts every untyped dependency you have.
5. A hand-written stub is the **complete truth** about its module: anything omitted ceases to exist for the checker, while still running fine at runtime. That asymmetry is why a thin typed wrapper of your own usually beats a partial stub — it confines the `Any` to one reviewable file without claiming to describe a library you have not read.
