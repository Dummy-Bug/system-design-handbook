#dependency-injection #fastapi #langgraph #architecture #python #syllabus

# 13 · Dependency Wiring — Syllabus

**5 notes, 33 rungs.** How a function gets the things it needs, and how a request gets an identity. Generic — the pattern, not one codebase's implementation, which is mapped at the bottom.

Deliberately smaller than [[AI-Engineering/12-Configuration/00-Syllabus|folder 12]]. That folder had 56 rungs because precedence has genuinely surprising corners; this one has one idea applied at four boundaries, so the work is in the applying rather than in the learning.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — a function reaches for a collaborator, therefore its signature is a lie, therefore a caller cannot supply a different one, therefore it cannot be tested without rebuilding the world. Rungs are not topics and not section headings.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.**

**Currency check (2026-09-12), verified by importing against the versions this actually targets — fastapi 0.141.1, langgraph 1.2.11.** All three mechanisms note 5 depends on are present: `langgraph.runtime.Runtime`, `langgraph.prebuilt.ToolRuntime`, and `context_schema` on `StateGraph`. Worth checking rather than assuming, because the older `config.configurable` approach is what most writing still shows, and the typed-context API replaced it during the 1.x line.

---

## How to teach from this

**One note at a time, one rung at a time.** A rung is taught in the terminal first, and only after a response does that one section get appended to the note — a note is never written in one pass. That is the method folder 12 was built with and it is the method here.

**Where a rung says break, it is run, not read.** This folder gets its own lab at `~/Desktop/projects/wiring-lab/`, one folder per note, built at the versions above so that what the notes claim about `ToolRuntime` is what the installed library actually does.

**The test of whether it landed** is not whether you can define dependency injection. It is whether you can take one function out of a running service and call it from a script, with inputs you typed yourself, and have it work.

---

## Note 1 · Hidden Inputs

Written up as [[01-Hidden-Inputs]] — **complete 2026-09-13**, all 7 rungs in 8 sections from 12 lab files: `note01/a_the_signature_is_a_promise.py`, `b_inside_the_program.py`, `c_from_outside_the_program.py`, `d_rebuild_the_startup.py`, `e_three_hidden_inputs.py`, `f_one_rule_from_outside.py`, `g_what_the_checker_can_see.py`, `h_everything_on_the_def_line.py`, `i_a_name_in_a_string.py`, `j_a_name_in_a_parameter.py`, `k_a_setting_named_in_a_string.py` and `l_a_setting_declared_once.py`. Rung 7's two files need `pydantic-settings`, added to the lab with `uv add`. `j` and `l` fail the checker on purpose and joined `g` in the lab's ty exclude list. Rung 5's claim that a forgotten `admin_ids=` is reported before running was verified against a scratch copy with that line deleted, not a lab file, since a file failing the checker for a second time would teach nothing new. Rung 3 runs to two sections: the one-line rebuild, then a function reaching for three things.

**`g_what_the_checker_can_see.py` fails the type checker on purpose**, because the failure is rung 4's lesson. It is listed under `[tool.ty.src] exclude` in the lab's `pyproject.toml`, so `uv run ty check` stays green for the rest of the lab, and the note runs `uv run ty check` against that one file by name — which still checks it, since ty only enforces an exclusion on an explicitly named path when given `--force-exclude`. Verified 2026-09-13 on ty 0.0.80, in a scratch copy first and then in the lab. Any later file that fails a checker on purpose goes in the same list.

7 rungs. **Break:** take a function that reaches for its collaborators and try to call it from a script with no app running. Count what you have to build first.

1. A signature is a promise about what a function needs, and a function that reaches for a collaborator inside its body breaks that promise without saying so.
2. The reaching version works perfectly at runtime, which is why it spreads — nothing is wrong until something tries to call it from outside the app.
3. Then the cost arrives all at once: to exercise one line you must first reproduce the entire ambient world the function assumes.
4. The pattern has a name, service locator, and what makes it an anti-pattern is not taste — the dependency is invisible to the type checker, to the IDE, and to a search for callers.
5. Passing the collaborator in as a parameter moves it into the signature, and a caller can then supply a different one without faking anything.
6. A string key makes it worse in a specific way: it cannot be renamed safely, cannot be checked, and fails at the moment of use rather than at startup.
7. This argument already won one layer down — a settings class replaced scattered `os.environ` lookups for exactly these reasons, and this is the same argument about objects instead of strings. [[AI-Engineering/12-Configuration/01-Declared-Not-Fetched|Declared, Not Fetched]]

> **Recall:** What does a signature promise, and what breaks the promise? · Why does the problem stay invisible in production? · What can a checker do with a parameter that it cannot do with a string key?

---

## Note 2 · Composition Root

Written up as [[02-Composition-Root]] — **complete 2026-09-13**, all 6 rungs in 6 sections from 10 lab files: `note02/a_someone_has_to_build_it.py`, `b_built_in_three_places.py`, `c_the_constructor_changes.py`, `d_one_function_builds_it.py`, `e_settings_read_inside.py`, `f_settings_read_in_the_root.py`, `g_environment_checked_everywhere.py`, `h_environment_decided_in_the_root.py`, `i_root_returns_a_dict.py` and `j_root_returns_named_attributes.py`. `j` also fails the checker on purpose and is in the ty exclude list. Rung 6's method-name row — a misspelled `leave_balanse_for` unreported through the dictionary and reported through the dataclass — was verified against scratch copies of `i` and `j`, not lab files. `c` fails the checker on purpose and is in the lab's ty exclude list.

**Stranger's pass, 2026-09-13.** Read front to back as somebody with no lab access. Fixed across notes 1 and 2: the note-2 heading now matches its filename, its info callout says three words rather than two, every `ty check` names its file so the bare and named forms no longer differ without explanation, the comment-header caveat is stated once per note instead of six times in total, the `admin_ids` output block gained its command line, note 1's configuration section now links to folder 12 for `BaseSettings` and `validation_alias`, and the method-name typo table is backed by both real `ty` runs. Two editor rows that asserted measured behaviour were reworded to state what follows from the declaration, since PyCharm was never tested. The in-memory-regardless-of-`ENV` row was verified by handing `salary_tool` an `InMemorySalaries()` under `ENV=prod`, which printed `from memory`.

6 rungs. **Break:** count how many places in a small app know how to construct the same object, then change how it is constructed.

1. Once functions stop fetching their collaborators, something else has to construct them and hand them over.
2. If construction is scattered, every call site knows how to build the thing, so changing how it is built is a search rather than an edit.
3. A composition root is the one place that builds the object graph — a single function, run once at startup, holding every wiring decision.
4. It is also the only place allowed to read configuration, which is what stops settings from leaking into code that should not care where values come from.
5. Environment differences belong here as branches — in-memory locally, the real thing in production — so nothing downstream has to ask which environment it is running in.
6. What it hands back should be a typed object rather than a dictionary, because the entire point of the exercise was that names can be checked.

> **Recall:** Why does scattered construction make a change into a search? · What does the composition root stop from spreading? · Why is a dictionary the wrong return type?

---

## Note 3 · Declared At The Door

Written up as [[03-Declared-At-The-Door]] — **complete 2026-09-13**, all 7 rungs in 7 sections from 8 lab files: `note03/a_the_framework_is_the_caller.py`, `b_the_framework_supplies_it.py`, `c_providers_ask_for_providers.py`, `d_yield_without_finally.py`, `e_yield_with_finally.py`, `f_override_the_provider.py`, `g_built_once_per_request.py` and `h_only_where_the_framework_calls.py`. `h` fails the checker on purpose and is in the lab's ty exclude list. Rung 5 was checked against a claim from a web search that `TestClient` captures dependencies when it is created, so overrides must be set first: on fastapi 0.141.1 an override set after the client exists took effect on the next request, and one set before the client also worked, verified against a scratch copy. Rung 4 was rewritten after running it: its first wording said a yielding provider closes reliably, and the run showed a close written plainly after `yield` is skipped when the route raises. It was also taught once in chat as running after the response is sent; on fastapi 0.141.1 with starlette 1.6.0, through `TestClient`, the close finished before the client received its response, and only that observation is in the note. Rung 2 uses the `Annotated[X, Depends(provider)]` spelling. The older spelling, `x: X = Depends(provider)`, was run against a scratch copy and behaves identically, but the lab's ruff rejects it with B008 — a function call in an argument default — which is the reason the notes use `Annotated`, and why that detail stays here rather than in the note. Requests are sent with FastAPI's `TestClient`, which needs `httpx` — already present in the lab through its dependencies, version 0.28.1.

7 rungs. **Break:** swap a real collaborator for a fake in a test without editing the function under test.

1. A web framework sits exactly where a request becomes a function call, which makes it the natural place to supply what that function needs.
2. The mechanism is a parameter whose default names a provider, and the framework calls the provider and passes the result in.
3. Providers compose, because a provider can declare dependencies of its own, so a chain assembles without any link knowing about the others.
4. A provider that yields rather than returns gets a place for teardown, which is how a per-request resource is opened and closed — but only a close inside `finally` runs when the route raises; one written plainly after the `yield` is skipped, and every failed request leaks.
5. The same declaration is the test seam — override the provider and the real thing is replaced by a fake, with nothing about the function changing.
6. Results are cached per request, so a dependency declared in three places is built once and shared.
7. It is not free, and the limit is the subject of note 5: the framework supplies only what was declared to it, and only to functions the framework itself calls.

> **Recall:** What does a provider that yields buy you? · Why does the test seam cost nothing extra once the parameter exists? · What is the framework unable to reach?

---

## Note 4 · Protected By Default

Written up as [[04-Protected-By-Default]] — **complete 2026-09-13**, all 6 rungs in 6 sections from 7 lab files: `note04/a_who_is_calling_is_a_dependency.py`, `b_middleware_checks_the_path.py`, `c_the_route_nobody_listed.py`, `d_deny_by_default.py`, `e_protection_follows_the_router.py`, `f_a_real_check.py` and `g_what_middleware_keeps.py`. Every file passes the checker, so note 4 adds nothing to the ty exclude list. Rung 4 refuses with 422 rather than 401, because a required `Header()` that is absent is reported as a missing input; the note says so rather than hiding it, and rung 5 is where the check returns 401 deliberately. Rung 3's `c` uses a `startswith` prefix and a bare `call_next` fallthrough deliberately, because that is the shape of the real middleware the refactor in [[Current-Standing/TODO/08-Composition-And-Lifecycle]] replaces. Identity is carried in a plain `X-Employee-Id` header throughout this note, so the examples stay about where the check is declared rather than about how a token is verified.

6 rungs. **Break:** add a new route to a service and find out whether it is authenticated before you read any code.

1. Who is calling is a dependency like any other, which means it can be reached for or declared, and the choice has consequences beyond style.
2. Reached for, it becomes middleware that inspects the path and decides — so the rule protecting a route lives in a different file from the route.
3. A path comparison has exactly one default, and that default is open: a route nobody remembered is served to anyone.
4. Declared, the check attaches to the router, so protection becomes a property of where a route lives rather than of a list someone maintains.
5. That inverts the default — a route added to a protected router is protected whether or not anybody was thinking about it.
6. Middleware keeps what is genuinely ambient and applies to everything: the request id, logging context, CORS. The test is whether it needs to know which route it is.

> **Recall:** Which default does a path check have, and why is that the wrong one? · What belongs in middleware after this change?

---

## Note 5 · Past The Framework Edge

Written up as [[05-Past-The-Framework-Edge]] — **complete 2026-09-13**, all 7 rungs in 8 sections from 12 lab files: `note05/a_the_model_loop_is_the_caller.py`, `b_the_global_that_bridges.py`, `c_the_tool_module.py`, `d_testing_the_rule.py`, `e_two_requests_one_global.py`, `f_a_key_per_request.py`, `g_who_supplies_the_key.py`, `h_the_key_is_the_task.py`, `i_the_context_is_declared.py`, `j_what_the_model_is_asked_for.py`, `k_the_declared_tool_module.py` and `l_testing_the_rule_now.py`. Rung 1's section covers syllabus rungs 1 and 2, since the boundary and the model loop are one demonstration; `b` is rung 3 and `c`+`d` are rung 4. Nothing in note 5 is in the ty exclude list — the three graph files carry an inline `# ty: ignore[invalid-argument-type]` instead, for the reason below.

**The concurrency leak is rung 5**, across `e_two_requests_one_global.py`, `f_a_key_per_request.py`, `g_who_supplies_the_key.py` and `h_the_key_is_the_task.py` — three sections. Its shape came from the user's own diagnosis, which was sharper than the draft: the leak happens because **the key is static**, so both requests write `CURRENT_CALLER["employee_id"]` and the second lands on the first. Following that through is what makes the rung: a key per request does fix it, but the tool must then receive that key, and `sorted(tool.args)` shows the model would be the one filling it — `['employee_id', 'request_id']`. A `ContextVar` is that same per-request key with the task as the key, supplied invisibly. It closes the leak and leaves the testing cost untouched, so ContextVar is not the answer this note is building toward — worth stating plainly, since Xarvis uses one today.

Two lab-file corrections while writing rung 5: a long f-string in `f` was split with a local variable rather than reformatted into a wrapped `print`, and `g` reads `sorted(tool.args)` rather than `tool.tool_call_schema.model_json_schema()["properties"]`, which ty rejects because that attribute is a union that may be a v1 model or a plain dict.

**Rung 6 is `i_the_context_is_declared.py`** — `context_schema` on the graph, `ToolRuntime[Caller]` on the tool, the caller passed once as `context=` at invoke time.

**Rung 7 is `j_what_the_model_is_asked_for.py`, `k_the_declared_tool_module.py` and `l_testing_the_rule_now.py`**, in two sections. `j` reuses `sorted(tool.args)` so the worry `g` raised is answered with the same instrument: `keyed_by_request` shows the model `['employee_id', 'request_id']`, `with_runtime` shows it `['employee_id']`. `k` and `l` mirror the `c`/`d` pair on the fixed side — a no-run tool module and a test that now passes, checking both directions of the refusal rule with no server, graph, model or key.

**Stranger's pass on note 5, 2026-09-13.** All 12 code blocks were checked against their lab files and match byte for byte. Three defects fixed: the note claimed the ty suppression appears in every file when it is in 3 of 12, the files that build a graph; note 5 carried no comment-header caveat while showing tracebacks citing line 16 for code shown as four lines; and it held the folder's only empty-header table plus a plain-text `note 4` inside a mermaid node while linking properly everywhere else. A link to [[02-Composition-Root]] was added where the per-request caller meets the built-once services, since note 5 previously linked notes 1, 3 and 4 but never 2. One table row asserting that a forgotten context is named by the checker was reasoning rather than measurement when written; it is now measured — `error[missing-argument]: No argument provided for required parameter 'runtime' of function 'salary_for'`.

**The lab gained `[tool.ruff] line-length = 100`**, matching config-lab. It had been running on ruff's default 88 while carrying a 95-character line that survived only because ruff format will not split a line ending in a `# ty: ignore` comment. Adding the setting reformats nothing: all 50 files were already clean at 100.

**Building a `ToolRuntime` by hand takes six fields** — `state`, `context`, `config`, `stream_writer`, `tool_call_id`, `store` — all required, only `context` meaningful to the tool. `dataclasses.replace(DEFAULT_RUNTIME, context=...)` also works and is ty-clean, but returns a `Runtime` rather than a `ToolRuntime`, so the note builds one explicitly to match what the tool's signature declares.

**The state shape was settled here, and it forced a real trade-off.** `ToolRuntime` types its `state` field as a dict, so a dataclass or pydantic state runs correctly but prints four lines of `PydanticSerializationUnexpectedValue` on every turn, while a `TypedDict` state runs silently but trips ty's `invalid-argument-type` false positive. Measured all three. Chose the `TypedDict` — `MessagesState` plus `# ty: ignore[invalid-argument-type]` — **because that is what Xarvis does**: `orchestration/state.py` declares a `TypedDict` state and `orchestration/admin/graph.py:23` carries the same ignore with a comment calling it a false positive. Rungs 1 and 3 were rewritten to use the same state so the shape does not change mid-note. The state is a `@dataclass` rather than `MessagesState`: both run correctly, but `StateGraph(MessagesState)` trips a ty false positive — `Argument type MessagesState does not satisfy upper bound TypedDictLikeV1 | ... | BaseModel` — the same one Xarvis carries a `# ty: ignore[invalid-argument-type]` for in its graph builders. A dataclass is inside that bound, so the teaching file needs no ignore comment. A pydantic `BaseModel` state is also clean but costs `Annotated`, `add_messages` and a reducer to explain.

7 rungs. **Break:** call an agent tool from a script — no server, no model, no API key.

1. The framework's injection reaches the functions the framework calls, and stops there.
2. An agent's tools are called by the model loop instead, so nothing a route declared ever reaches them.
3. That is the honest reason a global gets introduced: it is the only thing both sides can see, and it works.
4. It keeps working until something tries to test a tool, at which point the full cost from note 1 arrives — and tools are where the authorization checks live.
5. The graph library has its own version of the same mechanism: a typed context object passed once when the graph is invoked, and injected into each tool as a parameter.
6. That parameter is invisible to the model — it never appears in the tool's schema — so the model cannot fill it, be confused by it, or invent it.
7. Which closes the loop. Both boundaries now declare what they need, and a tool can be called from a test with a context written by hand.

> **Recall:** Why does `Depends` not reach a tool? · What makes the injected parameter safe to add to a tool the model calls? · Which two boundaries does this folder end up covering?

---

## Coverage

Note files are numbered to match this list. Sections and lab files are filled in as each note is written.

| Note | Rungs | Break |
|---|---|---|
| 1 · Hidden Inputs | 7 | call a reaching function from a bare script |
| 2 · One Place Builds It | 6 | change how one object is constructed |
| 3 · Declared At The Door | 7 | swap a real collaborator for a fake |
| 4 · Protected By Default | 6 | add a route, discover if it is protected |
| 5 · Past The Framework Edge | 7 | call a tool with no server and no key |

---

## Deferred

| Topic | Goes to |
|---|---|
| Writing the tests this makes possible — fixtures, doubles, async | [[AI-Engineering/11-Testing/00-Syllabus|folder 11]], which already covers all three |
| Where values come from, precedence, secrets | [[AI-Engineering/12-Configuration/00-Syllabus|folder 12]] |
| DI container libraries — wireup, dishka, dependency-injector | out. They earn their place across multiple entry points, and the composition root in note 2 is the thing to own first |
| Authentication itself — OAuth, JWT verification, session storage | out. Note 4 is about where the check is declared, not how identity is proven |
| Repository and unit-of-work patterns | out, and a different subject that only looks adjacent |

---

## Where this lands in Xarvis

The refactor plan is [[Current-Standing/TODO/08-Composition-And-Lifecycle]], written 2026-09-12 from a read of `refactor`, and every note here maps to a phase in it.

**Note 1 is the whole reason that plan exists.** `RequestContext.get_current()` is called at 55 sites across 48 files and services are pulled out by string 39 times, so one tool declares one parameter and actually has seven inputs. That is why the system has no tests — not discipline, price.

**Note 4 has a live example.** Authentication is decided by a path comparison in middleware, with a fallthrough that serves anything unmatched, so a new route is unauthenticated unless somebody edits that file. The public-path list in it is already wrong in a way that has been harmless by luck.

**Note 5 is the phase that unlocks the rest**, and the mechanism only became available three weeks ago — the LangGraph upgrade taken to close two CVEs is what makes the typed context possible. The global was the correct workaround for the version that code used to run on, and stopped being correct without anybody noticing.

---

## Sources to verify against

- [LangChain — Runtime](https://docs.langchain.com/oss/python/langchain/runtime), the typed context object for nodes and tools
- [ToolRuntime reference](https://reference.langchain.com/python/langgraph.prebuilt/tool_node/ToolRuntime), and why the parameter stays out of the model's schema
- [FastAPI — Testing Dependencies with Overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/), the test seam in note 3
- [Service locator pattern](https://en.wikipedia.org/wiki/Service_locator_pattern), for the named argument behind note 1
