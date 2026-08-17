A type hint alone only checks **what kind** of value arrived — that an age is an integer, say. It says nothing about whether `-5` or `9000` is a sensible age. Constraints are the layer above type checking: rules about the **range or shape** of an otherwise correctly-typed value.

## The `Annotated` + `Field` pattern

Pydantic V2's recommended way to attach a constraint to a field is Python's `Annotated` type, wrapping the real type and a `Field(...)` call carrying the rule:

```python
from typing import Annotated
from pydantic import BaseModel, Field

class User(BaseModel):
    uid: Annotated[int, Field(gt=0)]
    username: Annotated[str, Field(min_length=3, max_length=20)]
    age: Annotated[int, Field(ge=13, le=130)]
```

`Annotated[int, Field(gt=0)]` reads as: this field's real type is `int`; attached to that type is metadata — here, a constraint saying the value must be greater than zero. The numeric comparison constraints follow the same short names used across the library: `gt` / `ge` (greater-than / greater-than-or-equal) and `lt` / `le` (less-than / less-than-or-equal). String and list-like fields use `min_length` / `max_length` instead.

A constrained instance still gets built by ordinary construction; a violation raises the usual `ValidationError`, and multiple violations across different fields are still reported together:

```python
User(uid=0, username="ab", email="c@d.com", age=12)
```

```
3 validation errors for User
uid
  Input should be greater than 0 
  [type=greater_than, input_value=0, input_type=int]
username
  String should have at least 3 characters 
  [type=string_too_short, input_value='ab', input_type=str]
age
  Input should be greater than or equal to 13 
  [type=greater_than_equal, input_value=12, input_type=int]
```

Same behavior as the earlier type-only errors — every failing field shows up in one error, not three separate round-trips.

## Pattern matching with regex

`Field` also accepts a `pattern` for string fields that need to match a specific shape — a URL slug, for instance:

```python
slug: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]
```

This restricts `slug` to lowercase letters, digits, and hyphens only — the standard shape for a URL-safe identifier. Any character outside that set fails validation.

## Combining constraints

Multiple constraints stack inside the same `Field(...)` call:

```python
title: Annotated[str, Field(min_length=1, max_length=200)]
```

## A naming note for anything written against Pydantic V1

Older code sometimes uses `conint`, `constr`, and similar `con*` helpers (**c**onstrained **int**, **c**onstrained **str**) instead of `Annotated` + `Field`. Those still exist but are deprecated in V2 in favor of the pattern above — a signal, like `.dict()` vs `.model_dump()`, for which version a piece of reference code was written against.
