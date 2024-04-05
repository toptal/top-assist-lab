# ./oai_assistants/utility.py
from openai import OpenAI
from credentials import oai_api_key
import os
from configuration import model_id



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


# Sample assistant template used for creating new assistants in the system.
new_assistant_with_tools = {
    "model": model_id,
    "name": "Shams",
    "instructions": """Your role is to serve as a Q&A-based knowledge base assistant.
Prioritize reviewing and referencing the documents provided as context or conversation history.
Generate responses exclusively from the information available in the provided context documents previous context documents and conversation history or context you retrieved using the context retrieval tool.
You can use the retrieval tool multiple times with different queries to satisfy the question.
Refrain from improvisation or sourcing content from other sources.
Utilize logical reasoning and deduction based on the conversation history and previous context.
If you lack an answer from the files and you attempted context retrieval without success, clearly state it and abstain from responding.
Disclose when using external knowledge to explain information beyond the provided files.
Format your responses as follows:
summary: [providing a short to the point answer]
comprehensive answer: [providing a detailed answer]
technical trace: [providing the source of the information]""",
    "description": "The Ultimate Documentation AI",
    "file_ids": [],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_context",
                "description": "Retrieve relevant documents based on a context query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "context_query": {
                            "type": "string",
                            "description": "The query to retrieve relevant context for"
                        },
                        "max_length": {
                            "type": "integer",
                            "description": "The maximum length of the returned context"
                        }
                    },
                    "required": [
                        "context_query"
                    ]
                }
            }
        }
    ]
}

new_assistant = {
    "model": model_id,
    "name": "Shams",
    "instructions": """Your role is to serve as a Q&A-based knowledge base assistant.
Prioritize reviewing and referencing the documents provided as context or conversation history.
Generate responses exclusively from the information available in the provided context documents previous context documents and conversation history or context you retrieved using the context retrieval tool.
You can use the retrieval tool multiple times with different queries to satisfy the question.
Refrain from improvisation or sourcing content from other sources.
Utilize logical reasoning and deduction based on the conversation history and previous context.
If you lack an answer from the files and you attempted context retrieval without success, clearly state it and abstain from responding.
Disclose when using external knowledge to explain information beyond the provided files.
Format your responses as follows:
summary: [providing a short to the point answer]
comprehensive answer: [providing a detailed answer]
technical trace: [providing the source of the information]
document in context: [list of document ids and titles provided in context]""",
    "description": "The Ultimate Documentation AI",
    "file_ids": [],
    "tools": []
}

new_assistant_knwoeldge_gap = {
    "model": model_id,
    "name": "Amar",
    "instructions": """
As an assistant, your primary goal is to sift through user interactions to identify questions that have not been fully answered or areas where the documentation lacks depth. These represent knowledge gaps within our information repository. Your task is to compile these unanswered questions into a structured format, preparing them for submission to domain experts. The insights gained from the experts will be integrated back into our knowledge base, ensuring that future inquiries on these topics can be addressed with enriched context and precision.

Please format your findings into a JSON structure that outlines the unanswered questions, emphasizing their significance and the potential impact of obtaining detailed answers. This structured inquiry will enable us to directly engage with domain experts, fostering a collaborative effort to enhance our collective understanding and documentation.
JSON format:
[
  {
    "Question": "Identify the first key question that remains unanswered from the user interactions.",
    "Relevance": "Provide a brief explanation of how answering this question will contribute to closing the knowledge gap, enhancing our documentation, or offering clearer guidance to users."
  },
  {
    "Question": "Identify the second key question that remains unanswered from the user interactions.",
    "Relevance": "Explain the importance of this question in the context of our knowledge base and the potential benefits of obtaining a comprehensive answer from domain experts."
  }
  // Add additional questions as necessary
]""",
    "description": "The Ultimate Documentation AI",
    "file_ids": [],
    "tools": []
}

