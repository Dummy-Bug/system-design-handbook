The previous note argued that SQLModel merges the table class and the read schema into one. This note is what that leaves behind: the classes this project actually defines, and why there are four of them rather than one.

## Why one concept needs several classes

A table model and its schemas divide one idea — a review — along a line that matters: what actually gets **stored**, against what a **client is allowed to send or receive**. Two of the four are already settled. A **create** schema has to be separate from the table because leaving `id` and `created_at` out of it is the only thing stopping a client from sending them. A **read** schema is separate only when the shape going out genuinely differs from the shape stored — otherwise the table class serves as the `response_model` directly. Both were derived earlier, so the summary is just the shape of the pattern:

| Class | `table=True`? | Purpose |
|---|---|---|
| The table model | Yes | The full column set — everything actually stored, including the fields no client ever sends: an auto-generated `id` and a server-set `created_at` |
| A **create** schema | No | Only the fields a client should be allowed to submit when creating a new row — deliberately **excludes** the fields the server is responsible for filling in |
| A **read** schema | No | The shape returned to a caller reading data back — needed only when it has to differ from the stored shape |
| An **update** schema | No | Every field **optional**, since an update might only touch one of them |

> [!note] The two excluded fields are excluded for **different reasons**, which is worth keeping straight. `id` is left out because **only the database can produce it** — it assigns the next number as the row is written, and Python has no way to know it in advance. `created_at` is left out because **a client must not be trusted to say when something happened**; nothing stops it technically, and this project fills the value in Python the moment the object is built, not in the database at all. Same exclusion, two different justifications.

The last row is the one this project hasn't earned yet, and it differs from the others in **kind**. Every other class here describes a complete review. An update schema describes a **set of changes** — which is why every field on it is optional, and why it can't simply reuse the fields the others share.

That connects directly back to the very first distinction drawn between `PUT` and `PATCH`: a `PATCH` request should be able to send just the one field being changed, leaving everything else untouched. An update schema with every field optional is the concrete Pydantic-level mechanism that makes that possible — a client sending only `{"rating": 4}` validates cleanly, because every other field is allowed to simply be absent.

> [!note] Optional here means the caller may leave a field out, and nothing more. The earlier failure still applies: optional never means forbidden, so an update schema must not carry `id` or `created_at` as optional fields in the hope that nobody sends them.


---

## This project's four classes

All four, as they actually appear in `models.py` — one table, three schemas around it.

```python
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class ReviewTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    play_name: str = Field(index=True)
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.now)
```

This is the actual database table — every field here becomes a column, and `table=True` is what makes that happen. Worth reading each field's choices deliberately:

- **`id`** — `Optional[int]`, `default=None`, `primary_key=True`. It's optional because the database assigns it, not the caller — a new review is created without one, and the database fills it in.
- **`play_name`** — indexed, since filtering reviews by which play they belong to is an expected, frequent query.
- **`rating`** — written as `Field(ge=1, le=5)`, but on a `table=True` class that range is **not enforced**: constructing `ReviewTable(rating=99)` succeeds, and no `CHECK` constraint reaches SQLite either. It is here as a statement of intent and as insurance if the class is ever reused without `table=True`. The rating is genuinely enforced one layer up, on `ReviewCreate` — see the schemas below.
- **`created_at`** — `default_factory=datetime.now`, not `default=datetime.now()`. Function reference, not a called value — the difference between every review getting a genuinely fresh timestamp versus every review sharing the exact moment the server happened to start.

---

### The three schemas around it

```python
class ReviewCreate(SQLModel):
    play_name: str
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    comment: str


class ReviewRead(SQLModel):
    id: int
    play_name: str
    reviewer_name: str
    rating: int
    comment: str
    created_at: datetime


class ReviewUpdate(SQLModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
```

None of these three has `table=True` — they're pure validation shapes, exactly like every Pydantic model in the earlier projects, just built from `SQLModel` instead of `BaseModel` so the same import and `Field` syntax carries over without needing two separate libraries in the same file.

**`ReviewCreate`** — what a client is allowed to submit to create a review. No `id`, no `created_at`: both are the database's responsibility, not the caller's. Sending either of those fields to this schema simply wouldn't validate against it — **the schema itself is what enforces that a client can't invent its own id or backdate a review**.

**`ReviewRead`** — what comes back when a review is read. Now `id` and `created_at` **do** appear, because by the time something is being read, the database has already assigned both.

**`ReviewUpdate`** — every field optional, defaulting to `None`. This is the schema a `PATCH /reviews/{id}` request validates against: sending `{"rating": 4}` alone is perfectly valid here, because `comment` being absent is allowed. `rating`'s constraint (`ge=1, le=5`) still applies **if** a rating is sent — optional doesn't mean unvalidated, it means **validated only when present.**

The shape of all three exists specifically to keep the table model's real column set — the actual source of truth — separate from what any particular caller is permitted to see or send at each stage of interacting with it.

> [!important] These three are not merely tidier — for this app they are the **entire** validation layer. Since `ReviewTable` validates nothing, a rating of `99` is rejected only because `POST /reviews` takes a `ReviewCreate` and `PATCH /reviews/{id}` takes a `ReviewUpdate`, and both of those do enforce `ge=1, le=5`. Write a route that builds a `ReviewTable` straight from raw input and that protection is gone, silently, with no error anywhere.
