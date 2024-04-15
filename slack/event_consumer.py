# ./slack/event_consumer.py

# was a built as a publisher before we migrated to using API calls. It was used to publish events to the persist queue.
# some of its code is still used in the current implementation and should be extracted and the publisher part discarded.

import logging
from datetime import datetime
from pydantic import BaseModel
from slack_sdk import WebClient

from configuration import question_context_pages_count
from credentials import slack_bot_user_oauth_token
from database.interaction_manager import QAInteractionManager
from database.score_manager import ScoreManager
from open_ai.assistants.query_assistant_from_documents import query_assistant_with_context
from database.database import get_db_session
from slack_sdk.errors import SlackApiError
import vector.pages


class QuestionEvent(BaseModel):
    text: str
    ts: str
    thread_ts: str
    channel: str
    user: str


class FeedbackEvent(BaseModel):
    text: str
    ts: str
    thread_ts: str
    channel: str
    user: str


def get_user_name_from_id(slack_web_client, user_id):
    try:
        response = slack_web_client.users_info(user=user_id)
        if response and response['user']['name']:
            return response['user']['name']
    except SlackApiError as e:
        print(f"Error fetching user name: {e.response['error']}")
    return None


class EventConsumer:
    def __init__(self):
        self.web_client = WebClient(token=slack_bot_user_oauth_token)
        logging.log(logging.DEBUG, f"Slack Event Consumer initiated successfully")

    def add_question_and_response_to_database(self, question_event, response_text, assistant_thread_id):
        QAInteractionManager().add_question_and_answer(question=question_event.text,
                                                       answer=response_text,
                                                       thread_id=question_event.ts,
                                                       assistant_thread_id=assistant_thread_id,
                                                       channel_id=question_event.channel,
                                                       question_ts=datetime.fromtimestamp(
                                                           float(question_event.ts)),
                                                       answer_ts=datetime.now(),
                                                       slack_user_id=question_event.user)

        print(
            f"\n\nQuestion and answer stored in the database: question: {question_event.dict()},\nAnswer: {response_text},\nAssistant_id {assistant_thread_id}\n\n")

    def process_question(self, question_event: QuestionEvent):  # TODO: Refactor this method
        channel_id = question_event.channel
        message_ts = question_event.ts

        try:
            context_page_ids = vector.pages.retrieve_relevant_ids(question_event.text,
                                                                  count=question_context_pages_count)
            response_text, assistant_thread_id = query_assistant_with_context(question_event.text,
                                                                              context_page_ids,
                                                                              None)
        except Exception as e:
            print(f"Error processing question: {e}")
            response_text = None

        if response_text:
            print(f"Response from assistant: {response_text}\n")
            try:
                self.add_question_and_response_to_database(question_event,
                                                           response_text,
                                                           assistant_thread_id=assistant_thread_id)
                try:
                    ScoreManager().add_or_update_score(slack_user_id=question_event.user, category='seeker')
                    print(f"Score updated for user {question_event.user}")
                except Exception as e:
                    print(f"Error updating score for user {question_event.user}: {e}")
                self.web_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=message_ts)
                print(f"\nResponse posted to Slack thread: {message_ts}\n")
            except Exception as e:
                print(f"Error registering message as processed, adding to db and responding to the question on slack: {e}")

    def generate_extended_context_query(self, existing_interaction, feedback_text):
        extended_context_query = ""
        if existing_interaction:
            extended_context_query = f"Follow up: {feedback_text}, Initial question: {existing_interaction.question_text}, Initial answer: {existing_interaction.answer_text}"
        return extended_context_query

    def process_feedback(self, feedback_event: FeedbackEvent):  # TODO: Refactor this method
        channel_id = feedback_event.channel
        message_ts = feedback_event.ts
        thread_ts = feedback_event.thread_ts
        response_text = None

        try:
            with get_db_session() as session:
                existing_interaction = QAInteractionManager().get_interaction_by_thread_id(session, thread_ts)
                assistant_thread_id = existing_interaction.assistant_thread_id if existing_interaction else None
                print(f"\n\nExisting interaction found: {existing_interaction}\n\n")
        except Exception as e:
            print(f"Error getting existing interaction from the database: {e}")
            existing_interaction = None
            assistant_thread_id = None


        if existing_interaction:
            extended_context_query = self.generate_extended_context_query(existing_interaction, feedback_event.text)
            print(f"\n\nExtended context: {extended_context_query}\n\n")
            page_ids = vector.pages.retrieve_relevant_ids(extended_context_query, count=question_context_pages_count)
            try:
                response_text, assistant_thread_id = query_assistant_with_context(feedback_event.text,
                                                                                  page_ids,
                                                                                  assistant_thread_id)
            except Exception as e:
                print(f"Error processing feedback: {e}")
                response_text = None

        if response_text:
            print(f"Response from assistant: {response_text}\n")
            timestamp_str = datetime.now().isoformat()
            comment = {"text": feedback_event.text, "user": feedback_event.user, "timestamp": timestamp_str,
                       "assistant response": response_text}
            QAInteractionManager().add_comment_to_interaction(thread_id=thread_ts, comment=comment)
            print(f"Feedback appended to the interaction in the database: {feedback_event.dict()}\n")
            self.web_client.chat_postMessage(channel=channel_id, text=response_text, thread_ts=thread_ts)
            print(f"Feedback response posted to Slack thread: {message_ts}\n")
        else:
            print(f"No response generated for feedback: {feedback_event.dict()}\n")


def process_question(question_event: QuestionEvent):
    """Directly processes a question event without using the queue."""
    EventConsumer().process_question(question_event)


def process_feedback(feedback_event: FeedbackEvent):
    """Directly processes a feedback event without using the queue."""
    EventConsumer().process_feedback(feedback_event)
