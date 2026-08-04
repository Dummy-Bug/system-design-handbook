Every project so far has kept every route directly on `app` inside `main.py`. That stops scaling the moment an app has more than a handful of routes — `main.py` would keep growing forever, mixing app setup with dozens of unrelated endpoints. `APIRouter` is the fix.

---

## The folder shape

```
project/
├── main.py
└── routes/
    ├── __init__.py
    └── reviews.py
```

`__init__.py` is typically **empty** — its only job is telling Python "treat this folder as an importable package," so `routes.reviews` works as an import path. Nothing is meant to be written inside it for this purpose; it's a marker file, not a place for logic.

---

## Defining a router

```python
from fastapi import APIRouter

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/")
def list_reviews():
    ...
```

`APIRouter` behaves like a miniature version of `app` — it has its own `.get(...)`, `.post(...)`, and so on — but it isn't a running application by itself. It's a **collection of routes** waiting to be attached to the real `app` somewhere else.

Two parameters worth being precise about:

- **`prefix="/reviews"`** — every route defined on this router gets this string prepended automatically. A route declared as `"/"` on this router does **not** mean the application's root — it means `/reviews`, because the prefix is stacked in front of it. A route declared `"/{id}"` here becomes `/reviews/{id}`. This is easy to misread at a glance, since `"/"` looks like the application root everywhere else in this course so far — here specifically, it means "the root *of this router's own prefix*."
- **`tags=["reviews"]`** — every route on this router gets grouped under this tag in the generated docs, the same tagging mechanism from the doc-customization note, just applied once for the whole file instead of route by route.

---

## Wiring it into the app

```python
# main.py
from routes.reviews import router as reviews_router

app.include_router(reviews_router)
```

`app.include_router(...)` is what actually merges this router's routes into the running application — until this line runs, the routes defined in `reviews.py` exist as Python objects but aren't reachable by anything, the same "defined but not connected" gap seen with custom exception handlers before their registration call.

The payoff: `main.py` stays small and focused on app-level setup (title, description, lifespan, mounting routers), while each area of functionality — reviews, and whatever comes after it — lives in its own file, importable and testable independently of everything else.
