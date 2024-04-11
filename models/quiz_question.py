# from database.database import Base
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from database.mixins.crud_mixin import CRUDMixin
from sqlalchemy import Column, Integer, String, Text, DateTime


class QuizQuestion(Base, CRUDMixin):
    __tablename__ = 'quiz_questions'

    id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    thread_id = Column(String)
    summary = Column(Text)
    posted_on_slack = Column(DateTime)
    posted_on_confluence = Column(DateTime, nullable=True)

    def get_filter_attributes(self):
        return [
            "id", "thread_id"
        ]
