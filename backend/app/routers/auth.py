from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt

from ..schemas import LoginRequest, TokenResponse
from ..deps import get_db
from ..models import User
from ..utils.security import verify_password
from ..auth import SECRET_KEY, ALGORITHM

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = jwt.encode(
        {"sub": user.username, "role": user.role},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": token}
