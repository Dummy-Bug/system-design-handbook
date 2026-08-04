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

## Why `cls`, not `self` — a level deeper

`self` is not magic — it's just the first argument of an instance method, filled in automatically with **whatever object the method was called on**. `obj.some_method()` is really shorthand for `SomeClass.some_method(obj)`: Python hands the object in as the first argument. For that to work at all, `obj` has to already exist as a real thing sitting in memory.

A field validator runs at the exact moment Pydantic is still deciding whether raw incoming data is even allowed to *become* an attribute on a real object. When `validate_code` runs, there is no `self.code` to check yet — that's literally the question being answered. Pydantic validates the incoming values first, and only assembles the actual model instance once everything has passed. There is often no instance at all yet, not even a partially-built one.

> [!question]- A concrete image: filling out a form vs. holding an ID card
> An instance method is something you can only do **with an ID card already in hand** — `self` is the ID card, already issued, already real. A field validator runs at the stage where you're still filling out the *application form*. The office reviewing your form isn't checking your ID card's photo, because you don't have one yet — that's what's being decided. What the office *does* have, reliably, the whole time, is their **rulebook** — the class itself, which existed the moment the code defining the class was loaded, long before this particular piece of data ever showed up. `cls` is a reference to that rulebook, not to your not-yet-issued ID.

**Why `cls` at all, if it usually goes unused?** `@classmethod` isn't a Pydantic invention — it's a general Python mechanism, and Pydantic just requires validators to follow its contract. Under the hood, `@classmethod` works through a descriptor protocol: when the method is looked up, Python automatically supplies the *class* as the first argument, no matter when or how it's called — a class object exists the moment its `class` block finishes executing, independent of any particular instance's lifecycle. So `cls` is guaranteed to be valid at validation time in a way `self` fundamentally cannot be.

`cls` going unused most of the time doesn't make it pointless — it exists for when it's needed: calling another classmethod on the same class, referencing a class-level constant, or — especially relevant under inheritance — resolving to whichever **subclass** actually gets used, rather than hardcoding the base class's name. If this class were subclassed later, `cls` inside an inherited validator would correctly refer to the subclass; a hardcoded class name never could.

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

---

## The limit of `field_validator`: it only ever sees one field

`@field_validator("code")` receives *exactly* the data submitted for `code` — nothing about any other field on the same model is reachable through its normal parameters. That's a real limitation, not an oversight: the string passed to the decorator is what determines which field's data gets handed in, and there is no way to name two fields at once.

If logic genuinely needs to compare two fields against each other — say, a `name` field constraining what a `pin_code` field is allowed to be — there are two real tools for it:

**Option 1 — a third `info` parameter, if the other field was declared earlier in the class:**

```python
from pydantic import BaseModel, field_validator, ValidationInfo

class Something(BaseModel):
    name: str
    pin_code: str

    @field_validator("pin_code")
    @classmethod
    def validate_pin_code(cls, value: str, info: ValidationInfo) -> str:
        name = info.data.get("name")
        if name and name.startswith("Test") and value != "000000":
            raise ValueError("Test entries must use pin_code 000000")
        return value
```

`info.data` is a dict of whatever fields were **already validated before this one** — which is why `name` has to be declared *above* `pin_code` in the class for this to work at all. Fields validate top-to-bottom; a field can only see the ones that came before it, never ones declared after.

**Option 2 — `@model_validator`, the more common tool for genuine cross-field checks:**

```python
from pydantic import model_validator

class Something(BaseModel):
    name: str
    pin_code: str

    @model_validator(mode="after")
    def check_together(self) -> "Something":
        if self.name.startswith("Test") and self.pin_code != "000000":
            raise ValueError("Test entries must use pin_code 000000")
        return self
```

This one takes `self`, not `cls` — because with `mode="after"`, every individual field has already validated and a real instance genuinely exists by the time this runs, so it behaves like an ordinary method, with every field reachable by name, regardless of declaration order.

> [!note] The practical rule: `field_validator` for checking one field in isolation (exactly the cases in this note so far). The moment validation logic needs to compare fields against each other, that's the signal to reach for `model_validator` instead — it's the tool actually designed for that job, rather than working around `field_validator`'s single-field scope.
