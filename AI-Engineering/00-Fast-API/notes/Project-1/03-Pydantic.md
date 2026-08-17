
## What Pydantic actually is

A **Python validation library. That's the entire scope.** Not an ORM, not a web framework, not a database layer — it checks that data matches a declared shape, and does that one job well. It is a separate project with its own release cycle, and FastAPI depends on it directly — so `pip install fastapi` installs Pydantic too, with no extra step and no `[standard]` needed. Separate library, automatic install.

The core idea: declare what shape you **expect** data to be in, once, and get validation against that shape for free everywhere the declaration is used — instead of writing manual checks (`if not isinstance(...)`, `if "id" not in data`) scattered through the code.

---

## The `models.py` convention

The common pattern in a FastAPI project: one `models.py` file per module, holding nothing but Pydantic class definitions. Once one of these classes is understood, the rest read almost identically — only the field names and types change.

```python
from pydantic import BaseModel


class Something(BaseModel):
    id: int
    name: str
    price: float
    is_active: bool
```

A few things worth being precise about:

- **Subclass `BaseModel`.** That inheritance is what turns a plain-looking class into something Pydantic actively validates.
- **Each field is declared with a type annotation** — `int`, `str`, `float`, `bool`, and more. **The annotation isn't just documentation here; it's the actual validation rule.** A field declared `id: int` will reject a value that isn't an integer.
- **No method bodies, no logic.** A model class is just a shape declaration — data in, validated data out.

> [!important] The practical payoff: a typo in a field name, or a value of the wrong type, gets caught automatically — often with the editor's own linter flagging it before the code even runs, since the model's shape is now explicit and machine-readable rather than implied by scattered dictionary access.

---

## Two different jobs a model can do

It's easy to assume there's only one model per **thing** in an app, but two distinct needs show up constantly:

1. **A model for one item's shape** — what does a single record actually look like.
2. **A model for what a whole response looks like** — which is often **not** the same shape as one item. A response commonly wraps a list of items inside some metadata: how many items came back, whether the operation succeeded, and so on.

```python
class SomethingResponse(BaseModel):
    status: str = "success"
    count: int
    items: list[Something]
```

That `status: str = "success"` is a **default value** — if nothing else is specified when the model is built, `status` is automatically `"success"`. Defaults are optional per field; some fields have them, some (like `count` and `items` here) require a value to be provided every time.

The response model's `items` field being `list[Something]` is the connective piece: it says **a list of things shaped like `Something`,** reusing the first model rather than redeclaring its fields a second time.

--- 
### Pydantic-Models-For-The-Menu

The general Pydantic pattern applied to this project's actual data — a `models.py` with the two classes the menu routes will need.

```python
from pydantic import BaseModel


class MenuItem(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: str
    available: bool


class MenuResponse(BaseModel):
    status: str = "success"
    count: int
    items: list[MenuItem]
```

`MenuItem`'s fields are a direct match for `data.py`'s shape from the previous note — `id`, `name`, `category`, `description`, `price`, `available` — because that's exactly the job this class does: declare, formally, the shape the raw dictionaries in `MENU_ITEMS` are already following informally.

`MenuResponse` is the envelope every menu-returning endpoint will send back: a `status`, a `count` of how many items are included, and the `items` themselves as a list of `MenuItem`. Every route that returns menu data — the full list, a filtered-by-category list, even eventually a single item — can reuse this same shape rather than each endpoint inventing its own response format.

That consistency is the actual point: a caller integrating against this API only has to learn one response shape, not a different one per endpoint.
