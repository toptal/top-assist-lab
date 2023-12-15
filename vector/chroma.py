from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from credentials import oai_api_key
from configuration import vector_folder_path
from database.confluence_database import get_page_data_from_db
from database.confluence_database import update_embed_date


def vectorize_documents(all_documents, page_ids):
    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory=vector_folder_path)

    # Prepare page_ids to be added as metadata
    metadatas = [{"page_id": page_id} for page_id in page_ids]

    # Add texts to the vectorstore
    vectordb.add_texts(texts=all_documents, metadatas=metadatas)

    # Persist the database
    vectordb.persist()

    # Update the last_embedded timestamp in the database
    update_embed_date(page_ids)

def add_to_vector():
    all_documents, page_ids = get_page_data_from_db()

    # Check if the lists are empty
    if not all_documents or not page_ids:
        print("No new or updated documents to vectorize.")
        return []

    vectorize_documents(all_documents, page_ids)
    print(f'Vectorized {len(all_documents)} documents.')
    print(f'Vectorized page ids: {page_ids}')
    return page_ids


def retrieve_relevant_documents(question):
    # Initialize OpenAI embeddings with the API key
    embedding = OpenAIEmbeddings(openai_api_key=oai_api_key)

    # Create the Chroma vectorstore with the embedding function
    vectordb = Chroma(embedding_function=embedding, persist_directory=vector_folder_path)

    # Embed the query text using the embedding function
    query_embedding = embedding.embed_query(question)

    # Perform a similarity search in the vectorstore
    similar_documents = vectordb.similarity_search_by_vector(query_embedding)

    # Process and return the results along with their metadata
    results = []
    for doc in similar_documents:
        result = {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }
        results.append(result)
    document_ids = [doc.metadata.get('page_id') for doc in similar_documents if doc.metadata]

    return document_ids


if __name__ == '__main__':
    vectorized_page_ids = add_to_vector()
    question = "do we use any reminder functionality in our solution?"
    relevant_document_ids = retrieve_relevant_documents(question)
    for result in relevant_document_ids:
        print(result)
        print("---------------------------------------------------")
