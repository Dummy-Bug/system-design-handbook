A plain type annotation (`pin_code: str`) validates *shape* — is this a string at all — but says nothing about *content*. "Exactly 6 characters, all digits" isn't something a type hint alone can express. That's what a **field validator** is for.

---

## The pattern

```python
from pydantic import BaseModel, field_validator


class Request(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if len(value) != 6 or not value.isdigit():
            raise ValueError("Code must be exactly 6 digits")
        return value
```

Piece by piece:

- **`@field_validator("code")`** — a decorator naming exactly which field this validator runs against. The string has to match the field name on the class.
- **`@classmethod` stacked underneath it** — field validators are written as class methods, not instance methods, because they run *during* construction of the object, before there's a fully-built instance to call a normal method on.
- **The method signature is `(cls, value)`** — `cls` is the class itself (standard for any classmethod), `value` is whatever was passed in for that field, prior to this validator running.
- **Custom logic goes in the body**, checking whatever the plain type annotation couldn't express on its own.
- **Failure is signaled by `raise ValueError(...)`** — not a custom exception, not `HTTPException`. Pydantic specifically watches for `ValueError` (along with `TypeError` and `AssertionError`) raised inside a validator, and converts it automatically into its own structured validation-error format. This is the same mechanism already responsible for the automatic `422` response whenever incoming request data fails to match a model's shape — a field validator's `ValueError` plugs into that exact pipeline, rather than requiring anything to be written by hand to produce the error response.

> [!important] **The value has to be `return`ed at the end.** Skipping this isn't a silent no-op — whatever the validator was supposed to check gets validated, but the field's value is lost, because the validator's return value is what Pydantic actually keeps as the field's final value. A validator that checks everything correctly but forgets to `return value` still breaks the model.

---

## The same pattern on a list field

Nothing about this changes when the field being validated is a list instead of a single value — the method just receives (and must return) the whole list:

```python
class BulkRequest(BaseModel):
    codes: list[str]

    @field_validator("codes")
    @classmethod
    def validate_codes(cls, values: list[str]) -> list[str]:
        if len(values) == 0:
            raise ValueError("At least one code is required")
        if len(values) > 20:
            raise ValueError("Maximum 20 codes allowed per request")

        for code in values:
            if len(code) != 6 or not code.isdigit():
                raise ValueError("Each code must be exactly 6 digits")

        return values
```

Three separate checks, any one of which can fail the whole request: empty list, too-large list, and then the same per-item shape check as before, run inside a loop over every element. The parameter is conventionally named `values` (plural) rather than `value` here purely for readability — nothing enforces that naming, it's just a hint to whoever reads it later that this field holds many items, not one.
