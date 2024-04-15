# ./database/interaction_manager.py
from datetime import datetime, timezone
from models.qa_interaction import QAInteraction
from database.database import get_db_session
import json


class QAInteractionManager:
    def __init__(self):
        pass

    def add_question_and_answer(self, question, answer, thread_id, assistant_thread_id, channel_id, question_ts,
                                answer_ts, slack_user_id):
        with get_db_session() as session:
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
            session.add(interaction)

    def add_comment_to_interaction(self, thread_id, comment):
        with get_db_session() as session:
            interaction = self.get_interaction_by_thread_id(session, thread_id)
            if interaction:
                if interaction.comments is None:
                    interaction.comments = json.dumps([])
                comments = json.loads(interaction.comments)
                comments.append(comment)
                interaction.comments = json.dumps(comments)

    def get_interaction_by_thread_id(self, session, thread_id):
        return session.query(QAInteraction).filter_by(thread_id=thread_id).first()

    def get_interaction_by_interaction_id(self, session,  interaction_id):
        return session.query(QAInteraction).filter_by(id=interaction_id).first()

    def get_interactions_by_interaction_ids(self, session, interaction_ids):
        return session.query(QAInteraction).filter(QAInteraction.id.in_(interaction_ids)).all()

    def get_qa_interactions(self, session):
        return session.query(QAInteraction).all()

    def add_embed_to_interaction(self, session, interaction_id, embed):
        interaction = session.query(QAInteraction).filter_by(id=interaction_id).first()
        if interaction:
            interaction.embed = json.dumps(embed)
            interaction.last_embedded = datetime.now(timezone.utc)

    def get_interactions_without_embeds(self, session):
        return session.query(QAInteraction).filter(
            (QAInteraction.embed.is_(None)) |
            (QAInteraction.embed == json.dumps([])) |
            (QAInteraction.embed == '')
        ).all()

    def get_interactions_with_embeds(self, session):
        return session.query(QAInteraction).filter(
            (QAInteraction.embed.is_not(None)) |
            (QAInteraction.embed == json.dumps([])) |
            (QAInteraction.embed == '')
        ).all()
