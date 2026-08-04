A route that computes something, rather than just returning stored rows — `GET /reviews/average/{play_name}`, backed by SQL aggregate functions instead of Python arithmetic.

---

## Why this runs in the database, not in Python

The naive approach: fetch every review for a play, then average the ratings in a Python loop. It would work. It's also strictly worse — pulling every row across the network just to reduce them to two numbers is wasted transfer, and databases are specifically built to perform aggregation (`AVG`, `COUNT`, `SUM`, `MIN`, `MAX`) efficiently over however many rows exist, without ever handing the raw rows back to the caller. Doing the math where the data already lives is the whole point.

---

## The route

```python
from sqlmodel import func

@router.get("/average/{play_name}")
def get_average_rating(play_name: str, session: Session = Depends(get_session)):
    query = select(func.avg(ReviewTable.rating), func.count(ReviewTable.id)).where(
        ReviewTable.play_name == play_name
    )
    result = session.exec(query).first()
    average_rating, total_reviews = result

    if total_reviews == 0:
        raise HTTPException(status_code=404, detail=f"No reviews found for {play_name}")

    return {
        "play_name": play_name,
        "average_rating": round(average_rating, 2),
        "total_reviews": total_reviews,
    }
```

`func` — imported directly from `sqlmodel` — is the entry point to SQL's aggregate functions. `func.avg(ReviewTable.rating)` and `func.count(ReviewTable.id)` aren't Python computations; they're descriptions of SQL expressions (`AVG(rating)`, `COUNT(id)`), assembled the same way `.where(...)` assembles a `WHERE` clause — written in Python, executed as real SQL.

---

## Selecting *expressions* instead of a *model* changes what comes back

```python
result = session.exec(query).first()
average_rating, total_reviews = result
```

Every earlier query in this project selected a whole model — `select(ReviewTable)` — and `session.exec(...)` handed back actual `ReviewTable` instances. This query selects two computed *expressions* instead of a model class, and that changes the shape of what comes back:

> [!important] `session.exec(select(func.avg(...), func.count(...))).first()` returns a **`Row`** object — a plain tuple-like container holding one value per selected expression, in order. It is not a `ReviewTable`, and it has no `.rating` or `.id` attributes to access. That's exactly why the very next line unpacks it positionally — `average_rating, total_reviews = result` — the same way any two-element tuple would be unpacked. Selecting a model gives model instances back; selecting a set of expressions gives a `Row` of values back. Both go through the identical `session.exec(...)` call — the shape of what's *selected* is what determines the shape of what comes *out*.

**`.first()` instead of `.all()`** — this query is only ever going to produce exactly one row (one average, one count, for the whole matching set), so `.first()` fetches that single row directly rather than wrapping it in a list that would only ever hold one element.

---

## The zero-reviews case

```python
if total_reviews == 0:
    raise HTTPException(status_code=404, detail=f"No reviews found for {play_name}")
```

`AVG()` and `COUNT()` don't fail or error when nothing matches — `COUNT` correctly reports `0`, and `AVG` reports `None` (averaging zero numbers is undefined). So this check is genuinely necessary: without it, a play with no reviews at all would return `{"average_rating": None, "total_reviews": 0}` as if that were a valid, successful result, rather than clearly signaling "this play has nothing to average yet."

`round(average_rating, 2)` in the success path is just presentation — capping the average to two decimal places rather than returning whatever floating-point precision SQLite happens to compute.
