from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..deps import get_db
from ..database import SessionLocal
from ..models import SubmissionLink, Submission, SubmissionItem
from ..schemas import SubmissionCreate
from ..auth import get_current_user

router = APIRouter()


@router.get("/{token}")
def get_submission_form(token: str, db: Session = Depends(get_db)):
    link = db.query(SubmissionLink).filter_by(token=token).first()
    if not link:
        raise HTTPException(404, "Invalid link")

    now = datetime.utcnow()

    if now < link.submit_start:
        return {"status": "not_started", "start": link.submit_start}
    if now > link.submit_end:
        return {"status": "closed"}

    return {
        "status": "open",
        "link_type": link.link_type,
        "fixed_count": link.fixed_count,
        "max_count": link.max_count
    }

# @router.post("/{token}")
# def submit_links(
#     token: str,
#     name: str,
#     instagram_id: str,
#     links: list[str],
#     wants_money: bool,
#     upi_id: str | None = None,
#     db: Session = Depends(get_db)
# ):
#     link = db.query(SubmissionLink).filter_by(token=token).first()
#     if not link:
#         raise HTTPException(404, "Invalid link")

#     if db.query(Submission).filter_by(
#         challenge_id=link.challenge_id,
#         instagram_id=instagram_id
#     ).first():
#         raise HTTPException(400, "Already submitted")

#     submission = Submission(
#         challenge_id=link.challenge_id,
#         name=name,
#         instagram_id=instagram_id,
#         wants_money=wants_money,
#         upi_id=upi_id
#     )
#     db.add(submission)
#     db.commit()
#     db.refresh(submission)

#     for l in links:
#         db.add(SubmissionItem(
#             submission_id=submission.id,
#             link=l
#         ))

#     db.commit()
#     return {"message": "Submission successful"}


@router.post("/{token}")
def submit(token: str, data: SubmissionCreate, db: Session = Depends(get_db)):
    link = db.query(SubmissionLink).filter_by(token=token).first()
    if not link:
        raise HTTPException(404, "Invalid link")

    now = datetime.utcnow()
    if now < link.submit_start or now > link.submit_end:
        raise HTTPException(400, "Submission window closed")

    # Enforce unique Instagram ID
    exists = db.query(Submission).filter_by(
        challenge_id=link.challenge_id,
        instagram_id=data.instagram_id
    ).first()
    if exists:
        raise HTTPException(400, "Already submitted")

    if data.wants_money and not data.upi_id:
        raise HTTPException(400, "UPI ID required")

    # Enforce link count
    count = len(data.links)
    if link.link_type == "fixed" and count != link.fixed_count:
        raise HTTPException(400, "Invalid number of links")
    if link.link_type == "range" and count > link.max_count:
        raise HTTPException(400, "Too many links")

    submission = Submission(
        challenge_id=link.challenge_id,
        **data.dict(exclude={"links"})
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    for l in data.links:
        db.add(SubmissionItem(submission_id=submission.id, link=l))

    db.commit()
    return {"message": "Submitted successfully"}


@router.post("/items/{item_id}/view", dependencies=[Depends(get_current_user)])
def mark_viewed(item_id: int, db: Session = Depends(get_db)):
    item = db.get(SubmissionItem, item_id)
    if not item:
        raise HTTPException(404)
    item.viewed = True
    db.commit()
    return {"status": "ok"}


@router.post("/items/{item_id}/winner", dependencies=[Depends(get_current_user)])
def mark_winner(item_id: int, db: Session = Depends(get_db)):
    item = db.get(SubmissionItem, item_id)
    if not item:
        raise HTTPException(404)
    item.is_winner = True

    submission = db.get(Submission, item.submission_id)
    submission.is_winner = True

    db.commit()
    return {"status": "winner set"}
