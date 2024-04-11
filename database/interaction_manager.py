# ./database/interaction_manager.py
from datetime import datetime, timezone
from models.qa_interaction import QAInteraction
import json


class QAInteractionManager:
    def __init__(self, session):
        self.session = session

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
        self.session.add(interaction)
        self.session.commit()

    def add_comment_to_interaction(self, thread_id, comment):
        interaction = self.get_interaction_by_thread_id(thread_id)
        if interaction:
            if interaction.comments is None:
                interaction.comments = json.dumps([])
            comments = json.loads(interaction.comments)
            comments.append(comment)
            interaction.comments = json.dumps(comments)
            self.session.commit()

    def get_interaction_by_thread_id(self, thread_id):
        return self.session.query(QAInteraction).filter_by(thread_id=thread_id).first()

    def get_interaction_by_interaction_id(self, interaction_id):
        return self.session.query(QAInteraction).filter_by(id=interaction_id).first()

    def get_interactions_by_interaction_ids(self, interaction_ids):
        return self.session.query(QAInteraction).filter(QAInteraction.id.in_(interaction_ids)).all()

    def get_qa_interactions(self):
        return self.session.query(QAInteraction).all()

    def add_embed_to_interaction(self, interaction_id, embed):
        interaction = self.session.query(QAInteraction).filter_by(id=interaction_id).first()
        if interaction:
            interaction.embed = json.dumps(embed)
            interaction.last_embedded = datetime.now(timezone.utc)
            self.session.commit()

    def get_interactions_without_embeds(self):
        return self.session.query(QAInteraction).filter(
            (QAInteraction.embed.is_(None)) |
            (QAInteraction.embed == json.dumps([])) |
            (QAInteraction.embed == '')
        ).all()

    def get_interactions_with_embeds(self):
        return self.session.query(QAInteraction).filter(
            (QAInteraction.embed.is_not(None)) |
            (QAInteraction.embed == json.dumps([])) |
            (QAInteraction.embed == '')
        ).all()
