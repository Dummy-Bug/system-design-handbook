#testing #pytest #fastapi #async #langgraph #agents #syllabus

# 09 · Testing Python Services — Syllabus

**19 notes, 223 rungs.** Generic — pytest, async, FastAPI and agent code, not Xarvis's implementation, which is mapped at the bottom.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — a mock returns None, therefore the assertion passes on nothing, therefore the test proves nothing, therefore a green suite is not evidence. Rungs are not topics and not section headings. Eight to fifteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about pytest teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

**Three modes, trained differently.** Notes 1 to 12 are mechanism — what the tools do and how they lie — and respond to retrieval practice, so the rungs are the recall unit. Notes 13, 14, 16 and 17 are design judgement, worked as a position defended against changed constraints rather than recalled. Notes 18 and 19 are craft: done, not recited.

**The Java folder is the sibling, not the source.** `Backend Engineering/18-Testing` covers the same ideas in Spring — isolation, arrange-act-assert, slices, H2 versus Testcontainers. **The concepts transfer and none of the tooling does**, and two things are genuinely different rather than renamed: async changes what a fixture is, and a model that answers differently on identical input has no equivalent in a Spring service. Read the Java notes for the shape; do not expect a translation table.

**Currency check (2026-09-07):** FastAPI's own async-test documentation uses **`@pytest.mark.anyio` with `httpx.AsyncClient` and `ASGITransport`**, not `TestClient`. `pytest-asyncio`'s auto mode **conflicts** with the anyio plugin in the same session, so the choice is not free. **LocalStack archived its public repository on 23 March 2026**, which moved AWS-mocking practice to `moto` in-process and Testcontainers or Floci for a real endpoint. `pytest-freezegun` is deprecated in favour of `pytest-freezer`. Re-verify before relying on: whether `TestClient` is still discouraged for async apps, `respx`'s httpx floor, and whether `moto` still covers DynamoDB TTL.

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**Where a rung says break, it is run, not read.** Watching a test pass against a deliberately broken implementation produces a problem the fix attaches to. Reading that tests can be vacuous produces a fact that decays.

**Recall is per note, from memory, file closed.** Recognising an answer does not count.

**Two rabbit holes are marked and binding** — event-loop internals in note 6, and coverage tooling in note 17. Both are deep, satisfying, and pay back nothing here.

**Spacing:** re-test notes 1 to 7 after finishing note 11, and all of 1 to 12 once the first suite is green. Same-day re-testing is close to wasted, because retrieval works when forgetting has started.

**Where it gets built.** Every note is worked in `lab` first, where nothing is at stake, and only then applied to Xarvis. The order is not caution — it is that a test written against code you already trust teaches the tool, and a test written against code you do not teaches nothing until you can tell which one failed.

---

## Note 1 · What Tests Are For

Written up as [[01-Why-Test]].

11 rungs. No break — this is framing.

1. Code that works today is not the thing under threat; the thing under threat is code that still works after the next change.
2. A person can verify a change by hand once, and cannot verify every previous change by hand on every commit.
3. So the value of a test is not that it passes now — it is that it **fails later**, on a change whose consequences the author did not see.
4. Which means a test's real audience is a future person who does not know what you know today, including you.
5. That reframes what a good test is: not one that documents correct behaviour, but one that **notices** when behaviour changes.
6. A test nobody runs notices nothing, so speed is a correctness property rather than a nicety.
7. And a test that fails for reasons unrelated to the code is worse than absent — people learn to ignore it, and then ignore it on the day it is right.
8. **A suite has exactly two failure modes and they are opposite**: it fails when nothing is wrong, or it passes when something is.
9. Almost every technique in this folder is aimed at one or the other, and several trade one for the other.
10. The second failure mode is the dangerous one, because a suite exhibiting it looks identical to a healthy one.
11. So the discipline that matters most is not writing tests — it is **proving a test can fail**, which is a separate act from writing it.

> **Recall:** Why is a test's audience a future person rather than the current author? · Name the two failure modes of a suite and say which is worse, and why. · Why is speed a correctness property here rather than a convenience?
>
> **Stop:** Do not read about testing philosophy. The distinctions worth having are all in the failure modes above, and the rest is taste presented as principle.

---

## Note 2 · Your First Python Test

Written up as [[02-First-Test]].

12 rungs. **Break:** take a passing test, change the expected value, run it, and read every line pytest prints.

1. Nothing in a Python test file marks it as a test — no annotation, no base class, no import of the framework. This is the first real departure from JUnit and it changes how a file is organised.
2. pytest finds tests by **name**: a file whose name starts with `test_`, holding a function whose name starts with `test_`, discovered by walking directories from where the command was run.
3. So the smallest complete test is a four-line file with no scaffolding of any kind around it.
4. Tests live in a `tests/` directory beside `src/`, outside the package, because they are not part of what ships.
5. Which creates the first thing that goes wrong for everybody: the test has to import your package, and a `src/` layout makes that fail until the project is installed. **The error names a missing module, not a test**, so it reads as unrelated to what you were doing.
6. `uv run pytest` from the project root installs and runs in one step, which is why that problem mostly disappears with uv and bites hard without it.
7. The assertion is the bare `assert` statement. No `assertEquals`, no matcher library, no import.
8. pytest **rewrites** that statement before running it, so a failure prints both sides of the comparison rather than just saying false.
9. Which is why the helper methods do not exist and are not missed — and why a helper that hides the assert inside another function loses the diff, since the rewriting only reaches asserts pytest can see.
10. The report is one character per test: a dot passed, `F` failed, `E` errored. The count on the last line is the whole summary.
11. Reading a failure means reading the **rewritten assertion line first** and the traceback second, because the rewritten line usually contains the answer.
12. `-q` shrinks the report, `-x` stops at the first failure, `-k` selects tests by name substring. Three flags cover the first month.

> **Recall:** What marks a function as a test in pytest? · Why does `assertEquals` not exist? · What is the first error a fresh project gives you, and why does it not mention tests?
>
> **Stop:** Do not configure anything yet. No `conftest.py`, no `pyproject.toml` section, no plugins. One file, one function, one command.

---

## Note 3 · The Vacuous Test

Written up as [[03-Vacuous-Tests]].

12 rungs. **Break:** write a test, delete the body of the function it tests, and watch it still pass.

1. A test asserts something about a result, so the result has to come from the code under test for the assertion to mean anything.
2. A mock stands in for a dependency, and by default it returns a stand-in for everything asked of it.
3. So a mock placed one layer too high replaces the thing being tested, and the assertion then compares the mock's output to itself.
4. That test passes forever, including when the real implementation is deleted.
5. It is indistinguishable from a working test in the report, because both are green.
6. The most common accidental form is patching the module under test rather than its collaborator — one import path apart.
7. The second most common is asserting on the mock: `mock.method.return_value` compared to itself, with the subject never invoked.
8. A third is an assertion that cannot fail — comparing a value to itself, or asserting a truthy object rather than a specific value.
9. A fourth is a test whose assertions are all inside a conditional that is never entered.
10. **The single check that catches all four is mutation by hand**: break the implementation, rerun, and require red.
11. That takes ten seconds and is the only direct evidence that the assertion is connected to the code.
12. It is also the reason generated tests need reviewing more carefully than written ones — a tool given a subject and a mocking library produces vacuous tests fluently, and they read exactly like real ones.

> **Recall:** What makes a vacuous test invisible in a report? · Name three shapes a vacuous test takes. · What is the one check that catches all of them, and why is it not automatable in general?
>
> **Stop:** Do not go looking for mutation-testing frameworks yet. The manual version is the habit; the tooling is a later optimisation and a rabbit hole.

---

## Note 4 · pytest's Model

Written up as [[04-Pytest-Model]].

11 rungs. **Break:** put two tests in one file that pass alone and fail together.

1. pytest **collects before it runs** — it imports every matching file first, then executes. So an import error in one file can stop tests in a different file from running at all.
2. **Failed means the test ran; errored means it never got the chance** — an exception inside the test body is a failure whatever its type, while a fixture raising during setup or teardown, or a file failing to import, is an error. Read the errors first, because an errored test produced no information at all.
3. Every test in a run shares **one process**, so anything global — a module-level cache, a registry, a `contextvar` — survives from one test into the next.
4. Which produces the classic pair: two tests that pass alone and fail together.
5. Collection order is alphabetical by file and top-to-bottom within a file, and it is stable enough that an order dependence can sit undetected for months before a rename exposes it.
6. **Isolation is therefore something you arrange, not something pytest provides.**
7. `-p no:randomly` and its inverse exist because order dependence is common enough that deliberate shuffling is the standard way to expose it.
8. `--lf` reruns only what failed last time and `--ff` reruns everything with the failures first — and stacked with `-x`, **`--ff -x` is the better default**, since the two are identical while broken and only `--ff` confirms the whole suite the moment the fix lands.
9. Configuration lives in `pyproject.toml` under `[tool.pytest.ini_options]`, and a project without it relies on defaults that differ across versions.
10. `testpaths` and `addopts` are the two settings worth having on day one — where to look, and what flags to apply every time.
11. A `conftest.py` is found automatically and never imported by name, which is the mechanism the next note is built on.

> **Recall:** What is the difference between a failure and an error, and why does it matter when reading a report? · What makes two tests order-dependent, and what is the cheapest way to expose it? · Why can an import error in one file break a test in another?

> **Stop:** Do not learn the plugin ecosystem. Two config keys and a handful of flags cover the first month.

---

## Note 5 · Fixtures, And Where State Leaks

Written up as [[05-Fixtures]].

14 rungs. **Break:** give a fixture returning a mutable list `scope="session"` and mutate it in one test.

1. Arrange-act-assert repeated across a file duplicates the arrange step, which then drifts between tests.
2. A **fixture** is a function whose return value is injected into any test that names it as a parameter.
3. Naming it as a parameter is the entire wiring — there is no decorator on the test.
4. A fixture that `yield`s instead of returning gets a teardown: everything after the yield runs when the test ends.
5. `conftest.py` makes fixtures available to every test in its directory and below, with no import.
6. **Importing from conftest is an anti-pattern** — it creates a second copy of each fixture and resolution errors that read as impossible.
7. Scope decides how often the fixture runs: `function` by default, then `class`, `module`, `package`, `session`.
8. Widening scope makes the suite faster and is the single most common source of leaked state.
9. A session-scoped fixture returning a **mutable** object shares that object across every test, so one mutation changes another test's arrange step.
10. The rule that follows: widen scope only for things that are **expensive and immutable**, or expensive and explicitly reset between uses.
11. `autouse=True` applies a fixture without it being named, which is powerful and hides the dependency from the reader.
12. So autouse is right for environment isolation and wrong for anything a test's outcome depends on.
13. Parametrising a fixture runs every dependent test once per value, which multiplies rather than adds.
14. **A fixture is a dependency injection container**, and the same reasoning about lifetimes applies — including that a long-lived object handed to short-lived consumers is where the bugs are.

> **Recall:** What does naming a fixture as a parameter do, and what is the alternative wiring? · Why is a session-scoped mutable fixture dangerous when a session-scoped immutable one is not? · When is autouse correct?
>
> **Stop:** Do not build a fixture hierarchy before you have tests to serve. Fixtures extracted from three real duplications are right; fixtures designed up front are guesses.

---

## Note 6 · Async Changes The Rules

12 rungs. **Break:** call an async function in a sync test and assert on what comes back.

1. An `async def` function called without awaiting returns a **coroutine object** and runs nothing.
2. So a sync test calling async code asserts on a coroutine, which is truthy, and the assertion passes while nothing executed.
3. That is the vacuous test from note 2 arriving through a different door, and it does not look like mocking.
4. Running a coroutine needs an event loop, and a test framework has to supply one.
5. Two plugins do it: **`pytest-asyncio`** and the **anyio** pytest plugin.
6. FastAPI's own documentation uses **`@pytest.mark.anyio`**, because Starlette is built on anyio rather than raw asyncio.
7. And `pytest-asyncio`'s **auto mode conflicts with the anyio plugin** in the same session, so this is a choice rather than an accumulation.
8. It also cannot drive anyio-native primitives — `TaskGroup`, `CancelScope` — which is decisive for any code using them.
9. An async fixture needs the same treatment, and a fixture that forgets it hands the test a coroutine rather than a value.
10. Event-loop scope is a second, independent lifetime from fixture scope, and mismatching them produces `attached to a different loop`.
11. That error names the loop and never names the fixture that caused it, which is why it is hard.
12. **The safe default is one loop per test**, widened only when a fixture genuinely cannot be rebuilt.

> **Recall:** What does calling an async function without awaiting return, and why does that produce a passing test? · Why does FastAPI's documentation use anyio rather than asyncio? · Name the one incompatibility that decides the plugin choice.
>
> **Stop marker — binding:** Do not read the event-loop implementation. The observable rules above are the whole working set, and the internals are a day gone.

---

## Note 7 · Test Doubles, Named Precisely

13 rungs. **Break:** stub a method that is never called and watch the test pass anyway.

1. Test double is the family; mock, stub, fake and spy are members with different jobs.
2. A **stub** supplies a canned answer so the code under test can proceed — it is about input.
3. A **mock** records how it was called so the test can assert on the interaction — it is about output.
4. A **fake** is a working implementation with a shortcut, like an in-memory store, and it has behaviour.
5. A **spy** wraps the real thing and observes it, so the real behaviour still happens.
6. Python's `unittest.mock` calls all of them `Mock`, which is why the distinction has to be held in the head rather than the type.
7. `MagicMock` returns a new `MagicMock` for every attribute and call, so **any chained access succeeds**, and a typo in a method name silently passes.
8. `create_autospec` and `spec=` bind the double to the real signature, so a typo raises instead.
9. `patch` replaces an attribute on a module for the duration of a test, and it must target **where the name is used, not where it is defined**.
10. Which is the single most common patching error, and it fails by patching something nothing looks at, so the real code runs.
11. Asserting a stub was called is the difference between a test of behaviour and a test that a line exists.
12. Over-asserting on calls produces tests that break on every refactor while catching no bugs — the other failure mode from note 1.
13. **The rule that survives: mock at the boundary you own, and assert on the outcome rather than the choreography** unless the choreography is the requirement.

> **Recall:** Distinguish a stub from a mock in one sentence each. · Why does `MagicMock` hide typos, and what fixes it? · Where must `patch` point, and what is the symptom when it points at the wrong place?
>
> **Stop:** Do not adopt a mocking style guide. The four distinctions above plus autospec is more than most codebases apply consistently.

---

## Note 8 · Testing A FastAPI Endpoint

14 rungs. **Break:** override a dependency in one test and watch a later test still see the override.

1. Calling an endpoint function directly skips routing, validation, serialisation and error handling — which is most of what the framework contributes.
2. So an endpoint test needs a client that speaks HTTP without a socket.
3. `TestClient` does that synchronously by running the app in a background loop, and is the older path.
4. **`httpx.AsyncClient` with `ASGITransport(app=app)`** calls the ASGI app in-process, and is what FastAPI's async documentation now uses.
5. In-process means no port to manage, no race on startup, and tracebacks that point into your code rather than a transport.
6. The status code is a first-class assertion and is the thing no service-level test can check.
7. The response body is JSON, so assertions reach into a parsed dict — including the envelope, which is a contract fact worth pinning.
8. **`app.dependency_overrides`** replaces any `Depends(...)` callable with a fake, keyed by the original function object.
9. That is how a database session, an authenticated user or an external client is swapped for a test double without touching the route.
10. It is a plain dict on the app, and **it is global and persists**, so an override set in one test is still there in the next.
11. Which produces failures that only appear in a full run and vanish in isolation — the order-dependence of note 3, in FastAPI's own vocabulary.
12. So the override belongs in a fixture whose teardown clears it, never inline in a test.
13. Validation failures return 422 with a body describing the field, and asserting on that body pins the contract rather than the framework.
14. Lifespan events do not run under a bare `ASGITransport` unless asked for, so anything set up at startup is absent — which is either what you want or a silent hole.

> **Recall:** Name two things an endpoint test verifies that a service test structurally cannot. · What is `dependency_overrides` keyed by, and why must it be cleared? · Why does an override leak produce a failure that disappears in isolation?
>
> **Stop:** Do not test framework behaviour. That a 422 is returned for a bad type is FastAPI's test, not yours; that your error envelope wraps it is yours.

---

## Note 9 · The Database, And What H2 Has No Equivalent Of

12 rungs. **Break:** run two tests that each insert one row and assert a count of one.

1. Mocking the persistence layer makes sense until the persistence layer is the thing under test, at which point nothing is left.
2. A repository holds queries, and a query is a string the compiler never checks — only a database can say whether it is correct.
3. So this layer needs a real database that is disposable, which is the same requirement Spring solves with H2.
4. **Python has no H2.** SQLite is the closest and is a genuinely different engine from Postgres or MySQL, so the gap is wider than in the Java case.
5. Which pushes the honest default toward **Testcontainers** — a real engine, started for the run, destroyed after.
6. The cost is Docker, and the benefit is that a query passing has proved something about production.
7. Schema has to come from somewhere: generated from the models, or applied from migrations.
8. **Generating it skips the migrations**, so the suite proves the queries work against a schema nothing in production builds.
9. Running the migrations closes that gap and is the reason to prefer it once migrations exist.
10. State between tests is the second problem: a test asserting one row is only meaningful if the table started empty.
11. A transaction rolled back per test is the cheapest answer and does not survive code that commits.
12. **Truncation between tests survives commits and is slower**, which is the trade, and the choice depends on whether the code under test manages its own transactions.

> **Recall:** Why is SQLite a weaker stand-in for Postgres than H2 is for MySQL? · What does a generated schema fail to prove? · When does per-test rollback stop working, and what replaces it?
>
> **Stop:** Do not build a database fixture before there is a query worth testing. This note earns its keep on the first hand-written query and not before.

---

## Note 10 · External Services

11 rungs. **Break:** point a test at a real third-party API and run the suite on a train.

1. Any test that reaches the network can fail for reasons unrelated to the code, which is the flakiness of note 1.
2. It also fails differently on someone else's machine, in CI, and at 3am, which makes the report untrustworthy.
3. So outbound calls are replaced, and the question is only at which layer.
4. Patching the client object is the crudest and couples the test to how the call is made rather than what is sent.
5. **`respx`** intercepts at the httpx transport, so the real client, real serialisation and real headers all run and only the socket is faked.
6. Which means a change to the request shape is caught, where a patched client would not notice.
7. Recording real interactions and replaying them — **VCR** — trades fidelity for staleness: accurate on the day it was recorded, silently wrong afterwards.
8. **AWS is its own case**: `moto` simulates services in-process and covers most of DynamoDB and S3.
9. LocalStack's public repository was **archived in March 2026**, which removed the default answer for a real endpoint.
10. Testcontainers or a successor is what remains where a real endpoint is required, typically for polyglot or infrastructure tests.
11. **The failure paths are the point**: a timeout, a 500, a malformed body and a slow response are trivial to arrange with a fake and nearly impossible with a real service.

> **Recall:** Why does intercepting at the transport catch bugs that patching the client misses? · What does a recorded cassette lose over time? · What changed about AWS testing in March 2026?
>
> **Stop:** Do not chase full fidelity. The value is in the failure paths, and those are arranged, not recorded.

---

## Note 11 · Time, Randomness And Identity

10 rungs. **Break:** write a test that passes today and fails on the first of the month.

1. A test that reads the clock has a different input on every run, which is non-determinism the code did not ask for.
2. The classic symptom is a suite that passes for a month and fails at a boundary — midnight, month end, a leap day, a timezone shift.
3. **Freezing time** makes the clock an input rather than an ambient fact, and `pytest-freezegun` is deprecated in favour of `pytest-freezer`.
4. Most tests want frozen time, so freezing by default and unfreezing the few that need movement is the cheaper arrangement.
5. `uuid4` and `random` have the same shape, and seeding or patching them turns identity into an input too.
6. But freezing hides a real class of bug — code that behaves differently across a boundary is exactly what should be tested at the boundary.
7. So the rule is to **freeze at a boundary deliberately**, rather than at an arbitrary moment that happens to be safe.
8. Timezone is a separate axis: a test passing in one and failing in another is a bug in the code, not the test.
9. **Injecting a clock beats patching one**, because the injection point is visible in the signature and the patch is not.
10. Which generalises: anything ambient — time, randomness, environment, the current user — is easier to test when it is a parameter, and testing pressure is the cheapest signal that it should be.

> **Recall:** Why is freezing time at an arbitrary moment worse than at a boundary? · What does injecting a clock give you that patching one does not? · Name three ambient inputs besides time.
>
> **Stop:** Do not build a clock abstraction across a codebase for this. Inject where you are already testing, and leave the rest.

---

## Note 12 · Testing Code That Calls A Model

14 rungs. **Break:** run the same prompt twice at temperature zero and diff the outputs.

1. A model returns a different answer to the same input, so the usual contract — same input, same output — does not hold.
2. Temperature zero reduces variance and does not remove it, because floating-point non-associativity and provider-side changes remain.
3. So a test that asserts on model output is asserting on something the code does not control.
4. **The split that resolves it: everything around the model is deterministic and testable; the model's judgement is not, and belongs to evals.**
5. Which makes the first question of any agent test **what am I actually checking** — the plumbing, or the answer.
6. Plumbing is most of it: prompt assembly, tool-call parsing, retries, error handling, state updates, routing.
7. All of that is testable with a **fake model** returning scripted responses — `FakeListChatModel` and its relatives exist for exactly this.
8. A fake that only returns text tests half of it; a fake that returns **tool calls** is what exercises the interesting paths.
9. Capturing the prompt the fake received is often more valuable than the response, because prompt assembly is where silent regressions live.
10. Recording real model decisions and replaying them while tools execute for real is a middle path: deterministic replay, zero API cost, real tool behaviour.
11. It goes stale the same way a VCR cassette does, and for the same reason.
12. **A test suite cannot tell you the agent is good**, only that it is wired correctly — and conflating the two is the most common mistake in this area.
13. Evals answer the other half, on a different cadence, with a different failure signal, and belong in Block 1 rather than here.
14. The practical consequence: a green suite plus a falling eval score is a coherent state, and a system that cannot express it is missing one of the two.

> **Recall:** Why does temperature zero not make a model deterministic? · What exactly can a unit test prove about an agent, and what can it not? · Why is capturing the prompt often worth more than asserting on the response?
>
> **Stop:** Do not build an eval harness here. This note ends where Block 1 begins, and the boundary is the point.

---

## Note 13 · Testing A Graph

13 rungs. **Position to defend**, not recalled: an agent graph has four testable surfaces and they have different costs.

1. A graph is nodes, edges, conditions and state, and each is testable separately.
2. **A routing condition is a pure function of state** — no model, no network, no graph — and is the cheapest thing in the whole system to test.
3. Which makes extracting the condition from the node a testability decision before it is a design one.
4. **A node is a function from state to a state update**, so it is testable by handing it a dict, provided its dependencies are injectable.
5. A node that reaches for a global context is testable only by patching, which is the pressure of note 10 arriving in a new place.
6. **A trajectory test asserts the sequence of nodes visited**, which is the thing unit tests structurally cannot see.
7. Compiling with an in-memory checkpointer is what makes state, resume and history observable in a test.
8. An in-memory checkpointer is for tests and local development only, because it loses everything on restart.
9. **Human-in-the-loop needs its own test**: that a paused run resumes where it stopped rather than restarting.
10. Which requires asserting on what was and was not re-executed, because re-execution on resume is the framework's actual behaviour.
11. Parallel tool calls make ordering assertions necessary, and ordering is where hand-testing gives out first.
12. The four surfaces have wildly different costs — a condition is microseconds, a full graph invocation with a fake model is milliseconds, with a real model is seconds and money.
13. **So the same pyramid applies**: many condition and node tests, few trajectory tests, and the model kept out of both.

> **Recall:** Name the four testable surfaces of a graph in cost order. · Why is extracting a routing condition a testability decision? · What must a human-in-the-loop test assert that an ordinary test does not?
>
> **Stop:** Do not test the framework's own graph machinery. That a conditional edge routes is its test; that yours routes correctly is yours.

---

## Note 14 · The Pyramid, And When It Is Wrong

11 rungs. **Position to defend.**

1. The standard shape is many unit tests, fewer integration tests, fewest end-to-end tests, justified by cost and speed.
2. The justification is real: cost and frequency move in opposite directions, and catching something expensively that a cheap test would catch is waste.
3. But the shape assumes the units are where the risk is, and that is a claim about a specific system rather than a law.
4. In a service that is mostly glue between external systems, **the units are trivial and the seams are where everything breaks**.
5. There the honest shape is heavier in the middle, and a pyramid drawn out of habit produces a suite that tests trivia thoroughly.
6. The opposite failure is a suite of end-to-end tests with no units: slow, and when it fails it says the flow is broken without saying where.
7. **A test's diagnostic precision matters as much as its coverage**, and that is the axis the pyramid actually encodes.
8. Which gives a better question than what shape: **when this fails, how long until I know why**.
9. Integration tests earn their place per **journey**, not per branch, and a branch tested through an integration test is a branch tested expensively.
10. The number of end-to-end tests should be small enough to name individually, and if it is not, the middle is missing.
11. **Consequences decide the ceiling**: the same suite is over-engineered for an internal tool and negligent for a payments system, and neither answer is about testing.

> **Recall:** What does the pyramid actually encode, beyond cost? · Describe a system where the standard shape is wrong, and say what replaces it. · Why is per-journey the right unit for an integration test?
>
> **Stop:** Do not argue about shapes. The question that produces decisions is the diagnostic-precision one.

---

## Note 15 · Making A Suite Runnable By Someone Else

10 rungs. **Break:** clone into a fresh directory and run the suite with no environment set.

1. A suite that needs undocumented setup is a suite only its author runs.
2. Which returns to note 1: a test that is not run notices nothing.
3. The first requirement is a **single command** that installs and runs, with no verbal instructions attached.
4. The second is that it needs no credentials, because a test requiring a real token cannot run in CI or on a new machine.
5. Environment variables read at import time are the usual blocker, and they fail as an import error naming something unrelated.
6. So configuration read lazily, or injected, is a testability property rather than a style preference.
7. Anything requiring Docker splits the suite in two, and marking those tests lets the fast half run without it.
8. **Markers plus a default deselection** is how a suite stays fast locally and thorough in CI.
9. CI is where the ordering assumptions of note 3 surface, because it runs the whole suite from clean every time.
10. And a suite that only passes in CI is as broken as one that only passes locally — both mean the environment is part of the test.

> **Recall:** Why can a suite requiring credentials never be a gate? · What breaks when configuration is read at import time? · What do markers buy beyond organisation?
>
> **Stop:** Do not build a CI pipeline here. One command that works from clean is the whole requirement at this stage.

---

## Note 16 · What Not To Test

11 rungs. **Position to defend.**

1. Every test has a cost paid on every future change, not only when written.
2. So a test that constrains something you intend to change freely is a liability rather than an asset.
3. **Testing the framework** is the clearest example: that a router routes, that an ORM saves, that validation rejects a bad type.
4. Those have tests already, written by people who understand the internals better than you do.
5. **Testing a getter** is the second: no branch, no logic, nothing that can regress independently.
6. **Testing implementation choreography** is the third and the most damaging — asserting which private method was called constrains the shape rather than the behaviour.
7. That suite goes red on every refactor while catching no bugs, and teaches people that red means nothing.
8. Coverage percentage is the usual driver, and it is a **proxy that is trivially gamed** by tests with no assertions.
9. Coverage's honest use is inverted: not as a target, but as a **map of which branches nothing exercises**.
10. The line worth holding: test **behaviour you would notice breaking**, at the **boundary you own**.
11. Everything else is either someone else's test or a cost with no counterpart.

> **Recall:** Why is testing choreography worse than testing nothing? · What is coverage's honest use, and what is its dishonest one? · State the line for what to test in one sentence.
>
> **Stop marker — binding:** Do not configure coverage tooling. Thresholds, exclusions and report formats are a day gone and change nothing about which tests exist.

---

## Note 17 · Testing A Security Boundary

12 rungs. **Position to defend.**

1. An authorisation check is a branch, so it is testable exactly like any other branch.
2. Which makes it unusual: it is the highest-consequence logic in most systems and among the cheapest to test.
3. **The negative case is the test.** That an authorised caller succeeds proves nothing about the guard.
4. So every check needs at least: authorised passes, unauthorised is refused, and the boundary case is decided deliberately.
5. A guard whose condition is accidentally always true passes the positive test and fails no test at all — the vacuous test of note 2, at the worst possible place.
6. Which is why the mutation check matters most here: invert the condition and require the negative test to go red.
7. A check duplicated across call sites needs the test at each site, or the copy that drifts is the one nothing covers.
8. **Enumerating the call sites is itself the test** — a registry with a test asserting every entry is guarded catches the next tool nobody wired up.
9. For an agent, the surface is the tool: which tools an audience can see, and what each does with a target that is not the caller.
10. That is a table-driven test, and the table is more valuable than the assertions because it makes the policy explicit.
11. An access-control test is also documentation of the policy, read by whoever changes it next.
12. **And it is the one class of test where a false pass is not a maintenance problem but an incident.**

> **Recall:** Why does the positive case prove nothing? · What does enumerating call sites catch that per-function tests do not? · Why does the mutation check matter more here than elsewhere?
>
> **Stop:** Do not write injection tests here. Adversarial input against an agent is Block 4, and it is a different discipline from testing a boundary.

---

## Note 18 · Retrofitting A Suite Onto Untested Code

11 rungs. **Practice, not recall.** This is the note that gets done rather than recited.

1. A codebase with no tests has no safe change, which makes the first test the hardest and every later one easier.
2. So the first target is chosen for **ease, not importance** — momentum matters more than coverage at the start.
3. **Pure functions first**: no dependencies, no mocking, no fixtures, a dict in and a value out.
4. Those exist in more places than expected — parsers, builders, formatters, routers, validators.
5. The second target is whatever has broken before, because a bug that happened once is evidence about where the risk is.
6. The third is whatever is about to be changed, since a test written just before a refactor is the one that pays immediately.
7. **Untestable code is a finding, not an obstacle**: a function that cannot be tested without patching three globals is telling you something about its design.
8. Extracting a pure function to make it testable is the most common refactor this produces, and it is an improvement independent of the test.
9. Writing tests against current behaviour — including behaviour you think is wrong — is correct, because the test's job is to notice change.
10. A wrong behaviour pinned by a test can be changed deliberately; unpinned, it changes accidentally.
11. **The order is: easiest, then most-broken, then most-imminent** — and coverage is an outcome rather than a plan.

> **Recall:** Why is the first test chosen for ease rather than importance? · What does untestable code tell you? · Why pin behaviour you believe is wrong?
>
> **Stop:** Do not plan a coverage campaign. Three tests that run today beat a plan for thirty.

---

## Note 19 · Reading A Suite You Did Not Write

9 rungs. **Practice, not recall.**

1. A suite is the most honest documentation a codebase has, because it is executable and therefore cannot drift silently.
2. So the first read is not the code — it is the test names, which state the behaviours somebody thought worth protecting.
3. A test file with no negative cases says the failure paths were never considered.
4. A test file where every name has one clause says the code has no branches, or the branches were never tested.
5. **Fixtures reveal the seams**: what is faked is what the author considered a boundary.
6. Anything mocked in every test is a dependency the design is uncomfortable with.
7. Anything never mocked is either genuinely pure or a hole.
8. A suite that takes minutes is one nobody runs while writing, so its failures are found in CI rather than in the loop.
9. **And what a suite does not test is a sharper signal than what it does** — the untested branch is where the next incident is.

> **Recall:** Why is a suite more honest than a README? · What does a fixture list tell you about a design? · Why is the absence of a test more informative than its presence?
>
> **Stop:** Do not audit a suite before you have written one. This note reads differently after note 17 and is nearly meaningless before it.

---

## Coverage

Note files are numbered to match this list and named as briefly as the subject allows, never the full heading — note 1 is `01-Why-Test.md`.

| Note | Rungs | Written |
|---|---|---|
| 1 · What Tests Are For | 11 | [[01-Why-Test]] |
| 2 · Your First Python Test | 12 | [[02-First-Test]] |
| 3 · The Vacuous Test | 12 | [[03-Vacuous-Tests]] |
| 4 · pytest's Model | 11 | [[04-Pytest-Model]] |
| 5 · Fixtures, And Where State Leaks | 14 | [[05-Fixtures]] |
| 6 · Async Changes The Rules | 12 | — |
| 7 · Test Doubles, Named Precisely | 13 | — |
| 8 · Testing A FastAPI Endpoint | 14 | — |
| 9 · The Database, And What H2 Has No Equivalent Of | 12 | — |
| 10 · External Services | 11 | — |
| 11 · Time, Randomness And Identity | 10 | — |
| 12 · Testing Code That Calls A Model | 14 | — |
| 13 · Testing A Graph | 13 | — |
| 14 · The Pyramid, And When It Is Wrong | 11 | — |
| 15 · Making A Suite Runnable By Someone Else | 10 | — |
| 16 · What Not To Test | 11 | — |
| 17 · Testing A Security Boundary | 12 | — |
| 18 · Retrofitting A Suite Onto Untested Code | 11 | — |
| 19 · Reading A Suite You Did Not Write | 9 | — |

---

## Deferred

| Topic | Goes to |
|---|---|
| Eval sets, golden data, judge alignment, pass@k | `01-Agent-Evals` — note 12 ends exactly where that begins |
| Load and stress testing, `locust`, capacity | `05-Cost-And-Latency`, and there is already a `locust.py` in Xarvis |
| Prompt-injection and adversarial input | `04-AI-Security` notes 19 and 20 |
| Tracing as a debugging tool, span assertions | `02-Observability` |
| CI pipelines, deployment gates, branch protection | `Devops/`, and it is January work |
| Property-based testing, `hypothesis` | outside this vault for now — worth a note once the basics are habitual |
| Mutation-testing frameworks | deliberately out: note 3's manual check is the habit, and the tooling is an optimisation of something not yet done |

---

## Where this lands in Xarvis

**The starting point, verified 2026-09-07:** eleven test files, **zero assertions**, no `conftest.py`, no pytest configuration in `pyproject.toml`, and `pytest==9.0.2` already in requirements. `anyio` and `httpx` are present too, so **the async testing stack is installed and unused**. One test file calls the live HRMS with a hardcoded bearer token in `setup_method` — which is note 15 rung 4 exactly, and the reason that file can never run in CI.

**The first real test already exists**, written 2026-09-07: `route_after_tools` in the admin graph, nine cases, no graph, no model, no network. That is note 13 rung 2 and note 18 rung 3 arriving together, and it is the template for what comes next.

**The obvious next targets, in note 18's order.** `sse_events.py` — pure frame builders, no dependencies, and build item 1 already names them as the pytest entry point. `tool_progress_message` and `extract_tool_names` in the same file. `find_pending_disambiguation` and `parse_tool_payload`, which the router already exercises indirectly. Then `is_allowed_admin` and `has_tool_access`, which is note 17 territory and build item 4.

**Note 17 maps onto a live finding.** Two authorisation holes were found by reading rather than by testing: a guard whose condition was accidentally always true, and a rule duplicated across call sites where one copy drifted. Those are rungs 5 and 7 of that note, in this codebase, already. The registry test at rung 8 is what would have caught both.

**Note 12 has a specific shape here.** The agent is Gemini through LangChain, so the fake-model work is `FakeListChatModel` returning tool calls — and the Gemini empty-text behaviour that shaped `sse_events.py` is exactly the kind of thing a scripted fake reproduces cheaply and a real model reproduces unreliably.

**And note 9 is smaller than it looks.** The persistence surface is a DynamoDB cache and a checkpointer, so it is `moto` rather than Testcontainers, and the checkpointer has an in-memory implementation that is already the right test double.

---

## Sources to verify against

- [FastAPI — Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/), which uses `@pytest.mark.anyio` with `ASGITransport`
- [LangGraph — Test](https://docs.langchain.com/oss/python/langgraph/test), node-level, trajectory and checkpointer testing
- [pytest — How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), scopes and teardown
- [RESPX user guide](https://lundberg.github.io/respx/guide/), transport-level httpx mocking
- [Moto for mocking AWS services in Python tests](https://oneuptime.com/blog/post/2026-02-12-moto-mocking-aws-services-python-tests/view)
- [Your LocalStack CI is broken — three options](https://dev.to/peytongreen_dev/your-localstack-ci-is-broken-here-are-your-three-options-41o8), the March 2026 archival and what replaced it
