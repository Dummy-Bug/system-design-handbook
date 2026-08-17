`model_dump()` and `model_dump_json()` cover the simple case — dump everything, using the Python field names as-is. Real integration points rarely stay that simple: an external API might use different field names than the Python code does, some fields shouldn't be serialized at all, and incoming data might arrive as a JSON string rather than a Python dict.

## Aliases — different names on the wire vs. in Python

`id` is a poor Python attribute name — it shadows a Python built-in. The common fix is a differently-named Python field with an **alias** **pointing at the external name**:

```python
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    uid: UUID = Field(alias="id", default_factory=uuid4)
```

> With just `alias="id"` and no further configuration, the model would accept `id` on input but **reject** `uid` — **the Python name stops working as an input key once an alias is declared, by default**. 
> `populate_by_name=True` in `model_config` restores the Python name as a valid input key **alongside** the alias, so both `User(id=...)` and `User(uid=...)` work:

```python
user = User.model_validate({"id": "3bc4bf25-...", ...})
```

Output, by default, still uses the **Python field name** (`uid`), not the alias — aliasing only affects input unless told otherwise:

```python
user.model_dump_json()          # {"uid": "3bc4bf25-...", ...}
user.model_dump_json(by_alias=True)  # {"id": "3bc4bf25-...", ...}
```

>`by_alias=True` on the dump call switches output to the alias names too — **the** **setting needed when the data is heading back out to whatever system expects** `id` rather than `uid`, like a frontend or an external API.

## `include` and `exclude` — controlling which fields serialize

Sometimes a field genuinely shouldn't leave the process — even with `SecretStr` already masking a password's **value**, sometimes the key shouldn't appear in the output at all:

```python
user.model_dump(exclude={"password"})
```

The inverse — allow-listing instead of block-listing — uses `include`:

```python
user.model_dump(include={"username", "email"})
```

> `include` is the better choice when the safe set is small and known (send back only these two fields); 
> `exclude` is better when almost everything should go out and only a specific field or two needs holding back. 

> Both accept nested paths too, e.g. `exclude={"address": {"pin_code"}}` to drop just one field inside a nested model.

## Loading from a JSON string directly

Data doesn't always arrive as a Python dict — an API request body or a line read from a file is a raw JSON **string**. `model_validate_json()` parses and validates in one step, without a manual `json.loads()` first:

```python
import json

user = User.model_validate_json(json.dumps(user_data))
```

Equivalent to `User.model_validate(json.loads(raw_json_string))`, just without the intermediate `json.loads()` call written out separately.
