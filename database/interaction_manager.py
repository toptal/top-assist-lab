# ./database/interaction_manager.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
from models.qa_interaction import QAInteraction
import json

from configuration import sql_file_path


# Define the base class for SQLAlchemy models
Base = declarative_base()


class QAInteractionManager:
    def __init__(self):
        self.engine = create_engine('sqlite:///' + sql_file_path)
        self.Session = sessionmaker(bind=self.engine)

    def add_question_and_answer(self, question, answer, thread_id, assistant_thread_id, channel_id, question_ts,
                                answer_ts, slack_user_id):
        session = self.Session()
        try:
            serialized_answer = json.dumps(answer.__dict__) if not isinstance(answer, str) else answer
            interaction = QAInteraction(
                question_text=question,
                thread_id=thread_id,
                assistant_thread_id=assistant_thread_id,
                answer_text=serialized_answer,
                channel_id=channel_id,
                question_timestamp=question_ts,
                answer_timestamp=answer_ts,
                comments=json.dumps([]),  # Initialize an empty list of comments
                slack_user_id=slack_user_id  # Store the Slack user ID
            )
            session.add(interaction)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_comment_to_interaction(self, thread_id, comment):
        session = self.Session()
        try:
            interaction = session.query(QAInteraction).filter_by(thread_id=thread_id).first()
            if interaction:
                if interaction.comments is None:
                    interaction.comments = json.dumps([])
                comments = json.loads(interaction.comments)
                comments.append(comment)
                interaction.comments = json.dumps(comments)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_interaction_by_thread_id(self, thread_id):
        session = self.Session()
        try:
            return session.query(QAInteraction).filter_by(thread_id=thread_id).first()
        finally:
            session.close()

    def get_interaction_by_interaction_id(self, interaction_id):
        session = self.Session()
        try:
            return session.query(QAInteraction).filter_by(interaction_id=interaction_id).first()
        finally:
            session.close()

    def get_interactions_by_interaction_ids(self, interaction_ids):
        session = self.Session()
        try:
            # The query filters QAInteraction by checking if the interaction_id is in the list of interaction_ids
            return session.query(QAInteraction).filter(QAInteraction.interaction_id.in_(interaction_ids)).all()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_qa_interactions(self):
        session = self.Session()
        try:
            return session.query(QAInteraction).all()
        finally:
            session.close()

    def get_all_interactions(self):
        session = self.Session()
        try:
            return session.query(QAInteraction).all()
        finally:
            session.close()

    def add_embed_to_interaction(self, interaction_id, embed):
        session = self.Session()
        try:
            interaction = session.query(QAInteraction).filter_by(interaction_id=interaction_id).first()
            if interaction:
                interaction.embed = json.dumps(embed)
                interaction.last_embedded = datetime.now(timezone.utc)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_interactions_without_embeds(self):
        session = self.Session()
        try:
            # Filter interactions where embed is either None, the JSON representation of an empty list, or an empty string
            return session.query(QAInteraction).filter(
                (QAInteraction.embed.is_(None)) |
                (QAInteraction.embed == json.dumps([])) |
                (QAInteraction.embed == '')
            ).all()
        finally:
            session.close()

    def get_interactions_with_embeds(self):
        session = self.Session()
        try:
            # Filter interactions where embed is either None, the JSON representation of an empty list, or an empty string
            return session.query(QAInteraction).filter(
                (QAInteraction.embed.is_not(None)) |
                (QAInteraction.embed != json.dumps([])) |
                (QAInteraction.embed != '')
            ).all()
        finally:
            session.close()


# Set up the database engine and create tables if they don't exist
engine = create_engine('sqlite:///' + sql_file_path)
Base.metadata.bind = engine
Base.metadata.create_all(engine)

# Create a session maker object to manage database sessions
Session = sessionmaker(bind=engine)
session = Session()
