from .base import *


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'

    id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    thread_id = Column(String)
    summary = Column(Text)
    posted_on_slack = Column(DateTime)
    posted_on_confluence = Column(DateTime, nullable=True)

