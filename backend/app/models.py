from sqlalchemy import *
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String)


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    challenge_start = Column(DateTime)
    challenge_end = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))


class SubmissionLink(Base):
    __tablename__ = "submission_links"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), unique=True)
    token = Column(String, unique=True)
    submit_start = Column(DateTime)
    submit_end = Column(DateTime)
    link_type = Column(String)
    fixed_count = Column(Integer)
    max_count = Column(Integer)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    name = Column(String)
    instagram_id = Column(String)
    wants_money = Column(Boolean)
    upi_id = Column(String)
    is_winner = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("challenge_id", "instagram_id"),
    )

    # 🔑 ADD THIS
    items = relationship(
        "SubmissionItem",
        back_populates="submission",
        cascade="all, delete-orphan"
    )


class SubmissionItem(Base):
    __tablename__ = "submission_items"

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    link = Column(String)
    viewed = Column(Boolean, default=False)
    is_winner = Column(Boolean, default=False)

    # 🔑 ADD THIS
    submission = relationship(
        "Submission",
        back_populates="items"
    )
