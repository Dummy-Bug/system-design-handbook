#config #pydantic #pydantic-settings #dotenv #docker #secrets #syllabus

# 12 · Configuration — Syllabus

**6 notes, 56 rungs.** Generic — how a Python service takes its settings from the environment, not one codebase's implementation, which is mapped at the bottom. Deliberately short: this is a thing to get right once and stop thinking about, not a subject to become an expert in.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — a value arrives as a string, therefore something must convert it, therefore the conversion can fail, therefore where it fails decides whether you find out at startup or at 3am. Rungs are not topics and not section headings. Seven to nine of them build one note, except note 1, which follows its two lab halves and runs to seventeen.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.**

**Currency check (2026-09-11), verified by running it on pydantic-settings 2.15.0 and pydantic 2.13.5.** `BaseSettings` no longer lives in `pydantic` — it moved to the separate `pydantic-settings` package, and importing it from the old place raises a `PydanticImportError` that says so. Four behaviours are silent surprises rather than documented gotchas: a key in your `.env` that no field declares is an **error** by default and needs `extra="ignore"`; malformed JSON in a `dict` or `list` field raises `SettingsError`, which is **not** a `ValidationError`, so anything catching config failures must catch both; a `bool` field given an **empty** value is an error rather than false; and a nested settings block reads **its own** file, so redirecting the parent at a different file does not reach the child.

---

## How to teach from this

**One note at a time, one rung at a time.** A rung is taught in the terminal first, and only after a response does that one section get appended to the note — a note is never written in one pass. The ordering is the design — note 6 only lands because the second half of note 1 established which source outranks which.

**Where a rung says break, it is run, not read.** Every note has a lab folder in `~/Desktop/projects/config-lab/src/config_lab/`, `note01/` for note 1 and so on, and the point of the lab is that the outputs quoted in the notes are reproducible rather than taken on faith.

**This is craft, not recall.** Nobody is going to ask you to recite precedence order. The test of whether it landed is whether the next service you set up has one file that says what it needs and refuses to start when it does not.

---

## Note 1 · Declared, Not Fetched

Written up as [[01-Declared-Not-Fetched]].

17 rungs in two halves, in the order of the lab folder `note01/`. **Break:** give it two bad settings at once and count how many each mechanism reports, then call `load_dotenv()`, point a settings class at a different file and watch the first file win.

### First half · the declaration — `a_by_hand.py`, `b_one_problem_at_a_time.py`, `c_declared_same_job.py`, `d_all_errors_at_once.py`

1. A service reads its settings from the environment, and `os.environ` already does that in one line, so the case for anything more has to come from the unhappy path.
2. Reading by hand stops at the first problem — it crashes on the missing value and never discovers the malformed one two lines below it.
3. Each discovery costs a run, and when the run is a container start, that is a deploy.
4. The messages also under-report: `invalid literal for int()` never names the setting it was converting.
5. A settings class inverts the order — everything is read and checked first, then one report lists every problem, each naming its field and what arrived.
6. The `input_value` in that report answers the first question you actually have: did the value never arrive, or arrive malformed.
7. The declaration also carries the contract — name, type, required-or-defaulted — as one readable line per setting, instead of something inferred from `os.environ[x]` versus `.get(x, d)` versus an `int(...)` wrapper.
8. Everything from the environment is a string, so something has to convert it; the annotation does the conversion and names the field when it fails.
9. Which leaves one place that states what the program needs — a property no scattered set of `os.environ` calls can have, however correct each call is.

### Second half · who wins — `e_from_a_dotenv_file.py`, `f_who_wins.py`, `g_load_dotenv_promotes.py`, `h_the_file_that_loses.py`

10. Nobody types a forty-variable command line, so settings move into a `.env` file, which one line of configuration points at.
11. That path resolves from the directory you run in, not from the source file, so the same script works and then mysteriously reports a missing value.
12. A value is now findable in four places, checked in order: constructor argument, real environment variable, the `.env` file, the default in the class.
13. The first match wins and the rest are never consulted.
14. Ranks 2 and 3 are the pair that matters — a real environment variable beats the file.
15. `load_dotenv()` moves values from rank 3 to rank 2 by setting them as real environment variables, and within that process it cannot be undone.
16. Once promoted, pointing settings at a different file cannot dislodge them: the other file is rank 3 and loses silently, producing an answer that looks right and is not.
17. The same ordering is the deploy story — stable settings baked into the image, per-run settings passed in as real environment variables that win without a rebuild.

Rungs 15 and 16 are the `load_dotenv()` promotion, which needs a second environment file — `staging.env` at the lab root.

> **Recall:** Why is the happy path not an argument for either mechanism? · What does `input_value` tell you that `KeyError` cannot? · Where does the contract live in the by-hand version? · Name the four sources in order. · What exactly does `load_dotenv()` change, and why is it invisible? · Why does rank 2 beating rank 3 make containers work rather than break them?

---

## Note 2 · Names And Types

Written up as [[02-Names-And-Types]].

8 rungs. **Break:** rename a field and watch the environment variable it reads change with it.

1. The field name and the environment variable name are two different things, and the library maps between them.
2. The default map is the field name itself, with case ignored — `JWT_SECRET`, `jwt_secret` and `Jwt_Secret` all match — which means renaming a field silently renames the variable your deployment has to set.
3. An explicit alias pins one field to one exact variable name, so renaming the field can no longer move the variable — the same tool you reach for when the variable already exists and cannot be renamed. A `.env` file has a second net: a key no field declares is an error by default, until `extra="ignore"` switches it off. Real environment variables never get that check.
4. A prefix on a block gives a whole group of variables a shared namespace without repeating it on every field.
5. Types are not documentation: `int` converts, and refuses with a message naming the field.
6. `bool` is the one that surprises — `true`, `yes`, `y`, `on`, `t` and `1` are true, `false`, `no`, `off` and `0` are false, and `2`, `enabled` or an **empty value** are errors rather than false.
7. A fixed set of allowed values turns a typo into a startup error that lists the legal ones, which is the cheapest way to make a wrong configuration impossible rather than merely wrong.
8. Structured values arrive as JSON inside a single variable, and they fail in two different places: text that is not JSON at all is refused by the source before any field is checked and raises `SettingsError`, while valid JSON of the wrong shape is refused by the field and raises an ordinary `ValidationError`. `SettingsError` is **not** a `ValidationError`, so anything catching configuration errors has to catch both, or `ValueError`, which is their shared parent.

> **Recall:** What breaks when you rename a field? · Which bool values are errors rather than false? · Why are two exception types involved in one config load?

---

## Note 3 · Refuse To Start

Written up as [[03-Refuse-To-Start]].

8 rungs. **Break:** write a configuration where every value is the right type and the combination is impossible.

1. A type check says each value is the right shape on its own; it cannot say the combination makes sense.
2. Most real configuration errors are combinations — a storage mode selected with no destination, a database URL set with no password.
3. A field-level rule normalises one value before it is checked: trimming, uppercasing, expanding a path.
4. A model-level rule runs after every field is set, and is the only place a rule spanning two fields can live.
5. Writing those rules converts a crash during the first request into a refusal to start, which is the entire value.
6. The refusal has to say what to do rather than what went wrong — name the variable to set, not the field that failed.
7. Some invariants are security rather than correctness: a switch that disables authentication and must be impossible outside development belongs here, refused by the configuration rather than trusted to code review.
8. A named question is the other half of this — `is this configured?` as a property beats every call site re-deriving the same condition out of raw fields and drifting.

> **Recall:** What can a model-level rule express that a type cannot? · What should a refusal message contain? · Why is a named property better than repeating the condition?

---

## Note 4 · Secrets Are Not Config

8 rungs. **Break:** log the whole settings object, then log one secret deliberately, and compare.

1. Configuration and secrets both arrive as environment variables, which is why they get treated as one thing, and their lifecycles are not the same.
2. A secret rotates on its own schedule, has a blast radius when exposed, and must never be printed. A table name has none of those properties.
3. A secret type wraps the value so printing the object, formatting it into a string, or dumping it to JSON all produce a mask.
4. That covers the accidental paths, which are the ones that actually happen: a debug log of the settings object, a traceback, an error reporter, a health endpoint.
5. It does not cover the deliberate path — reading the value out and logging that is still a leak, so the unwrap belongs at the point of use and nowhere else.
6. A `.env` committed to git is permanent: deleting it later removes it from the working tree and leaves it in history.
7. Which makes rotation the only real remedy, and deletion a thing that feels like one.
8. In production the file is usually the wrong mechanism anyway — a secret manager or a mounted file keeps the value out of the image and lets it rotate without a rebuild.

> **Recall:** Which disclosure paths does a secret type close, and which does it not? · Why is deleting a committed secret not a fix?

---

## Note 5 · A Flag Per Capability

8 rungs. **Break:** take a gate written as "not production" and give one non-production environment the feature it was hiding.

1. A service that runs in more than one place needs one setting naming which place, constrained to a fixed set so a typo cannot invent a fifth environment.
2. Everything else branches off that value, which makes it the highest-leverage line in the file.
3. The tempting shape is `if env != "prod"`, and it quietly encodes an assumption: that production is the most capable environment and the rest are reduced copies of it.
4. That assumption is often false — a feature can be running everywhere except production, because production has not adopted it yet.
5. When it is false, every `not prod` gate is inverted, and the failure is invisible in development and total in production.
6. The fix is one flag per capability, named for the capability, so the answer is stated rather than derived from something correlated with it.
7. A flag also covers the case a derived condition cannot express at all: a capability needing no settings of its own has no key whose presence could imply it.
8. Two switches that sound alike are not the same switch, so write down which environments each one covers — the overlap between them is exactly where the misreading happens.

> **Recall:** What assumption is hidden inside `if env != "prod"`? · Why can a flag express something a derived condition cannot?

---

## Note 6 · Baked In Or Passed In

7 rungs. **Break:** change one setting without rebuilding the image.

1. An image is built once and run many times, which splits configuration into what is baked in and what is supplied at start.
2. Baking a file in makes the image self-contained, and makes every change to that file a rebuild.
3. A value passed at run time beats the baked file, because a real environment variable outranks a file.
4. That is the whole pattern: the file carries what is stable, the run carries what varies, and neither has to know about the other.
5. In an orchestrator the run-time half lives outside the repository, in a task definition or a config map, and the repository then cannot tell you what production actually runs.
6. That is the most dangerous sentence in this folder, and the answer to it is a command that prints the resolved configuration from inside the running environment.
7. Checking the configuration before the process starts serving is cheap, and a crash-restart loop is an expensive way to discover a missing variable.

> **Recall:** What decides whether a setting is baked in or passed at start? · Why can the repository stop being the source of truth?

---

## Coverage

Note files are numbered to match this list — note 3 is `03-Refuse-To-Start.md`.

| Note | Rungs | Break |
|---|---|---|
| 1 · Declared, Not Fetched | 17 | two bad settings, count the reports; promote a value, then redirect the file |
| 2 · Names And Types | 8 | rename a field |
| 3 · Refuse To Start | 8 | type-correct and impossible |
| 4 · Secrets Are Not Config | 8 | log the object, then the value |
| 5 · A Flag Per Capability | 8 | invert a "not prod" gate |
| 6 · Baked In Or Passed In | 7 | change a setting without rebuilding |

---

## Deferred

| Topic | Goes to |
|---|---|
| Secret managers, IAM roles, mounted-secret mechanics | `04-AI-Security` — note 4 stops at the boundary |
| Feature-flag services, gradual rollout, targeting | outside this folder; note 5 covers only the deploy-time flag |
| Hot reload and settings that change while running | deliberately out — almost always a restart is correct and simpler |
| Model names, temperatures, prompt versions as configuration | `01-Agent-Evals`, where the versioning question actually belongs |
| Rewriting git history to remove a committed secret | ops work, not configuration design |

---

## Where this lands in Xarvis

**The starting point, 2026-09-11:** one `config.py`, 162 lines, 8 blocks and 39 field declarations, replacing a `load_dotenv()` that ran on any import of anything in the package and pushed every key in the file into the environment.

**The second half of note 1 is the one that was paid for.** The promotion trap invalidated four separate measurements during the migration, each of which looked plausible and was wrong, because an earlier import had already moved one environment's values to rank 2.

**Note 5 is the load-bearing one here.** Three gates were written as `if env not in {"prod"}` on the assumption that production is the most-featured environment, and for the onboarding agent the opposite is true — production is the one deployment without it. That is rung 4 of that note, in this codebase, found by reading rather than by failing.

**Note 4 has a live example.** An authorisation code was being logged at INFO on every real handshake, invisible until the field became a secret type and the log line started printing a mask.

**Note 3 maps onto two rules that now refuse at startup:** a storage mode selected with no table name, and a database URL set with no password. Both were previously crashes on first use.

---

## Sources to verify against

- [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/), source precedence and nested models
- [The Twelve-Factor App — Config](https://12factor.net/config), the original argument for the environment, written in 2011 and predating secret managers
