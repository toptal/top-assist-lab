# from database.database import Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String


class UserScore(Base):
    """
    SQLAlchemy model for storing user scores.
    """
    __tablename__ = 'user_scores'

    id = Column(Integer, primary_key=True)
    slack_user_id = Column(String, unique=True, nullable=False)
    seeker_score = Column(Integer, default=0)
    revealer_score = Column(Integer, default=0)
    luminary_score = Column(Integer, default=0)
