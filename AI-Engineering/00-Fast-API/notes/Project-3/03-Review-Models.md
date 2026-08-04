The SQLModel pattern applied to this project's actual data: one table, three validation schemas around it.

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
- **`rating`** — constrained to `1`–`5` directly through `Field(ge=1, le=5)`, the same validation power seen with `field_validator`, just simpler to express for a plain numeric range.
- **`created_at`** — `default_factory=datetime.now`, not `default=datetime.now()`. Function reference, not a called value — the difference between every review getting a genuinely fresh timestamp versus every review sharing the exact moment the server happened to start.

---

## The three schemas around it

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

**`ReviewCreate`** — what a client is allowed to submit to create a review. No `id`, no `created_at`: both are the database's responsibility, not the caller's. Sending either of those fields to this schema simply wouldn't validate against it — the schema itself is what enforces that a client can't invent its own id or backdate a review.

**`ReviewRead`** — what comes back when a review is read. Now `id` and `created_at` *do* appear, because by the time something is being read, the database has already assigned both.

**`ReviewUpdate`** — every field optional, defaulting to `None`. This is the schema a `PATCH /reviews/{id}` request validates against: sending `{"rating": 4}` alone is perfectly valid here, because `comment` being absent is allowed. `rating`'s constraint (`ge=1, le=5`) still applies *if* a rating is sent — optional doesn't mean unvalidated, it means "validated only when present."

The shape of all three exists specifically to keep the table model's real column set — the actual source of truth — separate from what any particular caller is permitted to see or send at each stage of interacting with it.
