"""vector_db.py

This script creates a new collection in Qdrant instance.
"""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from dingus.database.processors import generate_embeddings, generate_id
from dingus.logger import set_logging
from dingus.settings import QDRANT_COLLECTION_NAME, QDRANT_HOST, QDRANT_VECTOR_SIZE

set_logging()

logger = logging.getLogger(__name__)


class QdrantDatabaseClient:
    def __init__(self, host: str, collection_name: str):
        self.QDRANT_HOST = host
        self.collection_name = collection_name
        self.qdrant_client = QdrantClient(self.QDRANT_HOST)

    def setup(self):
        self.create_collection()

    def create_collection(self):
        """
        Create a new collection in Qdrant instance if it doesn't already exist.

        Args:
            collection_name (str): The name of the collection to create.
        Returns:
            None
        """
        try:
            logger.info(f"Creating collection '{self.collection_name}' in Qdrant.")
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=QDRANT_VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"Created collection '{self.collection_name}' in Qdrant.")
        except Exception as e:
            logger.error(f"Failed to create collection '{self.collection_name}'. Error: {e}")

    def upsert(self, data_to_embed: list, payloads: list):
        """
        Insert logs into Qdrant, ensuring no duplicates are added.
        """
        logger.info(f"Upserting {len(data_to_embed)} logs into collection '{self.collection_name}'.")

        ids = [generate_id(payload) for payload in payloads]
        embeddings = generate_embeddings(data_to_embed)

        points = [
            {"id": ids[idx], "vector": embeddings[idx], "payload": payloads[idx]} for idx in range(len(data_to_embed))
        ]

        if points:
            self.qdrant_client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"Upserted {len(points)} logs into collection '{self.collection_name}'.")
        else:
            logger.info("No new logs to insert.")

    def search(self, collection_name: str | None, query_text: str, limit: int = 5) -> list:
        """
        Search in Qdrant.

        Args:
            collection_name (str | None): The name of the collection to search in.
            query_text (str): The query text to search for.
            limit (int): The number of search results to return.
        Returns:
            list: List of search results.
        """
        logger.info(f"Searching for '{query_text}' in collection '{collection_name}'.")
        if collection_name is None:
            collection_name = self.collection_name
        query_embedding = generate_embeddings([query_text])[0]

        search_results = self.qdrant_client.search(
            collection_name=collection_name, query_vector=query_embedding, limit=limit, with_payload=True
        )

        return search_results

    def get_existing_ids(self, ids):
        """
        Check which IDs already exist in Qdrant.
        """
        existing_ids = []
        for _id in ids:
            try:
                res = self.qdrant_client.retrieve(collection_name=self.collection_name, ids=[_id])
                if res:
                    existing_ids.append(_id)
            except Exception as e:
                logger.warning(f"Error checking ID {_id}: {e}")
        logger.info(f"Found {len(existing_ids)} existing logs in collection '{self.collection_name}'.")
        return existing_ids


class QdrantSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            logger.info("Creating new QdrantDatabaseClient instance")
            cls._instance = QdrantDatabaseClient(host=QDRANT_HOST, collection_name=QDRANT_COLLECTION_NAME)
            cls._instance.setup()
        return cls._instance


def get_qdrant_client():
    return QdrantSingleton.get_instance()


if __name__ == "__main__":
    client = QdrantDatabaseClient(host=QDRANT_HOST, collection_name=QDRANT_COLLECTION_NAME)
    client.setup()
    logger.info("QdrantDatabaseClient setup completed")
