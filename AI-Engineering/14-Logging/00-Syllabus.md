#logging #python #structlog #observability #syllabus

# 14 · Logging — Syllabus

**6 notes, 51 rungs.** From a clean slate: what a log is, then how important an entry is, then what a line says, then the parts Python's `logging` is built from, then structured logs, and finally one real service's setup — the society tax agent's `configure_logging()`, mapped at the bottom. The goal is that every line of that function reads as obvious.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — a program runs with nobody watching, therefore the only record of what happened is what it wrote down, therefore what it writes decides whether a failure can be found at all. Rungs are not topics and not section headings.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it**, and so that **no term is used before it is defined.** The order follows Python's own Logging HOWTO: what logging is, when to use it, levels, the shape of a line, and only then loggers, handlers and formatters.

**Currency check (2026-10-06), on Python 3.13.15 and structlog 26.1.0.** Three things surprise people. With nothing configured, Python's threshold is **WARNING**, so `logger.info(...)` prints nothing at all. structlog's pretty terminal tracebacks show **local variables by default** (`RichTracebackFormatter(show_locals=True)`), which prints whatever a function was holding — passwords included. And Starlette's catch-all error handler **re-raises after responding**, so a server logs every crash a second time unless the crash is caught inside the app.

---

## How to teach from this

**One note at a time, one rung at a time.** A rung is taught in the terminal first, and only after a response does that one section get appended to the note — a note is never written in one pass.

**Where a rung says break, it is run, not read.** Every note has a lab folder in `~/Desktop/projects/logging-lab/src/logging_lab/`, `note01/` for note 1 and so on, so the outputs quoted in the notes are reproducible rather than taken on faith.

**Clean slate.** Nothing is explained by comparison with another language or framework; each idea is built from the one before it.

**This is craft, not recall.** The test of whether it landed is reading a service's logging setup and knowing, for any line in it, what would go wrong if it were deleted.

---

## Note 1 · What A Log Is

**Break:** `a_what_print_leaves.py` — five payments, one fails, reported with `print()`. Try to say when it failed, which payment it was, and how bad it is.

1. While a program runs, things happen — a request arrives, a payment succeeds, a call to a bank fails. Each of these is an **event**.
2. A **log** is the program's written record of its events, made at the moment each one happens, because afterwards there is nothing else to look at.
3. One entry in that record is a **log line**: what happened, plus the details that make this occurrence different from the last one — which payment, what amount.
4. `print()` also writes text, so the difference has to be stated: `print()` is output for the person running the program right now; a log is a record for someone investigating later.
5. A service runs with nobody watching — on servers, often many copies at once, all day — so its log is the only witness to a failure.
6. That later reader searches the record, and can only search on what each line carries: when, how important, where in the code, and for which request.
7. Python ships logging as a standard module, `logging`, which every library also uses — so learning it is learning how every part of a service reports itself.

> **Recall:** What is an event? · What is a log, and when is it written? · What makes `print()` the wrong tool for a service? · What can a later search filter on, and why only that?

---

## Note 2 · How Important — Levels

**Break:** `a_levels_are_numbers.py`, then `b_nothing_configured.py` — two log calls with nothing configured: one line vanishes, the other prints with nothing but its message.

1. Events are not equally important — `payment started` and `database unreachable` should not be weighed the same — so every log line carries an **importance**, called its **level**.
2. Python has five: **DEBUG** (detail for diagnosing a problem), **INFO** (things working as expected), **WARNING** (something unexpected, but still working), **ERROR** (an operation failed), **CRITICAL** (the program itself may not be able to continue).
3. Each level is a number, increasing with importance: 10, 20, 30, 40, 50.
4. Numbers can be compared, which allows a **threshold**: a line is kept only if its level is at or above it, and thrown away otherwise.
5. With nothing configured, Python's threshold is WARNING — which is why the INFO line vanishes and the ERROR line survives.
6. The surviving line is bare — only its message, no time, no level — because nothing has yet said what a line should look like.
7. The threshold is set in one line, so production keeps the noise out and debugging lets it back in, without changing a single log call — though lowering it only affects lines written from then on.
8. Picking a level when writing a call is a decision about who needs to see it: a developer chasing a bug, the team watching the service, or someone who must be told now.

> **Recall:** What is a level for? · Name the five in order. · Why are they numbers? · What is a threshold, and what is Python's default? · Why did the surviving line have no time or level?

---

## Note 3 · What A Line Says

**Break:** configure a threshold and a format, and watch note 2's missing INFO line come back with a time, a level and a name.

1. A line needs more than its message — when it happened, how important it was, which part of the code wrote it — or a later search has nothing to filter on.
2. `logging.basicConfig(level=..., format=...)` sets the threshold and the shape of every line in one call, made once when the program starts.
3. The format is a template of placeholders — `%(asctime)s`, `%(levelname)s`, `%(name)s`, `%(message)s` — filled in for each line.
4. `logging.getLogger(__name__)` names the writer after the module it lives in, so `%(name)s` says which file a line came from.
5. Details go in as arguments — `logger.info("paid %s", amount)` — not pre-built strings, so a line that is thrown away is never even formatted.
6. When an operation fails with an exception, `logger.exception(...)` writes the line at ERROR and attaches the traceback — the exact place in the code where it failed.
7. Lines go to the terminal by default — to standard error, the second of every program's two output streams; a file is one alternative; a service writes to its output streams and lets the platform collect them.
8. `basicConfig` is the simple version of something with separate parts underneath, and those parts are what a real service configures.

> **Recall:** What must a line carry besides its message? · What does `basicConfig` set? · Where does `%(name)s` come from? · Why pass details as arguments? · What does `logger.exception()` add?

---

## Note 4 · Who Speaks, Where It Goes

**Break:** add a second output and get every line twice; import a library and watch its lines arrive in your format.

1. Under `basicConfig` there is a flow: the **logger** first checks its threshold, and below it nothing more happens; only then is a **record** created, keeping the message and its arguments separate; **handlers** send it somewhere; and each handler's **formatter** joins message and arguments into text and builds the line — the order that makes argument-style calls nearly free when thrown away.
2. A **logger** is who is speaking — named, usually after its module — and can have its own threshold.
3. A **handler** is where a record goes — the terminal, a file, a network service — and one logger can have several.
4. A **formatter** belongs to a handler, so the same record can look different in two places.
5. Loggers form a tree by their dotted names — `uvicorn.error` sits under `uvicorn` — with the **root logger** at the top.
6. A record **propagates** up the tree to the handlers of every logger above it, which is how one handler on the root sees every library's lines.
7. Which is also how a line gets written twice: two handlers on its path means two copies.
8. With no configuration at all, there is no handler anywhere, so Python uses a built-in last-resort one — WARNING and above, message only — which is exactly note 2's experiment.
9. A library that installs its own handlers keeps its own format; taking control means removing them and letting its records propagate to yours.

> **Recall:** Record, logger, handler, formatter — which does what? · Why does one handler on the root see every library? · Two causes of duplicate lines? · What happens when nothing is configured?

---

## Note 5 · Lines Machines Can Read

**Break:** search a thousand text lines for one user's failures, then query the same events as JSON.

1. `"login failed for asha after 3 attempts"` is easy to read and hard to search — every detail is buried in a sentence someone has to parse back out.
2. A **structured** log line is a set of named values — `event=login_failed user=asha attempts=3` — written as one JSON object per line.
3. Log tools index the names, so every failure for one user becomes a query, not a pattern match.
4. **structlog** is a library built around that: a log call produces an **event dict** — the event's name plus the values passed.
5. The dict goes through **processors**, a chain of small functions that each add or change something: a timestamp in UTC, marked as UTC — closing note 3's time-zone gap — the level, the logger's name.
6. The last processor is the **renderer**: JSON for machines, coloured text for a person at a terminal.
7. Passing the request ID into every log call by hand does not scale, so structlog can read it from **context variables** — set once per request, merged into every line written during it.
8. Context variables follow each request's own task, so requests running at the same time never see each other's IDs.
9. A processor is also the right place to **mask secrets**, because every line passes through it on the way out.

> **Recall:** What does structured logging change for the person searching? · What is an event dict? · What does a processor do, and which one comes last? · How does a request ID reach a line nobody passed it to?

---

## Note 6 · One Pipeline For Everyone

Reading `configure_logging()` line by line. **Break:** run uvicorn with structlog set up naively and see two formats in one log; then make it one.

1. structlog formats our own lines, but uvicorn, httpx and LangGraph log through the standard `logging`, so a naive setup has two formats in one log.
2. The fix is one pipeline: structlog hands its event dict to the standard library (`wrap_for_formatter`), and one handler renders everything (`ProcessorFormatter`).
3. Library records never went through structlog's processors, so the formatter runs the shared steps for them first (`foreign_pre_chain`).
4. Redaction sits in that formatter, after both paths meet, so it covers every line — ours and every library's.
5. Setting up twice must not install two handlers, so the handler is named and replaced, not added.
6. uvicorn's own handlers are removed so its records propagate to ours, and its access log is switched off because ours carries the request ID.
7. JSON when output is not a terminal (`isatty()`), readable colour when it is — one switch, no setting.
8. stdout, because containers collect it and some platforms treat every stderr line as an error.
9. `captureWarnings(True)` sends Python warnings through the same pipeline instead of as raw text.
10. After this, the function has no line whose purpose is unclear — which is the test.

> **Recall:** Why does a naive setup produce two formats? · What does `foreign_pre_chain` exist for? · Why is redaction in the formatter and not in structlog's chain? · What breaks if the handler is not named?

---

## Deferred, deliberately

| Topic | Why it is out |
|---|---|
| Tracing, spans, OpenTelemetry | `02-Observability` — a different data model, not better logging |
| The whole journey from a service to the log store — the platform that runs the service and catches its output, the collector that ships the lines, the log store that keeps them, and Grafana that searches them | its own future folder, next to `Devops/`; this folder stops at the service writing to its output streams |
| Log sampling and rate limiting | a volume problem the society tax agent does not have yet |

---

## Where this lands in the society tax agent

**The starting point, 2026-10-06:** the service's `logging.py`, written when its request IDs and structured logs were added. It is the whole of note 6: `configure_logging()`, `redact_sensitive()`, and `RequestContextMiddleware`, which gives every request an ID and writes one access line.

To be filled in as the notes are written.

---

## Sources to verify against

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html) — the definitions of logging, an event and the five levels, and the teaching order this syllabus follows; and the [logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [structlog documentation](https://www.structlog.org/), especially the Standard Library Logging and Context Variables pages
