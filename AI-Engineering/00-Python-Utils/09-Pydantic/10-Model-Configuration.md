Everything up to this point configures individual **fields**. `model_config` configures the **whole model** — behaviors that apply uniformly across every field, set once via `ConfigDict`:

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        strict=True,
        extra="allow",
        frozen=True,
    )
    ...
```

(`populate_by_name` was already covered in the serialization note — it belongs here mechanically, but its effect is specifically about aliasing.)

## `strict` — turning off type coercion

The type-coercion note showed Pydantic quietly converting `"39"` to `39` for an `int` field. That's convenient by default, but sometimes it's exactly the wrong behavior — a case where receiving the wrong type should be treated as an error, not silently patched over. `strict=True` **disables coercion model-wide**:

```python
model_config = ConfigDict(strict=True)
```

With `strict=True`, `User(age="39", ...)` now fails with `Input should be a valid integer` instead of silently converting. The same flag exists per-field too (`Field(strict=True)`, or the `Strict*` type aliases) for cases where only one or two fields need the stricter behavior rather than the whole model.

## `extra` — what happens to fields the model doesn't declare

By default (`extra="ignore"`), data containing keys the model doesn't declare is accepted, and those **extra keys are silently dropped**. Two other modes change that:

- **`extra="allow"`** — unknown keys are kept and attached to the instance rather than discarded. Useful for forward-compatibility (a producer adds a new field before the consumer's model is updated to expect it) or genuinely dynamic/plugin-style data.
- **`extra="forbid"`** — unknown keys **raise a validation error**. Useful when unexpected fields usually mean a typo or a caller sending the wrong shape entirely, and silent acceptance would hide that bug.

```python
model_config = ConfigDict(extra="allow")

user = User(username="coreyms", email="c@d.com", age=39, notes="a note")
user.notes  # "a note" — kept, even though `notes` isn't a declared field
```

## `validate_assignment` — re-checking fields after creation

The basics note mentioned, as a default to remember rather than rely on: reassigning a field after construction does **not** re-validate by default.

```python
model_config = ConfigDict(validate_assignment=True)

user.email = "not-an-email"  # now raises ValidationError, instead of silently succeeding
```

With this on, every later assignment goes through the same validation machinery construction does. 
> The right call for any model that's **expected to stay valid across its whole lifetime**, not just at the moment it's built — **a config object being adjusted at runtime**, for instance.

## `frozen` — making instances immutable

```python
model_config = ConfigDict(frozen=True)

user.email = "new@example.com"  # raises: instance is frozen
```

`frozen=True` blocks **all** assignment after construction — not **assignment that fails validation** (that's `validate_assignment`'s job) but assignment at all, even to a value that would otherwise be perfectly valid. 

> The right fit for genuinely immutable data — **configuration that shouldn't drift once loaded**, a value object that represents a fixed fact rather than mutable state. 

> As a side effect, **Pydantic can also skip some internal bookkeeping** for a model it knows can never change, which is a **minor performance win** layered on top of the correctness guarantee.

`frozen` and `validate_assignment` solve different problems and can't really substitute for each other: `frozen` says **nothing changes, ever**; `validate_assignment` says **changes are fine, but they have to stay valid**.

---

Between these four flags, `model_config` is where a model's overall **posture** toward its data gets decided — how forgiving it is about types (`strict`), about unknown fields (`extra`), and about being changed at all after creation (`validate_assignment`, `frozen`) — as distinct from what any single field is allowed to contain.
