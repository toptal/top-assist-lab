# ./database/interaction_manager.py
from datetime import datetime, timezone
from models.qa_interaction import QAInteraction
from sqlalchemy.exc import SQLAlchemyError
import json


class QAInteractionManager:
    def __init__(self, db_session):
        self.db_session = db_session

    def add_question_and_answer(self, question, answer, thread_id, assistant_thread_id, channel_id, question_ts,
                                answer_ts, slack_user_id):

        serialized_answer = json.dumps(answer.__dict__) if not isinstance(answer, str) else answer
        interaction = QAInteraction(
            question_text=question,
            thread_id=thread_id,
            assistant_thread_id=assistant_thread_id,
            answer_text=serialized_answer,
            channel_id=channel_id,
            question_timestamp=question_ts,
            answer_timestamp=answer_ts,
            comments=json.dumps([]),
            slack_user_id=slack_user_id
        )
        self.db.add_object(interaction)

    def add_comment_to_interaction(self, thread_id, comment):
        try:
            with self.db.get_session() as session:
                interaction = session.query(QAInteraction).filter_by(thread_id=thread_id).first()
                if interaction:
                    if interaction.comments is None:
                        interaction.comments = json.dumps([])
                    comments = json.loads(interaction.comments)
                    comments.append(comment)
                    interaction.comments = json.dumps(comments)
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error adding comment to interaction: {e}")
            raise e

    def get_interaction_by_thread_id(self, thread_id):
        try:
            with self.db.get_session() as session:
                return session.query(QAInteraction).filter_by(thread_id=thread_id).first()
        except SQLAlchemyError as e:
            print(f"Error getting interaction by thread ID: {e}")

    def get_interaction_by_interaction_id(self, interaction_id):
        try:
            with self.db.get_session() as session:
                return session.query(QAInteraction).filter_by(id=interaction_id).first()
        except SQLAlchemyError as e:
            print(f"Error getting interaction by interaction ID: {e}")

    def get_interactions_by_interaction_ids(self, interaction_ids):
        try:
            with self.db.get_session() as session:
                return session.query(QAInteraction).filter(QAInteraction.id.in_(interaction_ids)).all()
        except SQLAlchemyError as e:
            print(f"Error getting interactions by interaction IDs: {e}")

    def get_qa_interactions(self):
        try:
            with self.db.get_session() as session:
                return session.query(QAInteraction).all()
        except SQLAlchemyError as e:
            print(f"Error getting QA interactions: {e}")

    def add_embed_to_interaction(self, interaction_id, embed):
        try:
            with self.db.get_session() as session:
                interaction = session.query(QAInteraction).filter_by(id=interaction_id).first()
                if interaction:
                    interaction.embed = json.dumps(embed)
                    interaction.last_embedded = datetime.now(timezone.utc)
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error adding embed to interaction: {e}")
            session.rollback()
            return

    def get_interactions_without_embeds(self):
        try:
            with self.db.get_session() as session:
                return session.query(QAInteraction).filter(
                    (QAInteraction.embed.is_(None)) |
                    (QAInteraction.embed == json.dumps([])) |
                    (QAInteraction.embed == '')
                ).all()
        except SQLAlchemyError as e:
            print(f"Error getting interactions without embeds: {e}")

    def get_interactions_with_embeds(self):
        try:
            with self.db.get_session() as session:
                return session.query(QAInteraction).filter(
                    (QAInteraction.embed.is_not(None)) |
                    (QAInteraction.embed == json.dumps([])) |
                    (QAInteraction.embed == '')
                ).all()
        except SQLAlchemyError as e:
            print(f"Error getting interactions with embeds: {e}")
