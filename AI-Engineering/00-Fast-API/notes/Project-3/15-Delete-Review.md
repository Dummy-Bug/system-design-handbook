`DELETE /reviews/{review_id}` — the last of the four CRUD operations, and the simplest.

```python
@router.delete("/{review_id}")
def delete_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(ReviewTable, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    session.delete(review)
    session.commit()
    return {"message": "Review deleted"}
```

Same lookup as the previous two routes — `session.get(...)`, same `404` if nothing matches. The only genuinely new line is `session.delete(review)`: stages the object for removal, the deletion equivalent of `session.add(...)` staging an object for insertion. Nothing is actually removed from the database until `session.commit()` runs — up to that point, the deletion is still just pending, reversible by a `rollback()` the same way an uncommitted insert would be.

**No `response_model`, and no returning the review** — there's nothing left to shape a response around once the row is gone. Returning a plain confirmation message is the honest option here, rather than trying to force the deleted object into a response shape built for describing something that still exists.

**Worth naming plainly, not glossing over:** this route has no authentication or ownership check — it deletes on `review_id` alone, with no verification of who's asking or whether they're allowed to remove this particular review. That's an accurate limitation of this project as built so far, not something to pretend isn't there. A production version of this endpoint would need to confirm the caller actually owns (or is authorized to delete) the review before this line ever runs.
