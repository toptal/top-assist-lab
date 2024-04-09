from sqlalchemy.exc import SQLAlchemyError
from models.bookmarked_conversation import BookmarkedConversation
from datetime import datetime, timezone
from database.database import Database


class BookmarkedConversationManager:
    def __init__(self):
        self.db = Database()

    def add_bookmarked_conversation(self, title, body, thread_id):
        new_conversation = BookmarkedConversation(title=title, body=body, thread_id=thread_id)
        return self.db.add_object(new_conversation)

    def update_posted_on_confluence(self, thread_id):
        try:
            with self.db.get_session() as session:
                conversation = session.query(BookmarkedConversation).filter_by(thread_id=thread_id).first()
                if conversation:
                    conversation.posted_on_confluence = datetime.now(timezone.utc)
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error updating conversation with Confluence timestamp: {e}")
            return None

    def get_unposted_conversations(self):
        try:
            with self.db.get_session() as session:
                return session.query(BookmarkedConversation).filter_by(posted_on_confluence=None).all()
        except SQLAlchemyError as e:
            print(f"Error getting unposted conversations: {e}")
            return None
