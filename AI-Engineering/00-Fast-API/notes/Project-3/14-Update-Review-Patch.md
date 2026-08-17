`PATCH /reviews/{review_id}` — the route that actually delivers on `PATCH`'s promise, made all the way back when `PUT` and `PATCH` were first distinguished: send only what changed, leave everything else untouched.

```python
@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(review_id: int, update: ReviewUpdate, session: Session = Depends(get_session)):
    review = session.get(ReviewTable, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    session.add(review)
    session.commit()
    session.refresh(review)
    return review
```

The lookup is identical to the previous route — `session.get(...)`, the same `if not review:` guard. What's new is everything after it.

---

## `exclude_unset=True` — the mechanism that makes partial genuinely partial

`ReviewUpdate` declares both its fields as optional, defaulting to `None`:

```python
class ReviewUpdate(SQLModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
```

A caller sending `{"rating": 4}` — updating only the rating — constructs a `ReviewUpdate` where `comment` was never provided at all. Calling `.model_dump()` on that object **without** `exclude_unset=True` produces:

```python
{"rating": 4, "comment": None}
```

`comment` shows up anyway, holding its default value, indistinguishable from a caller who deliberately wanted to **clear** the comment. Looping over that dict and applying it with `setattr` would silently null out an existing comment the caller never meant to touch.

> [!important] `exclude_unset=True` changes what `model_dump()` includes: only fields the caller **actually provided** in the request, not fields that merely fell back to their declared default. The same object, dumped with this flag, produces just `{"rating": 4}` — `comment` isn't in there at all, because it was never set. This is the literal mechanism behind `PATCH`'s **only send what changed** behavior — without this flag, every `PATCH` request would risk silently overwriting every field it didn't mention.

---

## The update loop

```python
for key, value in update_data.items():
    setattr(review, key, value)
```

`update_data` is a plain dict — however many keys the caller actually sent, could be one, could be all of them. `setattr(review, key, value)` is ordinary Python: set the attribute named `key` on `review` to `value`. Looping over the dict this way means the same three lines handle a caller updating just the rating, just the comment, or both — no branching needed for how many fields arrived.

---

## Then, the same write sequence as creating a row

```python
session.add(review)
session.commit()
session.refresh(review)
```

Identical shape to the create route — stage, commit, refresh — except `review` here is an **existing**, already-persistent object being modified, not a brand-new one. `session.add(...)` on an object the session already knows about doesn't create a duplicate row; it's effectively a no-op for an object that's already tracked, included here mostly for consistency with the create route's shape. `commit()` writes the changed fields; `refresh()` forces the reload, same reasoning as before.
