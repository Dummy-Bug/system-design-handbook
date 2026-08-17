#python #pydantic #validation #structured-outputs #python-utils #syllabus

# 09 · Pydantic — Syllabus

24 concepts. **Generic** — the library's own surface, not FastAPI's or LangGraph's slice of it.

> Same ordering discipline as folder 08: ten notes already existed, so the concept list was derived from the library first and the notes checked off afterwards. The result is worth reading before anything else here. The written notes cover **defining a model and validating input into it** thoroughly — and cover almost nothing of the direction that actually matters for agent work: **getting a schema back out.** `model_json_schema()`, discriminated unions, and `TypeAdapter` are the mechanism behind every structured LLM output and every tool definition, and none of the three has a note.

**Why this sits ninth.** It's the payoff folder. Pydantic is **type hints, enforced at runtime** — so it needs 01 for `Annotated`, `Literal`, and unions; 02 for what a class and a descriptor are; 03 for what a decorator is; and 06 for exceptions, since a `ValidationError` is the primary thing it produces. Reading it earlier works, but every mechanism arrives as magic.

**Currency check (2026-08-05):** this machine runs Pydantic **2.11.3** on Python 3.13.3; verify against current 2.x before relying on version-sensitive claims. Everything here is **V2** — V1 reached end of life and its API differs enough that a V1 answer in an interview reads as stale. The renames that still catch people: `.dict()` → `model_dump()`, `.json()` → `model_dump_json()`, `parse_obj()` → `model_validate()`, `@validator` → `@field_validator`, `@root_validator` → `@model_validator`, `class Config` → `model_config = ConfigDict(...)`, `allow_mutation=False` → `frozen=True`, and the constraint keywords `min_items`/`max_items` → `min_length`/`max_length`. Worth re-verifying: the `Optional`/default interaction, the current status of `pydantic-settings` as a separate package (**not installed here**), and how PEP 649 deferred annotations in 3.14 change runtime introspection — Pydantic reads annotations at runtime, so that change lands squarely on this library.

---

## A · The core idea

**1. What Pydantic actually is**
Annotations are inert metadata; Python enforces nothing. Pydantic is a library that **chooses to read them at runtime** and enforce them itself. Every other concept here is a consequence. The comparison worth making once by hand: the same validation written manually is dozens of lines of `isinstance` checks with error messages you invented.

**2. Defining a model**
`BaseModel` with type-annotated class attributes. Required vs optional, and the distinction that trips everyone: **optional** meaning has-a-default* is not **optional** meaning can-be-`None`*. All four combinations are expressible and mean different things.

**3. The validation entry points**
`Model(**data)`, `model_validate(obj)`, `model_validate_json(str)` — and why the JSON one is not merely `json.loads` followed by the dict one. Parsing and validating in a single pass in Rust is measurably faster and produces better errors.

## B · Types and coercion

**4. Standard types and containers**
The primitives, the `datetime` family, and typed containers — `list[str]`, `dict[str, int]`, `set`, `tuple`. What a container annotation asserts about every element, and the cost of that assertion on a large payload.

**5. Coercion — the thing that surprises people**
`'38'` becomes `38` by default, and that is usually correct: an HTTP query string, a CSV cell, and a form field are all text. Where it is **not** correct, and how the default lax mode differs from strict mode.

**6. Defaults, and `default_factory`**
Why a mutable default is a bug in plain Python and how `default_factory` sidesteps it — the same **hand over the function, not the result** shape as folder 03's opening note.

**7. Domain types**
`EmailStr`, `HttpUrl`, `SecretStr`, `UUID`, `IPvAnyAddress` — validation with real-world knowledge baked in, and the extras that must be installed for some of them. `SecretStr` in particular is a logging-safety tool, not a typing one.

## C · Rules beyond the type

**8. Constraints — `Annotated` + `Field`**
`Annotated[int, Field(ge=0, le=130)]`. The type says **what kind**; the constraint says **what range or shape**. `-5` is a perfectly good `int` and a nonsense age — that gap is the entire reason this layer exists. The `Annotated` mechanism itself belongs to 01.

**9. `field_validator`**
Custom logic for one field, when no built-in constraint expresses the rule.

**10. `mode="before"` vs `mode="after"`**
Which value the validator actually receives — the raw input, or the already-coerced typed value. Gets picked by coin-flip until you've been bitten once: `before` for cleaning up input you don't control, `after` for business rules over a value you can trust the type of.

**11. `model_validator`**
Rules spanning more than one field — password confirmation, **end date must follow start date**, mutually exclusive options. Nothing per-field can express these.

**12. Computed fields**
Values **derived** from other fields, that the caller never supplies and that still appear in the output. The runtime-serialization counterpart to `@property` from folder 02.

## D · Composition

**13. Nested models**
A field whose type is another model. Validation recurses, so a malformed comment 3 levels down produces an error that names the path to it rather than a generic failure.

**14. Recursive models and forward references**
A `Comment` containing a `list[Comment]`; a `Node` pointing at a `Node`. Quoted annotations, `model_rebuild()`, and the errors you get when the reference can't be resolved yet.

**15. Discriminated unions**
`Field(discriminator='type')` — a union where one field decides which member to validate against. **The single most agent-relevant concept in this folder and currently unwritten:** it is how a tool-call payload gets routed to the right schema, how an LLM's `{"action": ...}` response is validated into exactly one of eight shapes, and how LangGraph state carrying heterogeneous events stays typed. Without it, a union is tried member-by-member and the errors are unreadable.

**16. Generic models**
A model parameterised by a type — `Response[User]`, `Page[Document]`. The pattern behind every typed API envelope.

## E · Getting data back out

**17. `model_dump` and `model_dump_json`**
Back to a dict or a JSON string. `mode='python'` vs `mode='json'` and why the difference matters the moment a `datetime` or a `UUID` is involved.

**18. `include`, `exclude`, and friends**
Choosing which fields serialize. `exclude_none`, `exclude_unset`, `exclude_defaults` — three distinct meanings of **leave it out**, and `exclude_unset` is the one that makes a PATCH endpoint correct.

**19. Aliases**
Different names on the wire than in Python — `validation_alias`, `serialization_alias`, `alias_generator` for camelCase boundaries, and `populate_by_name` for accepting both.

**20. Custom serializers**
`@field_serializer` and `@model_serializer` — the output-side mirror of validators, for when the stored representation and the transmitted one differ.

## F · The wider API

**21. `model_config`**
Whole-model behaviour set once via `ConfigDict`: `strict`, `extra` (ignore / forbid / allow), `validate_assignment`, `frozen`. `extra='forbid'` is the one worth a deliberate decision — silently dropping an unrecognised field is how a typo'd config key costs an afternoon.

**22. `TypeAdapter` and `validate_call`**
Validation without a `BaseModel` at all: `TypeAdapter(list[User])` validates a bare list, `TypeAdapter(int)` a bare int, and `@validate_call` validates an ordinary function's arguments from its annotations. The escape hatch for everything that isn't shaped like a model — and the thing to reach for instead of wrapping a list in a pointless one-field wrapper model.

**23. JSON Schema generation**
`model_json_schema()`. Pydantic's least-appreciated half: the model definition is also a **schema definition**, and that schema is what FastAPI turns into OpenAPI docs, what gets handed to an LLM as a tool definition, and what constrains a structured-output call. Includes what doesn't round-trip cleanly, and how `Field(description=...)` becomes the text the model actually reads when choosing a tool.

**24. `ValidationError` — reading it and shaping it**
`.errors()` returns structured dicts: location path, error type, input value, message. Machine-readable by design, which is what makes the retry loop possible — **feed the validation error back to the model and ask it to fix its own output.** Plus `.json()`, custom messages, and how many errors you get back at once.

---

## Coverage — what is written and what is not

The ten existing notes were numbered in **writing order**, before this syllabus existed; file numbers do not match concept numbers and are not being renamed.

| # | Concept | Note |
|---|---|---|
| 1 | What Pydantic is | `01-Why-Pydantic` |
| 2 | Defining a model | `02-Basic-Models-And-Fields` |
| 3 | Validation entry points | partial — `02`, `09` |
| 4 | Standard types and containers | `03-Standard-Types…` |
| 5 | Coercion | `03-Standard-Types…`, `10-Model-Configuration` |
| 6 | Defaults and `default_factory` | `03-Standard-Types…` |
| 7 | Domain types | `05-Special-Types` |
| 8 | Constraints via `Annotated` + `Field` | `04-Constraints…` |
| 9 | `field_validator` | `06-Custom-Validators` |
| 10 | `before` vs `after` | `06-Custom-Validators` |
| 11 | `model_validator` | `06-Custom-Validators` |
| 12 | Computed fields | `07-Computed-Fields` |
| 13 | Nested models | `08-Nested-Models` |
| 14 | Recursive and forward references | — |
| 15 | **Discriminated unions** | — |
| 16 | Generic models | — |
| 17 | `model_dump` / `model_dump_json` | `02`, `09` |
| 18 | `include` / `exclude` | `09-Serialization-And-Aliasing` |
| 19 | Aliases | `09-Serialization-And-Aliasing` |
| 20 | Custom serializers | — |
| 21 | `model_config` | `10-Model-Configuration` |
| 22 | **`TypeAdapter` / `validate_call`** | partial — `01-Type-Hints/01` covers `validate_call` |
| 23 | **JSON Schema generation** | — |
| 24 | **`ValidationError` structure** | — |

**16 of 24 written**, and the shape of the gap is the point: everything on the **input** side is covered, and four of the five gaps are on the **output** side — schema generation, discriminated routing, adapters, and machine-readable errors. Those four are precisely the ones that make Pydantic an agent-engineering tool rather than a form-validation tool. Concepts **15, 22, 23, 24** are the priority if this folder gets touched again.

One more absence worth naming: `pydantic-settings` / `BaseSettings` is not on this list. Configuration-from-environment is a real and commonly-asked use, but it is a separate package (and not installed here), so it belongs with deployment rather than with the library surface.

## Deferred

| Topic | Goes to |
|---|---|
| `Annotated`, `Literal`, unions, `TypedDict` as typing constructs | 01 (written) |
| `dataclass` vs `BaseModel`, descriptors, `@property` | 02 |
| How the `@field_validator` decorator works underneath | 03 (written) |
| `ValidationError` in the exception hierarchy; API error boundaries | 06 |
| `pydantic-settings` / `BaseSettings` | outside this vault — deployment |
| FastAPI request/response models, dependency injection | `00-Fast-API` (written) |
| Using schemas to constrain LLM output in practice | outside this vault — `01-Agent-Evals`, agent work |

## Where this already shows up

`00-Fast-API` — request and response models throughout; the OpenAPI docs those routes generate are concept 23 happening invisibly. Xarvis — tool argument schemas are Pydantic, and the LangGraph state objects are typed structures whose validation errors surface at exactly the points concept 24 describes. `01-Type-Hints/01` already covers `validate_call`, strict mode, and `Field(ge=, le=)` from the typing side.

## Interview hooks

Sarvam names Pydantic in three separate places, and every one of them is about the **output** side: **strict structured outputs via Pydantic, JSON Schema, or grammar-guided decoding, to guarantee deterministic payload formatting during function calls**; **structured schema enforcement** under agent orchestration; and Week 6 — **enforce payload validation with Pydantic v2** on a custom MCP server. The question that separates people: **how do you guarantee an LLM returns valid JSON?** — where the full answer is schema → constrained generation → validate → **feed the `ValidationError` back and retry**, and the last step is concept 24.

## Sources to verify against

- [Pydantic V2 documentation](https://docs.pydantic.dev/latest/) — the **Concepts** section maps closely to sections B–F above
- [Migration guide, V1 → V2](https://docs.pydantic.dev/latest/migration/) — for the rename table in the currency check
- [JSON Schema documentation](https://docs.pydantic.dev/latest/concepts/json_schema/), for concept 23
- [PEP 593 — `Annotated`](https://peps.python.org/pep-0593/), the mechanism concept 8 rests on
