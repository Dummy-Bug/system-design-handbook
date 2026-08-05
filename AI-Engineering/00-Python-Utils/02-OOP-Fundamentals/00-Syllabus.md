#python #oop #classes #python-utils #syllabus

# 02 · OOP Fundamentals — Syllabus

17 concepts. **Generic** — Python's object model, not any framework's use of it.

> The temptation here is to skip straight to "the bits Pydantic needs." Don't. The descriptor protocol and `__init_subclass__` are what make `BaseModel` possible at all, and "how does Pydantic actually work?" is a real interview question with a real answer.

**Why this sits second:** `class User(BaseModel)` is inheritance. `@field_validator` **requires** `@classmethod` and the Pydantic notes had to state that as a rule without being able to explain it. `@computed_field` stacks on `@property`. Every one of those is unexplained machinery until this folder exists.

**Currency check (2026-08-04):** this is the most stable area in the language — the object model has barely moved in a decade. Two things worth confirming against current docs: `@override` (3.12+) for making an intended override checkable, and the `dataclasses` feature set, which has grown steadily (`slots=`, `kw_only=`).

---

## A · Classes and instances

**1. Class vs instance — and what `self` actually is**
`self` is not a keyword; it's the first positional parameter, filled in by the binding machinery. Understanding this is what makes `@classmethod` and `@staticmethod` obvious rather than memorised.

**2. `__init__` and object construction**
`__new__` vs `__init__`, and why the split exists (relevant later — Pydantic's construction path is not a plain `__init__`).

**3. Class attributes vs instance attributes**
Where a value lives, the lookup order, and the classic mutable-class-attribute-shared-across-instances bug — the same shape as the mutable-default trap in the Pydantic `default_factory` note.

**4. Instance methods, `@classmethod`, `@staticmethod`**
Three binding behaviours: receives the instance, receives the class, receives neither. **This is the concept the Pydantic notes owed an explanation for** — `field_validator` runs before an instance exists, so it can only be handed the class.

**5. `@property` and computed attributes**
Method that reads as an attribute. Getters, setters, deleters. Directly underneath `@computed_field`.

## B · Inheritance and composition

**6. Single inheritance and `super()`**
What `super()` resolves to and why bare `super()` works in 3.x.

**7. Multiple inheritance and the MRO**
C3 linearisation, `__mro__`, and cooperative `super()` calls. Mixins as the sane use of multiple inheritance.

**8. Composition vs inheritance**
When "has-a" beats "is-a". The nested-models pattern from the Pydantic notes is composition — worth naming as such.

**9. Abstract base classes**
`abc.ABC`, `@abstractmethod`, and enforcing an interface at instantiation time. Then the comparison that matters: **ABC (nominal — you must inherit) vs `Protocol` (structural — you must merely match)**, closing the loop with folder 01.

## C · The data-holding classes

**10. `__repr__` vs `__str__`**
Which one `print()` uses, which one the REPL uses, and why every class worth debugging defines `__repr__`.

**11. Dunder methods and operator overloading**
`__eq__`, `__hash__`, `__len__`, `__getitem__`, `__contains__`, `__call__`. The `__eq__`/`__hash__` contract and why defining one without the other breaks dicts and sets.

**12. `dataclasses`**
`@dataclass`, `field(default_factory=...)`, `frozen=`, `slots=`, `kw_only=`. **The direct comparison to hold onto:** a dataclass gives you the same clean declarative syntax as a Pydantic model and does *no runtime validation whatsoever*. That contrast is the cleanest one-sentence answer to "why Pydantic instead of a dataclass?"

**13. `Enum`**
`Enum`, `StrEnum`, `IntEnum`, `auto()`. The natural home for a closed set of states — and the runtime counterpart to `Literal` from folder 01.

**14. `NamedTuple` and `namedtuple`**
Lightweight immutable records, and where they still beat both dataclasses and models.

## D · The machinery underneath

**15. The descriptor protocol**
`__get__`, `__set__`, `__set_name__`. **`@property`, `@classmethod`, and `@staticmethod` are all descriptors** — this is the layer where "how does that decorator actually change attribute access?" gets answered.

**16. `__slots__`**
Trading dynamic attributes for memory and speed. Why it matters when you're holding a million small objects in a pipeline.

**17. `__init_subclass__` and a look at metaclasses**
How a base class can run code every time it's subclassed — which is, in essence, how `BaseModel` collects annotations and builds a validator the moment you define a model. Enough to answer *"how does Pydantic actually work?"* without pretending to be a metaclass expert.

---

## Deferred

| Topic | Goes to |
|---|---|
| `Protocol` as a typing construct | 01 (written) |
| Decorator mechanics — how `@property` is implemented | 03 |
| `__enter__` / `__exit__` | 05 |
| Exception class hierarchies | 06 |

## Where this already shows up in these notes

`09-Pydantic/02` inherits from `BaseModel`; `/06` states the `@classmethod` requirement as an unexplained rule; `/07` stacks `@computed_field` on `@property`. `00-Fast-API` defines custom exception classes. All of it currently rests on rules rather than reasons.

## Interview hooks

Two questions this folder is the answer to: *"why does `field_validator` need `@classmethod`?"* and *"what does Pydantic give you that a dataclass doesn't?"* Both are cheap to ask and quickly separate use-it-from-a-tutorial from understand-it.

## Sources to verify against

- [Python Data Model](https://docs.python.org/3/reference/datamodel.html) — the authoritative reference for every dunder here
- [Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html) — the best explanation of concept 15 that exists
- [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) · [`enum`](https://docs.python.org/3/library/enum.html) · [`abc`](https://docs.python.org/3/library/abc.html)
