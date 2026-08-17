#python #execution-model #bytecode #imports #python-utils #syllabus

# 00 · How Python Runs Code — Syllabus

12 concepts. **Deliberately small.** This folder exists to stop the same question resurfacing in every other folder, not to become a study of the interpreter.

> Created 2026-08-06, by splitting material out of `01-Type-Hints/02`. That note needed the compile-versus-execute distinction to explain how an editor can help you before anything runs — and the explanation grew until it was the longest section in a note about something else. It belongs here.

**Why this sits at 00.** Every other folder assumes it. Type hints need **when does the annotation get evaluated.** Decorators need **`@` is a function call that runs at import.** Async needs **what does the event loop actually execute.** Testing needs **why did my module-level code run twice.** Each of those is the same handful of facts asked from a different direction.

**Scope discipline — read this before adding to the list.** The bar for a concept here is: **does not knowing it cause a wrong answer somewhere else in the vault?** Reference counting, the GC generations, CPython's evaluation loop, and the peephole optimiser are all genuinely interesting and all fail that bar. This folder is a foundation, not a destination. If it grows past ~12 concepts, something has gone wrong.

**Currency check (2026-08-06):** verified on Python 3.13.3 (CPython). `.pyc` naming (`cpython-313`) and the `__pycache__` layout are stable and long-standing. Worth re-verifying if it ever matters: the exact `.pyc` invalidation header (timestamp-based by default, with a hash-based mode available), and whether 3.14 changes module-level evaluation timing — PEP 649 changes **annotation** evaluation specifically, which is concept 3's neighbourhood.

---

## A · From text to a running program

**1. The two phases — compile, then execute**
Python reads your whole file and turns it into **bytecode** first; only then does it start carrying those instructions out. Two phases, not one. Everything else in this section is a consequence.

**2. Four words for two things**
**Compile**, **execute**, **interpret**, **run** get used interchangeably and shouldn't be. **Interpret** is another word for **execute**; **run** is the colloquial umbrella covering both phases. Settling this once removes a surprising amount of confusion — including the argument about whether Python is a compiled or an interpreted language, which has the boring answer **both**.

**3. What each phase can catch**
Compilation asks only **is this well-formed Python?** — so a syntax error stops everything before line 1 executes, while an undefined name sails through and fails later, at the moment execution reaches it. This is the difference between a total, immediate failure and a local, late one, and it's why a mistake on a rarely-taken branch can survive for months.

**4. `__pycache__` and the `.pyc`**
Where compiled bytecode gets cached, why the filename carries the interpreter version, how the cache knows it's stale, and the detail that catches people: **the file you run is never cached — only the files you import.**

## B · Modules and imports

**5. What `import` actually does**
Find the file, compile it if needed, then **execute it top to bottom**. An import is not a declaration or a link — it runs code, which is why a module with a `print` at the top prints when imported.

**6. Modules execute once per process**
The second `import` of the same module does not re-run it. `sys.modules` is the cache that makes that true, and it's the mechanism behind both the singleton-ish behaviour of module-level state and the confusion when someone expects a reload.

**7. `if __name__ == "__main__"`**
Why the same file behaves differently when run directly versus imported, and what `__name__` actually holds in each case. The idiom everyone copies before they know what it does.

**8. Circular imports**
What actually fails, and why it's about **execution order** rather than a forbidden shape — module A is half-executed when it asks for module B, which asks for A and gets the half-built version. The standard escapes.

## C · Names, objects, and statements that run

**9. Names are bindings, not boxes**
`x = [1, 2]` does not put a list **in** `x`; it points the name `x` at a list object. Two names can point at one object. This is the single fact underneath aliasing bugs, mutable-default arguments, and every **why did my other variable change** question.

**10. Scope and the LEGB lookup**
Local, enclosing, global, built-in — the order Python searches when it meets a name. Plus `global` and `nonlocal`, and why assigning to a name inside a function makes it local for the **whole** function.

**11. `def` and `class` are executable statements**
Neither is a declaration read ahead by the compiler. Both run when execution reaches them, building an object and binding a name — which is why a decorator runs at import, why a `def` inside a function creates nothing until the outer function is called, and why a class body executes exactly once.

## D · When it goes wrong

**12. The call stack and reading a traceback**
What the frames are, why the most useful line is usually the bottom one, and how to read a traceback that crosses several files without skipping to the last line and guessing.

---

## Coverage

| # | Concept | Note |
|---|---|---|
| 1–4 | The two phases, vocabulary, what each catches, `__pycache__` | `01-Compile-Then-Execute` |
| 5–12 | imports through tracebacks | — |

**4 of 12 written.** Concepts 1–4 were derived live and moved here from `01-Type-Hints/02`; everything in that note was executed rather than recalled.

## Deferred

| Topic | Goes to |
|---|---|
| When **annotations** specifically get evaluated, PEP 649 | `01-Type-Hints` (concepts 4 and 21) |
| Decorator mechanics — what `@` does to the function object | `03-Decorators` (written) |
| The GIL, threads, processes | `07-Concurrency-Models-And-The-GIL` |
| The event loop as a thing that executes coroutines | `08-Async` (written) |
| Reference counting, garbage collection, the CPython eval loop | **not scheduled** — fails the scope bar above |

## Where this already shows up

`01-Type-Hints/01` — `def` executing is what builds `__annotations__`, and a nested `def` builds nothing until the outer call. `01-Type-Hints/02` — an editor can read a file that cannot run, because reading and executing are unrelated. `03-Decorators` — every decorator in that folder runs at import, which is concept 11. `08-Async` — `async def` is still just a `def` that executes and binds a name.

## Interview hooks

**Is Python interpreted or compiled?** is a screening question with a bad reputation, because the expected answer is usually wrong. The one that actually separates people is the follow-up: **so what's in `__pycache__`, and when does it get written?** Also common, and concept 9: **you passed a list to a function, the function modified it, and the caller's list changed — why?**

## Sources to verify against

- [The import system](https://docs.python.org/3/reference/import.html) — for section B
- [Execution model](https://docs.python.org/3/reference/executionmodel.html) — for concepts 9 and 10
- [PEP 3147 — `__pycache__`](https://peps.python.org/pep-3147/), for concept 4
