from models.bookmarked_conversation import BookmarkedConversation
from datetime import datetime, timezone


class BookmarkedConversationManager:
    def __init__(self, session):
        self.session = session

    def add_bookmarked_conversation(self, title, body, thread_id):
        BookmarkedConversation().create_or_update(self.session,
                                                  title=title,
                                                  body=body,
                                                  thread_id=thread_id)

    def update_posted_on_confluence(self, thread_id):
        BookmarkedConversation().create_or_update(self.session,
                                                  thread_id=thread_id,
                                                  posted_on_confluence=datetime.now(timezone.utc))
        print(f"Updated conversation with thread ID {thread_id} with timestamp")

    def get_unposted_conversations(self):
        return self.session.query(BookmarkedConversation).filter_by(posted_on_confluence=None).all()
