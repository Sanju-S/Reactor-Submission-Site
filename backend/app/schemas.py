from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# ---------- AUTH ----------
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str


# ---------- CHALLENGE ----------
class ChallengeCreate(BaseModel):
    name: str
    challenge_start: datetime
    challenge_end: Optional[datetime] = None

class SubmissionLinkCreate(BaseModel):
    submit_start: datetime
    submit_end: datetime
    link_type: str  # fixed | range
    fixed_count: Optional[int] = None
    max_count: Optional[int] = None


# ---------- SUBMISSION ----------
class SubmissionCreate(BaseModel):
    name: str
    instagram_id: str
    links: List[str]
    wants_money: bool
    upi_id: Optional[str] = None
