`GET /reviews/{review_id}` — a single row, looked up by its primary key. The shortest route in this project, and it introduces a method genuinely different from everything used so far.

```python
@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(ReviewTable, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review
```

Every earlier lookup went through `select(...)`, optionally `.where(...)`, then `session.exec(...)`. `session.get(ReviewTable, review_id)` skips all of that — it's a **dedicated shortcut for looking something up by its primary key**, taking the model class and the id directly, with no query-building step at all.

Two reasons this exists as its own method rather than everyone just writing `select(ReviewTable).where(ReviewTable.id == review_id)` every time:

- **It's shorter**, for what is genuinely the single most common kind of lookup in any CRUD application — get me the one thing with this id.
- **It checks the session's own memory first.** If an object with that primary key has already been loaded into this session earlier in the same request, `session.get(...)` can return that already-loaded object directly, without a fresh round-trip to the database at all. A `select(...).where(...)` query always goes to the database; `session.get(...)` doesn't have to.

`session.get(...)` returns `None` if nothing matches that id — not an exception, not an empty list, just `None` — which is exactly why `if not review:` is the check here, the same pattern already used for a missing dictionary key or an empty list earlier in this course, just applied to a database lookup this time.
