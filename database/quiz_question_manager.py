from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from interactions.quiz_question_dto import QuizQuestionDTO
from models.quiz_question import QuizQuestion


class QuizQuestionManager:
    def __init__(self, db_session):
        self.db_session = db_session

    def add_quiz_question(self, question_text):
        with self.db_session as session:
            new_question = QuizQuestion().create_or_update(session,
                                                           question_text=question_text,
                                                           posted_on_slack=datetime.now(timezone.utc))

            print(f"New question ID: {new_question.id}")
            dto = QuizQuestionDTO(
                question_id=new_question.id,
                question_text=new_question.question_text,
                thread_id=new_question.thread_id,
                summary=new_question.summary,
                posted_on_slack=new_question.posted_on_slack,
                posted_on_confluence=new_question.posted_on_confluence
            )

            print(f"DTO: {dto.id}")
            return dto

    def update_with_summary(self, question_id, summary):
        with self.db_session as session:
            QuizQuestion().create_or_update(session, id=question_id, summary=summary)
            print(f"Summary updated for question with ID {question_id}")

    def update_with_summary_by_thread_id(self, thread_id, summary):
        with self.db_session as session:
            QuizQuestion().create_or_update(session, thread_id=thread_id, summary=summary)
            print(f"Summary updated for question with thread ID {thread_id}")

    def update_with_thread_id(self, question_id, thread_id):
        with self.db_session as session:
            QuizQuestion().create_or_update(session,
                                            id=question_id,
                                            thread_id=thread_id,
                                            posted_on_slack=datetime.now(timezone.utc))
            print(f"Updated question with ID {question_id} with thread ID {thread_id}")

    def get_unposted_questions_timestamps(self):
        try:
            with self.db_session as session:
                questions = session.query(QuizQuestion).filter_by(posted_on_confluence=None).all()
                return [question.thread_id for question in questions]
        except SQLAlchemyError as e:
            print(f"Error getting unposted questions: {e}")
            return None
