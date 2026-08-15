A Pydantic model is a class that inherits from `BaseModel`, with fields declared as plain type-annotated class attributes:

```python
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
```

Every field written this way — with no default value — is **required**. Pydantic won't build the object without it.

## Required fields fail loudly, and all at once

```python
user = User()
print(user)
```

![[AI-Engineering/00-Python-Utils/09-Pydantic/Images/02-empty-user-required-field-errors.png]]

Two things are worth noticing in that error. First, `2 validation errors for User` — both missing fields are reported together, not one-at-a-time. Second, the specific error type: `Field required [type=missing, ...]`. Pydantic's errors always carry a machine-readable `type` alongside the human-readable message — useful later when a caller wants to handle *categories* of validation failure programmatically instead of string-matching error text.

## Optional fields — two different meanings of "optional"

There are two distinct things people mean by "optional field," and Pydantic treats them differently.

**A field with a plain default** is optional because a value is supplied automatically when the caller doesn't provide one:

```python
class User(BaseModel):
    username: str
    email: str
    bio: str = ""
    is_active: bool = True
```

Any field with a `= value` after the type hint stops being required. Create a `User` with only `username` and `email`, and `bio` comes back as `""`, `is_active` as `True`.

**A field that's genuinely optional — no sensible default, `None` when absent** needs a union type, not just a bare type hint with `None` as the value:

```python
full_name: str | None = None
```

Writing `full_name: str = None` would be a lie to the type system — it claims the field is *always* a string while handing it a default that isn't one. `str | None` says what's actually true: this field holds a string, or it holds nothing.

## Accessing and modifying fields

A model instance behaves like an ordinary Python object — dot notation reads a field:

```python
print(user.username)  # "coreyms"
```

And by default, an instance is **mutable**, and assignment does **not** re-validate:

```python
user.bio = 123  # a plain BaseModel accepts this silently by default
```

That reassignment succeeds even though `bio` is typed as `str`, because Pydantic only validates on *construction* unless it's explicitly told otherwise . Worth remembering as a default, not a guarantee: changing a field after creation doesn't automatically re-check it.

## Turning a model back into plain data

Two methods cover the common cases:

```python
user.model_dump()        # -> a plain Python dict
user.model_dump_json()   # -> a JSON string
user.model_dump_json(indent=2)  # -> pretty-printed JSON string
```

`model_dump()` is for staying inside Python — passing the data to another function, logging it, comparing it. `model_dump_json()` is for the boundary — writing to a file, sending over HTTP, anywhere a string is actually needed rather than a Python object. Both walk the *entire* model, including nested models and default values, unless told otherwise (see the serialization note for `include`/`exclude`/`by_alias`).

> [!info] These replace `.dict()` and `.json()` from Pydantic V1. If a tutorial or Stack Overflow answer uses those names, it's written against V1.
