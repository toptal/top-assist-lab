import json
import logging
from typing import List, Tuple

from configuration import (
    knowledge_gap_discussions_channel_id,
    knowledge_gap_interaction_retrieval_count,
    quizz_assistant_id,
)
from database.interaction_manager import QAInteractionManager, QAInteraction
from database.quiz_question_manager import QuizQuestionManager
from database.database import get_db_session
from open_ai.assistants.utility import extract_assistant_response, initiate_client
from open_ai.assistants.thread_manager import ThreadManager
from open_ai.assistants.assistant_manager import AssistantManager
from slack.message_manager import post_questions_to_slack
import vector.interactions


logging.basicConfig(level=logging.INFO)


def format_interactions(interactions: List['QAInteraction']) -> Tuple[str, List[str]]:
    """
    Format a list of QAInteraction objects into a human-readable string and collect user IDs.

    Each interaction contains a question, an answer, and optional comments.
    Comments are expected to be in JSON format and will be loaded accordingly.
    If comments deserialization fails, it defaults to an empty list.

    Parameters:
    interactions (List[QAInteraction]): A list of QAInteraction objects.

    Returns:
    Tuple[str, List[str]]: A tuple containing a string of formatted interactions and a list of user IDs.
    """
    formatted_interactions = []
    user_ids = []

    for interaction in interactions:
        # Extract attributes
        question = f"Question: {interaction.question_text}"
        answer = f"Answer: {interaction.answer_text}"
        user_id = interaction.slack_user_id

        # Determine whether comments is a string (JSON) or already a list
        comments = []
        if isinstance(interaction.comments, str):
            try:
                comments = json.loads(interaction.comments)
            except json.JSONDecodeError:
                pass  # Default to an empty list if deserialization fails

        # Format comments, handling both empty lists and lists of dictionaries
        comments_formatted = "Comments: "
        if comments:
            comments_formatted += "; ".join([f"{comment.get('text', 'No text')}" for comment in comments])
        else:
            comments_formatted += "No comments"

        # Combine question, answer, and comments for this interaction
        formatted_interaction = f"{question}\n{answer}\n{comments_formatted}\n---\n"
        formatted_interactions.append(formatted_interaction)
        user_ids.append(user_id)

    all_interactions = "\n".join(formatted_interactions)
    user_ids = list(set(user_ids))
    return all_interactions, user_ids


def query_assistant_with_context(context, formatted_interactions, thread_id=None):
    """
    Queries the assistant with a specific question, after setting up the necessary context by adding relevant interactions.

    Args:
    question (str): The question to be asked.
    page_ids (list): A list of page IDs representing the files to be added to the assistant's context.
    thread_id (str, optional): The ID of an existing thread to continue the conversation. Default is None.

    Returns:
    list: A list of messages, including the assistant's response to the question.
    """

    # Initiate the client
    client = initiate_client()
    print(f"Client initiated: {client}\n")
    assistant_manager = AssistantManager(client)
    print(f"Assistant manager initiated: {assistant_manager}\n")

    # Retrieve the assistant instance
    assistant = assistant_manager.load_assistant(assistant_id=quizz_assistant_id)
    print(f"Assistant loaded: {assistant}\n")

    # Initialize ThreadManager with or without an existing thread_id
    thread_manager = ThreadManager(client, assistant.id, thread_id)
    print(f"Thread manager initiated: {thread_manager}\n")

    # If no thread_id was provided, create a new thread
    if thread_id is None:
        thread_manager.create_thread()
        print(f"Thread created: {thread_manager.thread_id}\n")
    else:
        print(f"Thread loaded with the following ID: {thread_id}\n")

    # Format the question with context and query the assistant

    formatted_question = (f"""After analyzing the provided questions_text,
    Keep only the questions that are related to {context}
    From these identify those that were not provided a satisfactory answer in the answer_text
    These questions should reflect gaps in our current knowledge or documentation.
    Compile these questions so we can ask them to the domain experts and recover that knowledge.
    Provide them strictly in a JSON array, following the specified structure.
    Each entry should include the question and a brief explanation of why it was
    included, how it relates to the {context} domain, and what part of the question wasn't covered.
    Only include questions relevant to this domain:{context}\n
    f"Context:{formatted_interactions}\n
    """)

    print(f"Formatted question:\n{formatted_question}\n")

    # Query the assistant
    messages, thread_id = thread_manager.add_message_and_wait_for_reply(formatted_question)
    print(f"The thread_id is: {thread_id}\n Messages received: {messages}\n")
    if messages and messages.data:
        assistant_response = extract_assistant_response(messages)
        print(f"Assistant full response: {assistant_response}\n")
    else:
        assistant_response = "No response received."
        print(f"No response received.\n")

    return assistant_response, thread_id


def process_and_store_questions(assistant_response_json):
    """
    Processes the JSON response from the assistant, extracts questions, stores them in the database,
    and collects the QuizQuestionDTO objects.

    Args:
        assistant_response_json (str): JSON string containing the assistant's response.

    Returns:
        list[QuizQuestionDTO]: A list of QuizQuestionDTO objects added to the database.
    """
    try:
        questions_data = json.loads(assistant_response_json)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return []

    quiz_question_dtos = []
    for item in questions_data:
        question_text = item.get("Question")
        if question_text:
            quiz_question_dto = QuizQuestionManager().add_quiz_question(question_text=question_text)
            if quiz_question_dto:
                quiz_question_dtos.append(quiz_question_dto)
    return quiz_question_dtos


def strip_json(assistant_response: str):
    """
    Receives the response and extracts only the JSON from it, then returns the JSON.
    This function assumes the JSON content is wrapped in triple backticks with 'json' as a language identifier.

    Args:
        assistant_response (str): The full response from the assistant, potentially including the JSON content.

    Returns:
        str: The extracted JSON content as a string. Returns an empty JSON array '[]' if extraction fails.
    """
    try:
        json_content = assistant_response

        # Strip markdown quotes if any
        if "```json" in assistant_response:
            start_index = assistant_response.index("```json") + len("```json")
            end_index = assistant_response.index("```", start_index)
            json_content = json_content[start_index:end_index]

        json_content = json_content.strip()
        # Basic validation to check if it's likely to be JSON
        if json_content.startswith("[") and json_content.endswith("]"):
            return json_content
        else:
            logging.error("Extracted content does not appear to be valid JSON.")
            return "[]"
    except ValueError as e:
        logging.error(f"Error extracting JSON from response: {e}")
        return "[]"


def identify_knowledge_gaps(context):
    query = f"no information in context: {context}"
    interaction_ids = vector.interactions.retrieve_relevant_ids(query, count=knowledge_gap_interaction_retrieval_count)
    with get_db_session() as session:
        relevant_qa_interactions = QAInteractionManager().get_interactions_by_interaction_ids(session, interaction_ids)
        formatted_interactions, user_ids = format_interactions(relevant_qa_interactions)
    assistant_response, thread_ids = query_assistant_with_context(context, formatted_interactions)
    questions_json = strip_json(assistant_response)
    quiz_question_dtos = process_and_store_questions(questions_json)

    # Updated to print IDs of stored questions
    print(f"Stored questions with IDs: {[q.id for q in quiz_question_dtos]}")

    # Updated function call to match the expected input
    post_questions_to_slack(channel_id=knowledge_gap_discussions_channel_id, quiz_question_dtos=quiz_question_dtos, user_ids=user_ids)
