Pydantic validates all the standard Python types directly — `str`, `int`, `float`, `bool`, `list`, `dict`, `tuple`, `set`, and the `datetime` family (`datetime`, `date`, `time`, `timedelta`). Three extras are worth knowing before writing a model with any real shape to it: typed containers, `Literal`, and default factories.

## Typed containers

A bare `list` or `dict` only checks that *something list-shaped* arrived — it says nothing about what's inside it. Parameterizing the container checks the contents too:

```python
class BlogPost(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

`list[str]` validates two things at once: that `tags` is a list, *and* that every item in it is a string. A bare `list` would only catch the first.

## Default factories — for defaults that can't be a fixed value

```python
tags: list[str] = Field(default_factory=list)
```

Why not just `tags: list[str] = []`? In plain Python classes, a mutable default (an empty list, dict, etc.) is a well-known trap — that single list object gets shared across every instance, because the default is evaluated once, at class-definition time, not once per instance. `dataclasses` refuses to let you write a mutable default directly for this exact reason and forces `default_factory` instead. Pydantic actually handles the plain-list case safely under the hood, but writing `default_factory=list` is still the pattern worth reaching for by habit, since it generalizes to cases where safety isn't automatic.

The generalization matters for defaults that need to be computed *fresh per instance*, like a creation timestamp:

```python
from datetime import UTC, datetime
from functools import partial

created_at: datetime = Field(default_factory=partial(datetime.now, tz=UTC))
```

`default_factory` must receive an **unexecuted callable** — something Pydantic can call itself, once per instance, at creation time. `default_factory=datetime.now(tz=UTC)` would be wrong: that calls `datetime.now()` immediately, once, while the class body executes, and every instance would then share that same frozen timestamp. `functools.partial(datetime.now, tz=UTC)` builds a new, still-uncalled function — "call `datetime.now` with `tz=UTC` already filled in" — and hands *that* to `default_factory`. A `lambda: datetime.now(tz=UTC)` achieves the identical thing and is the more common way to see it written.

## Union types and `Literal`

A field can accept more than one type:

```python
author_id: str | int
```

A `Literal` field goes further than a type — it restricts the value to a fixed, explicit *set* of values:

```python
from typing import Literal

status: Literal["draft", "published", "archived"] = "draft"
```

Anything outside those three exact strings fails validation. This is the right tool whenever a field's legal values are a known, closed set — states, roles, categories — rather than "any string."

## Type coercion — Pydantic converts when the conversion is unambiguous

```python
class User(BaseModel):
    uid: int
    username: str
    email: str
    age: int

user = User(uid="123", username=None, email=123, age=39)
```

Running this produces:

```
2 validation errors for User
username
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
email
  Input should be a valid string [type=string_type, input_value=123, input_type=int]
```

Only two errors, not three. `uid="123"` — a numeric-looking **string** passed where an `int` is expected — gets silently converted to the integer `123` and passes. `username=None` and `email=123` do **not** get converted, because there's no unambiguous way to turn `None` or `123` into a string that Pydantic is willing to guess at.

> [!important] The direction that gets coerced (string → number) and the direction that doesn't (number → string, `None` → anything) isn't arbitrary. Numeric data arriving as a string is extremely common — form fields, query parameters, JSON, anywhere text is the wire format — so silently accepting `"39"` for an `age: int` field removes friction from a case that's ubiquitous and safe. Going the other way — accepting an `int` where a `str` was declared — has no equivalent "this is obviously fine" case, so Pydantic doesn't guess. If this default coercion is ever the wrong behavior for a field, `strict=True` (per-field or model-wide) turns it off — covered in the model-configuration note.
