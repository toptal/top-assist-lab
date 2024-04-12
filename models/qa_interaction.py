from database.database import Base
from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
from sqlalchemy import Column, Integer, String, Text, DateTime
import json  # TODO Can we switch to sqlalchemy JSON type?


class QAInteraction(Base):
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
