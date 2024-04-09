from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from interactions.quiz_question_dto import QuizQuestionDTO
from models.quiz_question import QuizQuestion
from database.database import Database


class QuizQuestionManager:
    def __init__(self):
        self.db = Database()

    def add_quiz_question(self, question_text):
        try:
            with self.db.get_session() as session:
                new_question = QuizQuestion(question_text=question_text, posted_on_slack=datetime.now(timezone.utc))
                self.db.add_object(new_question)
                # Convert and return a QuizQuestionDTO object
                return QuizQuestionDTO(
                    id=new_question.id,
                    question_text=new_question.question_text,
                    thread_id=new_question.thread_id,
                    summary=new_question.summary,
                    posted_on_slack=new_question.posted_on_slack,
                    posted_on_confluence=new_question.posted_on_confluence
                )
        except SQLAlchemyError as e:
            print(f"Error adding quiz question: {e}")
            return None

    def update_with_summary(self, question_id, summary):
        try:
            with self.db.get_session() as session:
                question = session.query(QuizQuestion).filter_by(id=question_id).first()
                if question:
                    question.summary = summary
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error updating quiz question with summary: {e}")

    def update_with_summary_by_thread_id(self, thread_id, summary):
        try:
            with self.db.get_session() as session:
                question = session.query(QuizQuestion).filter_by(thread_id=thread_id).first()
                print(f"question: {question}")
                if question:
                    question.summary = summary
                    session.commit()
                    print(f"Updated question with thread ID {thread_id} with summary: {summary}")
        except SQLAlchemyError as e:
            print(f"Error updating quiz question with summary: {e}")

    def update_with_thread_id(self, question_id, thread_id):
        try:
            with self.db.get_session() as session:
                question = session.query(QuizQuestion).filter_by(id=question_id).first()
                if question:
                    question.thread_id = thread_id
                    # question.posted_on_slack = datetime.now(timezone.utc)
                    session.commit()
        except SQLAlchemyError as e:
            print(f"Error updating quiz question with thread ID: {e}")

    def get_unposted_questions_timestamps(self):
        try:
            with self.db.get_session() as session:
                questions = session.query(QuizQuestion).filter_by(posted_on_confluence=None).all()
                return [question.thread_id for question in questions]
        except SQLAlchemyError as e:
            print(f"Error getting unposted questions: {e}")
            return None
