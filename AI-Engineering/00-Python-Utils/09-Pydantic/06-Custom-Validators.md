Built-in types and `Field` constraints cover generic shapes — a string of a certain length, a number in a certain range. They can't express rules specific to *this* application's business logic: usernames that must be alphanumeric, a URL that should be auto-corrected rather than rejected, a password-confirmation field that has to match another field. Pydantic covers that gap with two decorators: `field_validator` for a single field, `model_validator` for logic that spans more than one.

## `field_validator` — custom logic for one field

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):

    username: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric '_' allowed")
        return v.lower()
```

A few mechanical things to hold onto here:

- The decorator takes the **field name as a string** — `@field_validator("username")` — telling Pydantic which field this method validates.
- The method must also be a `@classmethod` — it receives the class (`cls`), not `self`, because at the point this runs the full instance doesn't exist yet.
- It receives the field's value as `v`, and **must return a value** — either the original `v` unchanged, or a transformed version of it. Whatever it returns becomes the field's final value.
- To reject the value, `raise ValueError(...)` — Pydantic catches that and folds it into the normal `ValidationError` machinery automatically. Nothing distinguishes a `ValueError` raised here from a built-in validation failure in the resulting error.

`User(username="Corey_Schafer")` passes the alphanumeric check and comes back with `username='corey_schafer'` — validation and normalization happening in the same step, since the method both checks *and* transforms the value it returns.

## `mode="before"` vs `mode="after"` — which value the validator actually sees

By default, a `field_validator` runs in `mode="after"` — **after** Pydantic has already done its own type-checking and coercion on the raw input. That's the right choice most of the time, but it means the validator can't repair a value that would fail type validation *before* the validator ever gets a chance to run.

```python
from pydantic import BaseModel, HttpUrl, field_validator

class User(BaseModel):
    website: HttpUrl | None = None

    @field_validator("website", mode="before")
    @classmethod
    def add_https(cls, v):
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v
```

`website="coreyms.com"` has no scheme, so `HttpUrl`'s own validation would reject it outright. With `mode="before"`, this validator runs **first**, on the raw, not-yet-validated string — it can still see and prepend to a bare `"coreyms.com"` before `HttpUrl` ever gets to judge it. Running the same fix as `mode="after"` (the default) wouldn't work: by the time it ran, `HttpUrl`'s own check would already have failed and raised.

> [!important] `mode="before"` trades type safety for a chance to repair the input. The value the validator receives hasn't been checked or converted yet — it could be any type at all, not necessarily the one declared on the field. 

> Reach for `before` specifically when the validator's job is to *normalize a raw, possibly-malformed input* into something the field's real type can then validate. 
> Reach for the default `after` (or don't specify a mode) whenever the validator's job is to check or transform an already-correctly-typed value, which is the more common case.

## `model_validator` — logic that spans more than one field

A validation rule that depends on *more than one field at once* — a password and its confirmation, an age that changes what other fields are required — can't be expressed as a `field_validator`, because a `field_validator` only ever sees the one field it's attached to.

```python
from pydantic import BaseModel, model_validator

class UserRegistration(BaseModel):
    email: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegistration":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
```

The shape here is different from `field_validator` in a way that matters: 

* no field name in the decorator (it applies to the whole model, not one field), 
* no `@classmethod` and 
* the method receives `self` — **the fully-built instance**, with every field already individually validated — rather than a single raw value. 

> `mode="after"` (validate individual fields first, then check them together) is what makes that possible; 

> `model_validator(mode="before")` exists too, receiving the raw input dict before any field has been validated, for cases that need to intervene earlier.

`UserRegistration(email="a@b.com", password="secret123", confirm_password="secret456")` raises:

```
1 validation error for UserRegistration
  Value error, Passwords do not match [type=value_error, ...]
```

## Two habits worth keeping

- **Always return the value**, even when the validator doesn't need to change it — a validator that raises or returns is complete; one that falls through without either is a bug.
- **Don't mutate and then raise.** Pick one: either return the corrected/normalized value, or raise an error describing what's wrong — not both in the same call.
