# ./oai_assistants/query_assistant_from_documents.py
from typing import List
from open_ai.assistants.utility import extract_assistant_response, initiate_client
from open_ai.assistants.thread_manager import ThreadManager
from open_ai.assistants.assistant_manager import AssistantManager
from configuration import qa_assistant_id
import logging

from database.page_manager import PageManager, PageData

logging.basicConfig(level=logging.INFO)


def format_pages_as_context(pages: List[PageData], max_length=30000, truncation_label=" [Content truncated due to size limit.]"):
    """
    Formats specified files as a context string for referencing in responses,
    ensuring the total context length does not exceed the specified maximum length.

    Args:
        pages (list of PageData): List of pages to be formatted as context.
        max_length (int): The maximum length allowed for the context.
        truncation_label (str): The label to indicate that the content has been truncated.

    Returns:
        str: The formatted context within the maximum length.
    """
    context = ""
    for page in pages:
        title = page.title
        space_key = page.space_key
        file_content = PageManager().format_page_for_llm(page)
        page_data = f"\nDocument Title: {title}\nSpace Key: {space_key}\n\n{file_content}"

        # Truncate and stop if the total length exceeds the maximum allowed
        if len(context) + len(page_data) > max_length:
            available_space = max_length - len(context) - len(truncation_label)
            context += page_data[:available_space] + truncation_label
            break

        context += page_data

    return context


def query_assistant_with_context(question, page_ids, db_session, thread_id=None):
    """
    Queries the assistant with a specific question, after setting up the necessary context by adding relevant files.

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
    assistant = assistant_manager.load_assistant(assistant_id=qa_assistant_id)
    print(f"Assistant loaded: {assistant}\n")

    # Ensure page_ids is a list
    if not isinstance(page_ids, list):
        page_ids = [page_ids]
    print(f"IDs of pages to load in context : {page_ids}\n")

    # Format the context
    pages = PageManager(db_session).find_pages(page_ids)
    context = format_pages_as_context(pages)
    print(f"\n\nContext formatted: {context}\n")

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
    formatted_question = (f"Here is the question and the context\n\n"
                          f"{question}\n\n"
                          f"Context:\n{context}")
    print(f"Formatted question: {formatted_question}\n")

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
