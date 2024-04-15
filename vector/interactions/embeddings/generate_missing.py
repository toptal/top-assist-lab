import logging
import time

from api.request import post_request
from configuration import interaction_embeds_endpoint
from database.interaction_manager import QAInteractionManager
from database.database import get_db_session


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def find_missing(session):
    return QAInteractionManager().get_interactions_without_embeds(session)


def submit_request(interaction_id):
    """
    Submit an API request to create interaction embeds.
    :return: None
    """
    post_request(interaction_embeds_endpoint, {"interaction_id": interaction_id})


def generate_missing_embeddings_to_database(retry_limit: int = 3, wait_time: int = 5) -> None:
    """
    Vectorize all interactions without embeds and store them in the database,
    with retries for failed attempts.
    """
    for attempt in range(retry_limit):
        # Retrieve interactions that are still missing embeddings.
        with get_db_session() as session:
            interactions = find_missing(session)

            # If there are no interactions missing embeddings, exit the loop and end the process.
            if not interactions:
                print("All interactions have embeddings. Process complete.")
                return

            print(
                f"Attempt {attempt + 1} of {retry_limit}: Processing {len(interactions)} interactions missing embeddings.")
            for interaction in interactions:
                try:
                    # Attempt to vectorize and store each interaction.
                    submit_request(str(interaction.id))
                    # A brief delay between processing to manage load.
                    time.sleep(0.5)
                except Exception as e:
                    logging.error(f"An error occurred while vectorizing interaction with ID {interaction.id}: {e}")

            print(f"Waiting for {wait_time} seconds for embeddings to be processed...")
            time.sleep(wait_time)

            # After waiting, retrieve the list of interactions still missing embeddings to see if the list has decreased.
            interactions = find_missing(session)
            if not interactions:
                print("All interactions now have embeddings. Process complete.")
                break  # Break out of the loop if there are no more interactions missing embeddings.

            print(f"After attempt {attempt + 1}, {len(interactions)} interactions are still missing embeds.")

    # After exhausting the retry limit, check if there are still interactions without embeddings.
    if interactions:
        print("Some interactions still lack embeddings after all attempts.")
    else:
        print("All interactions now have embeddings. Process complete.")
