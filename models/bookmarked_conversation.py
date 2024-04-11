from database.database import Base
from database.mixins.crud_mixin import CRUDMixin
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime


class BookmarkedConversation(Base, CRUDMixin):
    __tablename__ = 'bookmarked_conversations'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    body = Column(Text)
    thread_id = Column(String)
    bookmarked_on_slack = Column(DateTime, default=datetime.now(timezone.utc))
    posted_on_confluence = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<BookmarkedConversation(title={self.title}, thread_id={self.thread_id})>"

    def get_filter_attributes(self):
        return [
            "id",
        ]
