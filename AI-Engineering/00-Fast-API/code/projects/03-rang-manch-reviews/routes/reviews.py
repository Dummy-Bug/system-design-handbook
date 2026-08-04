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
