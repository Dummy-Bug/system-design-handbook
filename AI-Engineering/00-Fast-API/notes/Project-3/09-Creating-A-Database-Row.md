Every project so far has read from fixed or in-memory data. This is the first genuinely new operation: taking validated input and turning it into a permanent database row — three lines doing a surprising amount of work.

---

## Converting one schema's data into another schema's shape

```python
@router.post("/", response_model=SomethingRead)
def create_something(item: SomethingCreate, session: Session = Depends(get_session)):
    db_item = SomethingTable(**item.model_dump())
    ...
```

`item` arrives as a `SomethingCreate` instance — the input-validation shape, holding only the fields a caller is allowed to submit. But what needs to be added to the database is a `SomethingTable` instance — a different class, with additional fields (`id`, timestamps) the create-schema deliberately excludes.

**`item.model_dump()`** converts the validated Pydantic/SQLModel object back into a plain Python dictionary — `{"field": value, ...}` for every field on `item`. **`**item.model_dump()`** then unpacks that dictionary as keyword arguments into `SomethingTable(...)`.

> [!note] This works cleanly specifically *because* of how the schemas were designed in the first place. `SomethingCreate` and `SomethingTable` share the fields a caller submits (matching names, matching types) — those get filled in from `item`'s data. The fields `SomethingTable` has that `SomethingCreate` doesn't (an auto-assigned `id`, a `created_at` default) are simply absent from the unpacked dictionary — and because those fields were given defaults (`Field(default=None, primary_key=True)`, `Field(default_factory=datetime.now)`) back when the table model was defined, `SomethingTable(**item.model_dump())` doesn't error over their absence; it just falls back to those defaults. The multiple-schema pattern and this one line of unpacking are designed to fit together.

---

## The add / commit / refresh sequence

```python
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
```

Three distinct steps, each doing a different job:

| Step | What actually happens |
|---|---|
| `session.add(db_item)` | **Stages** the object for insertion. Nothing is written to the database yet — this just tells the session "this object should be part of the next save." |
| `session.commit()` | **Executes** the actual transaction — this is the point the `INSERT` genuinely runs against the database and the change becomes permanent. |
| `session.refresh(db_item)` | **Reloads** `db_item`'s fields from the database, after the commit. |

That last step is easy to assume is unnecessary, but it's doing real work: before the commit, `db_item.id` is still `None` — nothing has assigned it a real id yet, since that's the database's job, happening only at insert time. `session.refresh(db_item)` pulls the now-assigned `id` (and any other database-computed fields) back into the same Python object, so the value returned to the caller — via `response_model=SomethingRead` — actually has a real `id`, not `None`.

Skipping `refresh` wouldn't crash anything, but the response handed back to whoever made the request would be missing the very id they'd need to look the new row up again afterward.
