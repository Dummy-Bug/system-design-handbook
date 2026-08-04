Routes move out of `main.py` for the first time, and the first real database write goes in — `routes/reviews.py`, mounted into the app.

```python
# routes/reviews.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from models import ReviewTable, ReviewCreate, ReviewRead, ReviewUpdate
from database import get_session

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewRead)
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    db_review = ReviewTable(**review.model_dump())
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review
```

```python
# main.py
from routes.reviews import router as reviews_router

app.include_router(reviews_router)
```

A `POST` to `/reviews` (the route is declared as `"/"`, but the router's `prefix="/reviews"` makes the real path `/reviews`) now:

1. Receives a body, validated against `ReviewCreate` — no `id`, no `created_at`, exactly the fields a reviewer is meant to submit.
2. Builds a `ReviewTable` row from that data via `ReviewTable(**review.model_dump())` — `play_name`, `reviewer_name`, `rating`, `comment` carry across from `review`; `id` and `created_at` fall back to the defaults defined on `ReviewTable` itself.
3. Stages it, commits it, refreshes it — the genuine `INSERT`, and the point `db_review.id` stops being `None`.
4. Returns `db_review` — validated and shaped against `response_model=ReviewRead` on the way out, which is why the response includes `id` and `created_at` even though the request that created it never sent either.

This single route touches every piece built across this project so far: the table model and its three schemas, the session dependency, and the router mounting pattern — the first time all of it works together end to end, for a genuinely new row landing in `rangmanch.db`.

The remaining three routes — list, update, delete — are next.
