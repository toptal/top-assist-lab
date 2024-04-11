from sqlalchemy.exc import SQLAlchemyError
from models.bookmarked_conversation import BookmarkedConversation
from datetime import datetime, timezone


class BookmarkedConversationManager:
    def __init__(self, db_session):
        self.db_session = db_session

    def add_bookmarked_conversation(self, title, body, thread_id):
        with self.db_session as session:
            BookmarkedConversation().create_or_update(session,
                                                      title=title,
                                                      body=body,
                                                      thread_id=thread_id)

    def update_posted_on_confluence(self, thread_id):
        with self.db_session as session:
            BookmarkedConversation().create_or_update(session,
                                                      thread_id=thread_id,
                                                      posted_on_confluence=datetime.now(timezone.utc))
        print(f"Updated conversation with thread ID {thread_id} with timestamp")

    def get_unposted_conversations(self):
        try:
            with self.db_session as session:
                return session.query(BookmarkedConversation).filter_by(posted_on_confluence=None).all()
        except SQLAlchemyError as e:
            print(f"Error getting unposted conversations: {e}")
            return None
