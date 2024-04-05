# ./oai_assistants/utility.py
from openai import OpenAI
from credentials import oai_api_key


def initiate_client():
    """
    Initializes and returns an OpenAI client using the provided API key.

    Returns:
    OpenAI: An instance of the OpenAI client configured with the specified API key.
    """
    client = OpenAI(api_key=oai_api_key)
    return client


def extract_assistant_response(messages) -> str:
    """
    Extracts the assistant's reply from a list of messages.

    Args:
    messages (list): A list of messages, including the assistant's response to a question.

    Returns:
    str: The assistant's reply extracted from the messages.
    """
    result = []
    # Messages are returned in reverse chronological order
    # so to build a full reply we should take most recent
    # assistant messages block and concatenate them in reverse order
    for message in messages.data:
        if message.role != 'assistant':
            break
        result.append(message.content[0].text.value)
    result.reverse()
    result = '\n'.join(result)
    return result
