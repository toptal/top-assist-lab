# ./configuration.py
import logging
from pathlib import Path
import os


def get_project_root() -> str:
    """Get the project root directory as a string.

    Assumes this script is located in the project root.
    """
    # Get the directory of the current script
    project_root = Path(__file__).parent
    # Convert the Path object to a string and return it
    return str(project_root)


# DB configuration
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_NAME = os.environ.get("DB_NAME")
DB_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Chroma vector database configuration
chroma_host = os.environ.get("CHROMA_HOST")
chroma_port = int(os.environ.get("CHROMA_PORT"))
chroma_database = os.environ.get("CHROMA_DATABASE")
vector_collection_pages = "pages"
vector_collection_interactions = "interactions"

# API configuration
api_host = os.environ.get("NUR_API_HOST")
api_port = int(os.environ.get("NUR_API_PORT"))
embeds_endpoint = f'http://{api_host}:{api_port}/api/v1/embeds'
feedback_endpoint = f'http://{api_host}:{api_port}/api/v1/feedback'
questions_endpoint = f'http://{api_host}:{api_port}/api/v1/questions'
interaction_embeds_endpoint = f'http://{api_host}:{api_port}/api/v1/interaction_embeds'


logging.basicConfig(level=logging.INFO)

project_path = get_project_root()
logging.log(logging.DEBUG, f"Project path: {project_path}")

chart_folder_path = os.path.join(project_path, "content", "charts")
sql_file_path = os.path.join(project_path, "content", "database", "confluence_pages_sql.db")
db_url = 'sqlite:///' + sql_file_path


# Assistant IDs
qa_assistant_id = os.environ.get("OPENAI_ASSISTANT_ID_QA")
quizz_assistant_id = os.environ.get("OPENAI_ASSISTANT_ID_KNOWLEDGE_GAP")

# Model IDs
# Doesn't apply for assistants
# Assistants have as part of the assistant the model id
gpt_3t = ""
gpt_4t = "gpt-4-turbo-preview"
model_id = gpt_4t

# Embedding model IDs
embedding_model_id_latest_large = "text-embedding-3-large"
embedding_model_id_latest_small = "text-embedding-3-small"
embedding_model_id_ada = "text-embedding-ada-002"
embedding_model_id = embedding_model_id_latest_large

# page retrieval for answering questions
# document count is recommended from 3 to 15 where 3 is minimum cost and 15 is maximum comprehensive answer
question_context_pages_count = 2
# interaction retrieval for identifying knowledge gaps interaction_retrieval_count is recommended from 3 to 10 where
# 3 is minimum cost and 10 is maximum comprehensive list of questions
knowledge_gap_interaction_retrieval_count = 5


# System Knowledge space name on Confluence
system_knowledge_space_private = "Nur Documentation"
system_confluence_knowledge_space = system_knowledge_space_private


# Knowledge collection Slack channel ids
knowledge_gap_discussions_channel_id = os.environ.get("SLACK_CHANNEL_ID_KNOWLEDGE_GAP_DISCUSSIONS")

# Authorized Slack environments
slack_allow_enterprise_id = os.environ.get("SLACK_ALLOW_ENTERPRISE_ID")
slack_allow_team_id = os.environ.get("SLACK_ALLOW_TEAM_ID")
