#python #type-hints #typing #typeddict #python-utils


A dictionary used as a record — fixed keys, each holding a different kind of value — is something the ordinary container syntax cannot describe. `TypedDict` is the thing that can.

## The hole left by `dict[str, ...]`

A user record annotated as accurately as `dict` allows:

```python
type User = dict[str, str | int | None]

def create_user(first_name: str, age: int | None = None) -> User:
    str_age = str(age)
    return {'first_name': first_name, 'age': str_age}
```

The age was converted to a string somewhere in the middle — the sort of thing that arrives via a refactor, or a copy-paste, or a helper that stringifies everything.

```
Success: no issues found in 1 source file
```

Nothing caught. And the annotation isn't wrong: it says **every value is a string, a number, or nothing**, and a string satisfies that. The type is being obeyed exactly as written.

The problem is what it can express. `dict[K, V]` describes a mapping where **all values are alike** — a phone book, a word-count, a cache. A user record is not that. Its values are deliberately different from each other, and the one guarantee you want — **the thing under `'age'` is a number** — is the one guarantee this syntax has no way to state.

## Typing each key separately

```python
from typing import TypedDict

class User(TypedDict):
    first_name: str
    age: int | None
```

Same code as before, same bug:

```python
def create_user(first_name: str, age: int | None = None) -> User:
    str_age = str(age)
    return {'first_name': first_name, 'age': str_age}
```

```
error: Incompatible types (expression has type "str",
TypedDict item "age" has type "int | None")  [typeddict-item]
```

Caught, and the message names the key. The difference is not that `TypedDict` is stricter in general — it's that it can finally say **which** key holds **what**, so the checker has a specific claim to test the value against.

## It really is a dictionary

The `class` keyword makes this look like something heavier than it is:

```python
u = User(first_name='Corey', age=38)

print(u)                        # {'first_name': 'Corey', 'age': 38}
print(type(u).__name__)         # dict
print(isinstance(u, dict))      # True
print(u['first_name'])          # Corey
```

At runtime it is **an ordinary dict**. No class is created, no instance, no methods, no validation. `User(...)` builds a plain dictionary and hands it back; `type(u)` says `dict` because that is genuinely all it is. You subscript it with `u['age']`, not `u.age`.

So the `class` block is a **description**, read by the checker and ignored by everything else. Which also means:

> [!warning] `TypedDict` cannot check anything at runtime. Data arriving from an API, a JSON file, or a request body will happily be the wrong shape and nothing will notice — `TypedDict` only constrains code the checker can see. For data crossing into your program from outside, you need something that inspects values while running.

## Where it fits among the alternatives

Once a record can be described several ways, the choice needs making on purpose:

| | Access | Runtime cost | Methods | Checks incoming data |
|---|---|---|---|---|
| `dict[str, ...]` | `d['k']` | none | no | no |
| `TypedDict` | `d['k']` | none | no | no |
| `@dataclass` | `d.k` | a real object | yes | no |
| Pydantic `BaseModel` | `d.k` | a real object | yes | **yes** |

The deciding question is **where the data comes from**:

- Already a dictionary — a JSON payload you're passing through, a row from a driver that returns dicts, a config blob — then `TypedDict` describes what you already have without forcing you to convert it. That is the case it was built for.
- Something you're constructing yourself, that would benefit from methods or attribute access, then a `dataclass` is the better object.
- Anything arriving from outside your program, where being wrong is a real possibility rather than a typo — then you want validation, and neither of the first two provides it.

> [!tip] `TypedDict` is the low-friction option precisely because it changes nothing at runtime. Adding it to an existing codebase full of dictionaries is a pure annotation — no call sites change, no data is converted, nothing gets slower. That makes it the natural first move on legacy code, and a `dataclass` the natural choice for code you're writing fresh.
