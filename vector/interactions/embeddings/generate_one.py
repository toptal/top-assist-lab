import json
import logging

from configuration import embedding_model_id
from database.interaction_manager import QAInteractionManager
from open_ai.embedding.embed_manager import embed_text


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def format_comment(raw_comment):
    if raw_comment is None:
        return "No comments available."

    try:
        comment_data = json.loads(raw_comment)
    except json.JSONDecodeError:
        return "Invalid comment format."

    formatted_comments = []
    for comment in comment_data:
        text = comment["text"].replace('\n', ' ').strip()
        user = comment["user"]
        timestamp = comment["timestamp"]
        formatted_comments.append(f"{text} (Comment by {user} on {timestamp})")
    return ' '.join(formatted_comments)

def format_interaction(interaction):
    """
    Create a formatted string containing the page title and content for a given interaction.

    Args:
    interaction (QAInteraction): A QAInteraction object.

    Returns:
    str: A string containing the formatted page title and content.
    """
    # Create the page title and content
    comments = format_comment(interaction.comments)
    formatted_interaction = f"""
        <h2>Question</h2>
        <p>{interaction.question_text}</p>
        <h2>Answer</h2>
        <p>{interaction.answer_text}</p>
        <h2>Comments</h2>
        <p>{comments}</p>
        """
    return formatted_interaction


def generate_one_embedding_to_database(interaction_id):
    interaction = QAInteractionManager().get_interaction_by_interaction_id(interaction_id)
    if interaction:
        formatted_interaction = format_interaction(interaction)
        embed = embed_text(formatted_interaction, model=embedding_model_id)
        QAInteractionManager().add_embed_to_interaction(interaction_id, embed)
        logging.info(f"Interaction with ID {interaction_id} vectorized and stored in the database.")
    else:
        logging.error(f"No interaction found for ID {interaction_id}")
    return None
