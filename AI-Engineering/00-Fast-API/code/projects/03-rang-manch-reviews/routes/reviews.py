from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

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

@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(ReviewTable, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review


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


@router.delete("/{review_id}")
def delete_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(ReviewTable, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    session.delete(review)
    session.commit()
    return {"message": "Review deleted"}


@router.get("/", response_model=list[ReviewRead])
def list_reviews(
    play_name: str | None = Query(default=None, description="Filter by play name"),
    skip: int = Query(default=0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="Max reviews to return"),
    session: Session = Depends(get_session),
):
    query = select(ReviewTable)

    if play_name:
        query = query.where(ReviewTable.play_name == play_name)

    query = query.offset(skip).limit(limit)

    reviews = session.exec(query).all()
    return reviews


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

