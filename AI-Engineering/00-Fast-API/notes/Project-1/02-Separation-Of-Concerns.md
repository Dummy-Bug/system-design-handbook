
## Why the data doesn't just live in `main.py`

Nothing stops the menu from being declared directly inside the same file as the routes. It would work. The reason not to do that is a general principle, not a FastAPI-specific rule:

> [!important] **Separation of concerns.** Data and the logic that serves it are different responsibilities, and keeping them in different places makes each one easier to reason about on its own. 
> This is the same underlying reason most real applications put their data behind a database rather than inline in application code — a database is one way of enforcing that separation, but it isn't the only way. Here, with no database allowed, a dedicated `data.py` file does the same job: the menu lives in exactly one place, and the routes that serve it live somewhere else entirely.

So `data.py` isn't a workaround for not having a database — it's the same discipline a database would normally provide, applied by hand because this project's constraint ruled the database out specifically.

---

## The shape of one menu item

```python
MENU_ITEMS = [
    {
        "id": 1,
        "name": "Masala Chai",
        "category": "chai",
        "description": "A classic, spiced Indian tea.",
        "price": 30,
        "available": True,
    },
    # ...
]
```

| Field | What it holds |
|---|---|
| `id` | Unique identifier for the item — what `/menu/{id}` will look up later |
| `name` | Display name |
| `category` | One of a small fixed set — `chai`, `snacks`, `combos` — what `/menu?category=...` will filter on |
| `description` | Short freeform text |
| `price` | Numeric |
| `available` | `True`/`False` — whether the item is currently being served |

The whole dataset is just a Python list of dictionaries, all sharing this same shape. One item understood properly is enough — every other entry is the same pattern with different values.

---

## Why the shape matters more than the values

The specific chai names and prices are incidental. What actually matters is that **every item in the list shares an identical set of keys**, because the routes that get built next depend on that consistency:

- `/menu/{id}` needs every item to have an `id` to search by
- `/menu?category=chai` needs every item to have a `category` to filter by
- Whether unavailable items should even show up in `/menu` at all depends on every item reliably having `available` set

That last point is worth sitting with rather than assuming an answer to: the data supports filtering by `available`, but nothing about the brief says whether `/menu` should silently hide unavailable items by default, or show everything and let the caller filter. That's a design decision the routes still have to make — the data file just makes either choice possible.
