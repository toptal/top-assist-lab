from models.bookmarked_conversation import BookmarkedConversation
from datetime import datetime, timezone


def add_bookmarked_conversation(session, title, body, thread_id):
    new_conversation = BookmarkedConversation(title=title, body=body, thread_id=thread_id)
    session.add(new_conversation)
    session.commit()


def update_posted_on_confluence(session, thread_id):
    conversation = session.query(BookmarkedConversation).filter_by(thread_id=thread_id).first()
    if conversation:
        conversation.posted_on_confluence = datetime.now(timezone.utc)
        session.commit()
        print(f"Updated conversation with thread ID {thread_id} with timestamp")
