"""vectors.py

Tools for interacting with vector databases.
"""

import logging

from dingus.database.vector_db import get_qdrant_client
from dingus.settings import QDRANT_COLLECTION_NAME
from dingus.tools.fetch_logs import get_loki_streams

logger = logging.getLogger(__name__)


def upsert_logs(log_source: str = "loki", vector_db: str = "qdrant") -> None:
    """
    Fetch logs from a specified source and upsert them into a vector database.

    Args:
        log_source (str): The source of logs. Default is "loki".
        vector_db (str): The vector database to use. Default is "qdrant".

    Raises:
        NotImplementedError: If the log source or vector database is not supported.
        ValueError: If no logs are retrieved.
        TypeError: If logs cannot be processed correctly.
    """
    logger.info("Getting Logs for Upserting")
    if log_source == "loki":
        data, payloads = get_loki_streams()
    else:
        logger.error(f"Error: log_source {log_source} not implemented")
        raise NotImplementedError(f"Error: log_source {log_source} not implemented")

    if vector_db == "qdrant":
        logger.info("Setting up Qdrant Database Client")
        get_qdrant_client().upsert(data_to_embed=data, payloads=payloads)
    else:
        logger.error(f"Error: vector_db {vector_db} not implemented")
        raise NotImplementedError(f"Error: vector_db {vector_db} not implemented")


def search_logs(query_text: str, vector_db: str = "qdrant", limit: int = 20) -> list[dict]:
    """
    Search logs in a vector database using a query.

    Args:
        query_text (str): The search query.
        vector_db (str): The vector database to search in. Default is "qdrant".
        limit (int): Limit the number of items returned in the search.

    Returns:
        list[dict]: The search results, or None if an error occurs.

    Raises:
        NotImplementedError: If the specified vector database is not supported.
    """
    if vector_db == "qdrant":
        search_response = get_qdrant_client().search(
            collection_name=QDRANT_COLLECTION_NAME, query_text=query_text, limit=limit
        )
    else:
        logger.error(f"Error: vector_db {vector_db} not implemented")
        raise NotImplementedError(f"Error: vector_db {vector_db} not implemented")

    if search_response is None:
        logger.error("Error getting vector search response: None returned")
        search_response = []

    return search_response
