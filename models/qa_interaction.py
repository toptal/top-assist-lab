from database.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime
import json


class QAInteraction(Base):
    """
    SQLAlchemy model for storing QA interactions.
    """
    __tablename__ = 'qa_interactions'

    id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    thread_id = Column(String)
    assistant_thread_id = Column(String)
    answer_text = Column(Text)
    channel_id = Column(String)
    slack_user_id = Column(String)
    question_timestamp = Column(DateTime)
    answer_timestamp = Column(DateTime)
    comments = Column(Text, default=json.dumps([]))
    last_embedded = Column(DateTime)
    embed = Column(Text, default=json.dumps([]))
