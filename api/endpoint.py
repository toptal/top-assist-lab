# ./api/endpoint.py
from fastapi import FastAPI
import uvicorn
from openai import OpenAI
import threading
from credentials import oai_api_key
from slack.event_consumer import process_question, process_feedback
from pydantic import BaseModel
from configuration import api_host, api_port
import vector.pages
import vector.interactions

processor = FastAPI()

client = OpenAI(api_key=oai_api_key)


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


class EmbedRequest(BaseModel):
    page_id: str


class InteractionEmbedRequest(BaseModel):
    interaction_id: str


@processor.post("/api/v1/questions")
def create_question(question_event: QuestionEvent):
    thread = threading.Thread(target=process_question, args=(question_event,))
    thread.start()
    return {"message": "Question received, processing in background", "data": question_event}


@processor.post("/api/v1/feedback")
def create_feedback(feedback_event: FeedbackEvent):
    """
    Endpoint to initiate the feedback processing in the background.
    :param feedback_event:
    :return:
    """
    thread = threading.Thread(target=process_feedback, args=(feedback_event,))
    thread.start()
    return {"message": "Feedback received, processing in background", "data": feedback_event}


# refactor: should be changed to page_embed
@processor.post("/api/v1/embeds")
def create_embeds(EmbedRequest: EmbedRequest):
    """
    Endpoint to initiate the embedding generation and storage process in the background.
    :param EmbedRequest:
    :return:
    """
    page_id = EmbedRequest.page_id
    thread = threading.Thread(target=vector.pages.generate_one_embedding_to_database, args=(page_id,))
    thread.start()
    return {"message": "Embedding generation initiated, processing in background", "page_id": page_id}


@processor.post("/api/v1/interaction_embeds")
def create_interaction_embeds(InteractionEmbedRequest: InteractionEmbedRequest):
    """
    Endpoint to initiate the embedding generation and storage process in the background.
    :param InteractionEmbedRequest:
    :return:
    """
    interaction_id = InteractionEmbedRequest.interaction_id
    print(f"Received interaction embed request for ID: {interaction_id}")  # Debugging line
    thread = threading.Thread(target=vector.interactions.generate_one_embedding_to_database, args=(interaction_id,))
    thread.start()

    # Make sure to return a response that matches what your client expects
    return {
        "message": "Interaction embedding generation initiated, processing in background",
        "interaction_id": interaction_id
    }


def main():
    """Entry point for starting the FastAPI application."""
    uvicorn.run("api.endpoint:processor", host=api_host, port=api_port, reload=True)


if __name__ == "__main__":
    main()
