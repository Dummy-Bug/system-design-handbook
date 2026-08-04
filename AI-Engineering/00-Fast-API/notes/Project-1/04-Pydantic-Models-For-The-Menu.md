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
