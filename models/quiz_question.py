from .base import *


class QuizQuestion(Base):
    __tablename__ = 'quiz_questions'

    id = Column(Integer, primary_key=True)
    question_text = Column(Text)
    thread_id = Column(String)  # Slack thread ID for tracking conversations
    summary = Column(Text)  # Summary of the conversation
    posted_on_slack = Column(DateTime)  # Timestamp when posted on Slack
    posted_on_confluence = Column(DateTime, nullable=True)  # Timestamp when posted on Confluence

