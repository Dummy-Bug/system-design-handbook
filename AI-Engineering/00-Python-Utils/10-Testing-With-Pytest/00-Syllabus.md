#python #pytest #testing #evals #python-utils #syllabus

# 10 · Testing with pytest — Syllabus

18 concepts. **Generic** — the framework and the practice, not any one project's suite.

> The argument for this folder in one line: **an eval harness is a test harness.** Golden sets are parametrised cases. Judges are assertions with fuzzy comparators. CI gating on regressions is the same wiring either way. Sarvam's Week 7 asks for exactly this, and the AI-engineering plan puts evals as the single highest-signal block — but neither works without the underlying mechanics.

**Why this sits tenth:** it consumes almost everything above it. Fixtures are generators with teardown (04) or context managers (05). `@pytest.fixture` and `@parametrize` are decorators (03). Async tests need the event loop (08). Test data is validated with models (09). Testing failure paths needs `pytest.raises` and exception groups (06).

**Currency check (2026-08-04):** verify the pytest major version and, in particular, the current state of async testing — `pytest-asyncio` has changed its mode/configuration semantics more than once (`asyncio_mode`, strict vs auto), and `anyio` is the common alternative. Confirm before writing config.

---

## A · Mechanics

**1. Why pytest over `unittest`**
Plain `assert`, no boilerplate class hierarchy, better failure output. The stdlib comparison is worth one paragraph, not more.

**2. Discovery and layout**
`test_*.py`, `test_*` functions, `conftest.py`, and the `src/` vs flat layout question that decides whether your imports work.

**3. Assertions and introspection**
Why a bare `assert x == y` produces a useful diff — pytest rewrites assertions. Comparing floats, collections, and nested structures.

**4. `pytest.raises`**
Asserting that something fails, matching on message, inspecting the caught exception. With exception groups (06) as the harder case.

**5. Running selectively**
`-k`, `-m`, node IDs, `-x`, `--lf` (last failed), `-q`/`-v`. The everyday ergonomics that decide whether you actually run tests.

## B · Fixtures

**6. What a fixture is**
Dependency injection for tests — request it by naming it as a parameter. **Structurally the same idea as FastAPI's `Depends`**, which is already in the FastAPI notes.

**7. Setup and teardown via `yield`**
A fixture that yields is a generator (04) — everything before is setup, everything after is teardown, guaranteed. Same shape as `get_session`.

**8. Scopes**
`function` / `class` / `module` / `session`, and the trade: an expensive fixture reused across tests versus tests that leak state into each other.

**9. `conftest.py` and fixture resolution**
Where fixtures live, how they're found, and directory-scoped overriding.

**10. Built-in fixtures**
`tmp_path`, `monkeypatch`, `capsys`, `caplog`. `monkeypatch` in particular for env vars and attribute patching, scoped so it undoes itself.

**11. Factory and parametrised fixtures**
Fixtures that return a **maker** function; fixtures parametrised so every dependent test runs once per variant.

## C · Parametrisation — the eval-harness primitive

**12. `@pytest.mark.parametrize`**
One test function, many cases, each reported separately. **This is the mechanism a golden set is built on** — a list of (input, expected) pairs is a parametrised test, and a failing case names itself.

**13. Stacking and IDs**
Multiple `parametrize` decorators producing a cross-product; `ids=` so failures read as names rather than `case_17`.

**14. Loading cases from files**
Keeping cases in JSON/YAML/CSV rather than inline, so a non-engineer can extend the set — the practical shape of a real eval suite.

## D · Isolation and the outside world

**15. Mocking and patching**
`unittest.mock`, `monkeypatch`, `MagicMock`, `AsyncMock`. Patching **where it's looked up**, not where it's defined — the single most common mistake.

**16. Testing code that calls an LLM**
The genuinely hard case, and where testing and evals diverge: deterministic tests mock the model; evals actually call it and score the output. Recorded fixtures/cassettes as the middle ground. Knowing which of the three a given check should be is the judgement being tested.

**17. Async tests**
`pytest-asyncio` or `anyio`, event-loop fixtures and scope, and testing async generators (04) and streaming endpoints.

## E · Practice

**18. Coverage, CI, and what a suite is for**
`pytest-cov`, why coverage percentage is a weak proxy for confidence, running tests in CI, and the distinction that matters at the end: a **test** asserts deterministic behaviour and must pass; an **eval** scores non-deterministic quality and moves a number. Wiring both into CI is Sarvam's Week 7 deliverable.

---

## Deferred

| Topic | Goes to |
|---|---|
| LLM-as-judge, trajectory scoring, golden-set design | outside this vault (`01-Agent-Evals`, `03-LLM-Judge-And-Error-Analysis`) |
| Fixtures/generators/context managers as language features | 04, 05 (written) |
| `ValidationError` assertions | 09 (written) |
| Load and latency benchmarking | 07 / outside this vault |

## Where this already shows up

Nowhere yet — and that's the finding. `00-Fast-API` has no tests; the Xarvis audit records **11 test files, sparse coverage, no integration tests.** This folder is the prerequisite for closing the single largest gap identified in both the AI-engineering plan and the Sarvam assessment.

## Interview hooks

**How do you test an agent?** is the whole game here, and the strong answer separates the deterministic layer (tool wiring, schema compliance, error paths — real unit tests with mocks) from the non-deterministic layer (answer quality, trajectory correctness — evals with a judge). Sarvam's §4 names **automated evaluation harnesses** and Week 7 names CI regression-catching directly; capstone requirements say **real test coverage.**

## Sources to verify against

- [pytest documentation](https://docs.pytest.org/) — fixtures, parametrize, and monkeypatch pages in particular
- [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) — including `AsyncMock`
- `pytest-asyncio` / `anyio` docs — **check the current config semantics**, this is the part that goes stale
