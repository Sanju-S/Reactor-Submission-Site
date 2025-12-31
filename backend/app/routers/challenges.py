from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from sqlalchemy.orm import joinedload

from ..database import SessionLocal
from ..models import Challenge, SubmissionLink, Submission, SubmissionItem
from ..deps import get_db
from ..schemas import ChallengeCreate, SubmissionLinkCreate
from ..auth import get_current_user

router = APIRouter()

@router.get("/")
def list_challenges(db: Session = Depends(get_db)):
    return db.query(Challenge).all()

# @router.post("/")
# def create_challenge(
#     name: str,
#     challenge_start: datetime,
#     challenge_end: datetime | None = None,
#     db: Session = Depends(get_db)
# ):
#     ch = Challenge(
#         name=name,
#         challenge_start=challenge_start,
#         challenge_end=challenge_end,
#         created_by=1
#     )
#     db.add(ch)
#     db.commit()
#     db.refresh(ch)
#     return ch

@router.post("/", dependencies=[Depends(get_current_user)])
def create_challenge(
    data: ChallengeCreate,
    db: Session = Depends(get_db)
):
    ch = Challenge(**data.dict(), created_by=1)
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ch

# @router.post("/{challenge_id}/submission-link")
# def create_submission_link(
#     challenge_id: int,
#     submit_start: datetime,
#     submit_end: datetime,
#     link_type: str,
#     fixed_count: int | None = None,
#     max_count: int | None = None,
#     db: Session = Depends(get_db)
# ):
#     challenge = db.query(Challenge).get(challenge_id)
#     if not challenge:
#         raise HTTPException(404, "Challenge not found")

#     if submit_end > challenge.challenge_start:
#         raise HTTPException(400, "Submission end exceeds challenge start")

#     token = str(uuid.uuid4())

#     link = SubmissionLink(
#         challenge_id=challenge_id,
#         token=token,
#         submit_start=submit_start,
#         submit_end=submit_end,
#         link_type=link_type,
#         fixed_count=fixed_count,
#         max_count=max_count
#     )
#     db.add(link)
#     db.commit()
#     return {"submission_url": f"/submit/{token}"}

@router.post("/{challenge_id}/submission-link",
             dependencies=[Depends(get_current_user)])
def create_submission_link(
    challenge_id: int,
    data: SubmissionLinkCreate,
    db: Session = Depends(get_db)
):
    challenge = db.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(404, "Challenge not found")

    if data.submit_end > challenge.challenge_start:
        raise HTTPException(400, "Submission end exceeds challenge start")

    token = str(uuid.uuid4())

    link = SubmissionLink(
        challenge_id=challenge_id,
        token=token,
        **data.dict()
    )
    db.add(link)
    db.commit()
    return {"submission_url": f"/submit/{token}"}


@router.get("/{challenge_id}/submissions",
            dependencies=[Depends(get_current_user)])
def get_submissions(challenge_id: int, db: Session = Depends(get_db)):
    submissions = (
        db.query(Submission)
        .options(joinedload(Submission.items))
        .filter(Submission.challenge_id == challenge_id)
        .all()
    )

    result = []

    for sub in submissions:
        all_viewed = all(i.viewed for i in sub.items) if sub.items else False

        result.append({
            "submission_id": sub.id,
            "name": sub.name,
            "instagram_id": sub.instagram_id,
            "is_winner": sub.is_winner,
            "viewed": all_viewed,
            "links": [
                {
                    "item_id": i.id,
                    "link": i.link,
                    "viewed": i.viewed,
                    "is_winner": i.is_winner
                }
                for i in sub.items
            ]
        })

    return result

@router.get("/{challenge_id}/winners",
            dependencies=[Depends(get_current_user)])
def get_winners(challenge_id: int, db: Session = Depends(get_db)):
    winners = db.query(Submission).filter(
        Submission.challenge_id == challenge_id,
        Submission.is_winner == True
    ).all()

    return [
        {
            "name": w.name,
            "instagram_id": w.instagram_id,
            "upi_id": w.upi_id
        }
        for w in winners
    ]

