import chromadb

from configuration import chroma_host, chroma_port, chroma_database


def get_client() -> chromadb.ClientAPI:
    """
    Get a connection to the ChromaDB database.
    """
    return chromadb.HttpClient(
        host=chroma_host,
        port=chroma_port,
        database=chroma_database,
    )
