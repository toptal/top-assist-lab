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
        QAInteraction().create_or_update(
            self.db_session,
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

    def add_comment_to_interaction(self, thread_id, comment):
        interaction = self.get_interaction_by_thread_id(thread_id)
        if interaction:
            if interaction.comments is None:
                interaction.comments = json.dumps([])
            comments = json.loads(interaction.comments)
            comments.append(comment)
            interaction.comments = json.dumps(comments)
        interaction.update(self.db_session)

    def get_interaction_by_thread_id(self, thread_id):
        return QAInteraction().create_or_update(self.db_session, thread_id=thread_id)

    def get_interaction_by_interaction_id(self, interaction_id):
        return QAInteraction().create_or_update(self.db_session, id=interaction_id)

    def get_interactions_by_interaction_ids(self, interaction_ids):
        return self.db_session.query(QAInteraction).filter(QAInteraction.id.in_(interaction_ids)).all()

    def get_qa_interactions(self):
        return self.db_session.query(QAInteraction).all()

    def add_embed_to_interaction(self, interaction_id, embed):
        QAInteraction().create_or_update(self.db_session,
                                         id=interaction_id,
                                         embed=json.dumps(embed),
                                         last_embedded=datetime.now(timezone.utc))

    def get_interactions_without_embeds(self):
        return self.db_session.query(QAInteraction).filter(
            (QAInteraction.embed.is_(None)) |
            (QAInteraction.embed == json.dumps([])) |
            (QAInteraction.embed == '')
        ).all()

    def get_interactions_with_embeds(self):
        return self.db_session.query(QAInteraction).filter(
            (QAInteraction.embed.is_not(None)) |
            (QAInteraction.embed == json.dumps([])) |
            (QAInteraction.embed == '')
        ).all()
