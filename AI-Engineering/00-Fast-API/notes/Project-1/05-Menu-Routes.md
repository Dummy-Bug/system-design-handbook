Everything built so far — the data, the models, query and path parameter declarations, `response_model`, `HTTPException` — comes together into the two routes the client actually asked for.

---

## `GET /menu` — the full menu, or a filtered slice of it

```python
from fastapi import FastAPI, Query, HTTPException
from data import MENU_ITEMS
from models import MenuItem, MenuResponse

app = FastAPI()


@app.get("/menu", response_model=MenuResponse)
def get_menu(
    category: str | None = Query(default=None, description="Filter by chai, snacks, or combos"),
):
    if category:
        filtered = [item for item in MENU_ITEMS if item["category"].lower() == category.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No item found in category: {category}")
        return MenuResponse(count=len(filtered), items=filtered)

    return MenuResponse(count=len(MENU_ITEMS), items=MENU_ITEMS)
```

Two genuinely different paths through one function, controlled entirely by whether `category` was supplied:

- **No `category`** — the `if category:` block is skipped entirely, and the whole `MENU_ITEMS` list comes back as-is.
- **`category` supplied** — a list comprehension filters `MENU_ITEMS` down to matching entries, comparing `.lower()` on both sides so `chai`, `Chai`, and `CHAI` all match the same category. If nothing matches, that's a `404` via `HTTPException`, not an empty success response — an empty `items: []` with a `200` would silently look like **this category legitimately has zero items,** when what actually happened is the category doesn't exist at all.

Both return paths build a `MenuResponse` — same shape either way, exactly the consistency that model was built for.

---

## `GET /menu/{item_id}` — one specific item

```python
@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int):
    for item in MENU_ITEMS:
        if item["id"] == item_id:
            return item

    raise HTTPException(status_code=404, detail=f"Menu item with ID {item_id} not found")
```

The `response_model` here is `MenuItem`, not `MenuResponse` — this route returns exactly one item, not a wrapped list, so the response shape has to match that.

The logic is a plain linear search: loop through every item, return the first one whose `id` matches. If the loop finishes without returning — meaning nothing matched — execution falls through to the `raise HTTPException(...)` line underneath it. That fall-through is doing real work: there's no `else`, no flag variable tracking whether anything was found; the loop either exits early via `return`, or it runs out and hits the exception naturally.

`item_id: int` in the signature means the URL's raw text (`"4"`) arrives already converted to the integer `4`, so `item["id"] == item_id` is comparing an int to an int, not a string to an int.

---

