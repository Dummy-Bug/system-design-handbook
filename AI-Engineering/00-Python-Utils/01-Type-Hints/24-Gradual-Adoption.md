#python #type-hints #typing #strict-mode #migration #python-utils


The last rung, and the only one that is about a **process** rather than a feature. It owns an interview question — **how would you introduce typing to a large untyped service?** — where the tempting answer is wrong.

## Default mypy accepts unannotated code

```python
1  def build_prompt(system, user):
2      return f"[system] {system}\n[user] {user}"
3
4
5  print(build_prompt("be brief", "why is the sky blue"))
```

```
$ mypy gd0.py
Success: no issues found in 1 source file
```

```
$ mypy --strict gd0.py
gd0.py:1: error: Function is missing a type annotation  [no-untyped-def]
gd0.py:5: error: Call to untyped function "build_prompt" in typed context  [no-untyped-call]
Found 2 errors in 1 file (checked 1 source file)
```

Default mypy is **content with completely unannotated code**, and that is deliberate — it is what makes hints addable to a codebase that already exists. No annotations, nothing to check, no complaints.

`--strict` reverses the stance: **an unannotated function is itself the error.**

### The ratio is the problem

Note that **one** unannotated function produced **two** errors — line 1 for defining it and line 5 for calling it. Line 5 is innocent; it is a perfectly good call site punished for what line 1 failed to say.

Scale that. A service with 400 unannotated functions, each called from three places:

- 400 × `[no-untyped-def]`
- 1200 × `[no-untyped-call]`
- **≈ 1600 errors on day one**

And the number is the problem, not the work behind it, because a 1600-error report is **not actionable**:

- Nobody reviews 1600 lines to find the two that matter.
- It cannot land in one pull request without touching every file in the repo.
- CI is red from day one, so the team learns to ignore the type checker — which is worse than never having turned it on.

> [!warning] **Turn on strict mode** is the wrong answer to the interview question, and it is the answer most people give.

## Dial one: scope by module

The mechanism is already familiar from `22-Third-Party-Libraries` — a rule scoped to a module pattern rather than a switch thrown over the whole project.

A boundary drawn by **date** is the natural instinct and does not work: mypy sees files, not history, and has no idea when a line was written. The boundary has to be expressed in something it can see, which means **module paths**.

**`legacy/hrms.py`** — old code, unannotated:

```python
1  def fetch_employee(employee_id):
2      return {"id": employee_id, "name": "alice"}
3
4
5  def fetch_manager(employee_id):
6      return {"id": 99, "name": "bob"}
```

**`core/agent.py`** — new code, fully annotated:

```python
1  from legacy.hrms import fetch_employee
2
3
4  async def describe(employee_id: int) -> str:
5      record = fetch_employee(employee_id)
6      return f"employee {record['id']}"
```

**`pyproject.toml`:**

```toml
1  [tool.mypy]
2  strict = true
```

```
$ mypy core legacy
legacy/hrms.py:1: error: Function is missing a type annotation  [no-untyped-def]
legacy/hrms.py:5: error: Function is missing a type annotation  [no-untyped-def]
core/agent.py:5: error: Call to untyped function "fetch_employee" in typed context  [no-untyped-call]
Found 3 errors in 2 files (checked 4 source files)
```

Two errors sit in `legacy/`, which nobody intends to touch today. The third is in `core/agent.py` — **perfectly annotated code**, red only because it calls into `legacy`. At scale that third kind is the one that does the damage: your good new code turns red because of code you did not write.

Now the exemption, scoped by path:

```toml
1  [tool.mypy]
2  strict = true
3
4  [[tool.mypy.overrides]]
5  module = "legacy.*"
6  disallow_untyped_defs = false
7  disallow_untyped_calls = false
```

```
$ mypy core legacy
core/agent.py:5: error: Call to untyped function "fetch_employee" in typed context  [no-untyped-call]
Found 1 error in 1 file (checked 4 source files)
```

Three errors down to one. Both `legacy/hrms.py` errors are gone; `core` stays fully strict.

### The rule the surviving error teaches

`disallow_untyped_calls` was switched off for `legacy.*`, and an untyped-call error is still reported. Where is it? `core/agent.py:5`.

> [!important] **A per-module setting applies to the module where the error is reported, not to the module being referenced.**
>
> Exempting `legacy.*` silences errors **inside** `legacy`. It does nothing for a call site living in `core`.

Which turns out to be the useful half. That surviving error marks **exactly where typed code touches untyped code** — a migration work queue, generated automatically. Annotate one function:

```python
1  def fetch_employee(employee_id: int) -> dict[str, object]:
2      return {"id": employee_id, "name": "alice"}
3
4
5  def fetch_manager(employee_id):
6      return {"id": 99, "name": "bob"}
```

```
$ mypy core legacy
Success: no issues found in 4 source files
```

**Green** — with `fetch_manager` on line 5 still completely unannotated, covered by the exemption and called by nothing typed.

That is the whole loop, and it has the property that makes it survivable:

- **CI is green from day one.** Strict was turned on across the entire repo and the build passed.
- **New code is strictly checked** — `core/` never had an exemption.
- **You annotate one function when you have a reason to**: you touched it, or new typed code needs to call it.
- **The only errors you see are at the boundary**, which is precisely the set worth acting on.

Same end state as the 1600-error version. Only one of them gets finished.

## Dial two: scope by check

`--strict` is not a mode. mypy says so itself:

```
$ mypy --help
  --strict    Strict mode; enables the following flags:
              --disallow-any-generics, --disallow-subclassing-any,
              --disallow-untyped-calls, --disallow-untyped-defs,
              --disallow-incomplete-defs, --check-untyped-defs,
              --disallow-untyped-decorators, --warn-redundant-casts,
              --warn-unused-ignores, --warn-return-any,
              --no-implicit-reexport, --strict-equality, --extra-checks
```

**Thirteen separate flags under one name.** And `gd0.py`'s two errors came from two specific ones, run individually:

```
$ mypy --disallow-untyped-defs gd0.py
gd0.py:1: error: Function is missing a type annotation  [no-untyped-def]

$ mypy --disallow-untyped-calls gd0.py
gd0.py:5: error: Call to untyped function "build_prompt" in typed context  [no-untyped-call]

$ mypy --warn-return-any gd0.py
Success: no issues found in 1 source file
```

Each produced exactly one of the two; a third produced none.

So instead of thirteen checks at once, turn one on repo-wide, fix that class of problem, and keep it:

```toml
[tool.mypy]
warn_return_any = true
warn_unused_ignores = true
# disallow_untyped_defs = true   ← next quarter
```

| dial | axis | what it looks like |
|---|---|---|
| per-module overrides | **which code** | strict everywhere, `legacy.*` exempt — a list that only shrinks |
| individual flags | **which checks** | one flag on repo-wide, then the next |

Real migrations use both.

## What this concept claims

**Type hints are designed to be added incrementally, and a migration's job is to keep the error list small enough to act on — which means scoping by module and by check, never flipping one switch.**

Five things to carry:

1. Default mypy accepts fully unannotated code **by design**; that is what makes adoption possible at all. `--strict` inverts the stance so that an unannotated function is itself an error.
2. One untyped function yields one error for its definition plus one per call site, so a service with 400 of them prints roughly **1600 errors on day one**. The obstacle is not the work — it is that the report is unreviewable and CI goes red, which teaches the team to ignore the checker permanently.
3. **Dial one is per-module overrides**, scoping by **which code**: strict by default, plus an explicit exemption list that only ever shrinks. A date-based boundary cannot work, because mypy sees files rather than history.
4. A per-module setting applies where the error is **reported**, not to the module being referenced — so exempting `legacy.*` leaves a call site in `core` still red. That is a feature: the surviving errors are exactly the typed/untyped boundary, which is the work queue.
5. **Dial two is the individual flags.** `--strict` is thirteen of them wearing one name, so a check can be enabled repo-wide on its own, fixed, and kept. The answer to **how would you introduce typing to a large untyped service?** is **strict by default with a shrinking exemption list** — not **turn on strict mode**.
