from datetime import datetime, timezone
from interactions.quiz_question_dto import QuizQuestionDTO
from models.quiz_question import QuizQuestion
from database.database import get_db_session


class QuizQuestionManager:
    def __init__(self):
        pass

    def add_quiz_question(self, question_text):
        with get_db_session() as session:
            new_question = QuizQuestion(question_text=question_text, posted_on_slack=datetime.now(timezone.utc))
            session.add(new_question)
            session.flush()

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

    def update_with_summary_by_thread_id(self, thread_id, summary):
        with get_db_session() as session:
            question = session.query(QuizQuestion).filter_by(thread_id=thread_id).first()
            print(f"question: {question}")
            if question:
                question.summary = summary
                print(f"Updated question with thread ID {thread_id} with summary: {summary}")

    def update_with_thread_id(self, question_id, thread_id):
        with get_db_session() as session:
            question = session.query(QuizQuestion).filter_by(id=question_id).first()
            if question:
                question.thread_id = thread_id
                question.posted_on_slack = datetime.now(timezone.utc)

    def get_unposted_questions_timestamps(self):
        with get_db_session() as session:
            questions = session.query(QuizQuestion).filter_by(posted_on_confluence=None).all()
            return [question.thread_id for question in questions]
