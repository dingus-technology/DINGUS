"""setup.py

This script creates a new collection in Qdrant instance.
"""

import logging


from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import json
from dingus.database.processors import generate_embeddings
from dingus.settings import QDRANT_HOST

VECTOR_SIZE = 384  # 384D for MiniLM


logger = logging.getLogger(__name__)


class QdrantDatabaseClient:
    def __init__(self, host: str = QDRANT_HOST, collection_name: str = "logs_index"):
        self.QDRANT_HOST = host
        self.collection_name = collection_name
        self.qdrant_client = QdrantClient(self.QDRANT_HOST)

        self.setup()

    def setup(self):
         # TODO: get direct from logs API.
        # with open("data/loki_stream_5k.json") as f:
            # logs = json.load(f)
        logs = [
            {
                "stream": {
                    "filename": "sanitised_data.py",
                    "job": "cpu_monitor",
                    "level": "WARNING",
                    "line": "64",
                    "logger": "cpu_monitor_logger",
                    "message": "High CPU load detected",
                    "service": "monitoring-app",
                    "service_name": "monitoring-app",
                    "severity": "warning",
                    "timestamp": "2025-02-21 15:12:20",
                },
                "values": [
                    [
                        "1740150740271497984",
                        '{"timestamp": "2025-02-21 15:12:20", "level": "WARNING", "filename": "sanitised_data.py", "line": 64, "message": "High CPU load detected"}',
                    ]
                ],
            },
        ]

        data = [log.get("stream",{}).get("message", None) for log in logs]
        payloads = [log.get("stream",{}) for log in logs]

        self.create_collection()
        self.upsert(data_to_embed=data, payloads=payloads)

    def create_collection(self):
        """
        Create a new collection in Qdrant instance.

        Args:
            collection_name (str): The name of the collection to create.
        Returns:
            None
        """
        try:
            logger.info(f"Creating collection '{self.collection_name}' in Qdrant.")
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"Created collection '{self.collection_name}' in Qdrant.")
        except Exception as e:
            logger.error(f"Failed to create collection '{self.collection_name}'. Error: {e}")

    def upsert(self, data_to_embed: list, payloads: list):
        """
        Insert logs into Qdrant.

        Args:
            data_to_embed (str): The name of the collection to insert into.
            data (list): List of points to insert.
        Returns:
            None
        """

        logger.info(f"Upserting {len(data_to_embed)} logs into collection '{self.collection_name}'.")

        embeddings = generate_embeddings(data_to_embed)

        points = [
            {"id": idx, "vector": embeddings[idx].tolist(), "payload": payloads[idx]}
            for idx in range(len(data_to_embed))
        ]
        self.qdrant_client.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"Upserted {len(points)} logs into collection '{self.collection_name}'.")

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


def cli():

    logs = [
        {
            "stream": {
                "filename": "sanitised_data.py",
                "job": "cpu_monitor",
                "level": "WARNING",
                "line": "64",
                "logger": "cpu_monitor_logger",
                "message": "High CPU load detected",
                "service": "monitoring-app",
                "service_name": "monitoring-app",
                "severity": "warning",
                "timestamp": "2025-02-21 15:12:20",
            },
            "values": [
                [
                    "1740150740271497984",
                    '{"timestamp": "2025-02-21 15:12:20", "level": "WARNING", "filename": "sanitised_data.py", "line": 64, "message": "High CPU load detected"}',
                ]
            ],
        },
    ]

    data = [log["stream"]["message"] for log in logs]
    payloads = [log["stream"] for log in logs]

    qdrant_client = QdrantDatabaseClient()
    qdrant_client.create_collection()
    qdrant_client.upsert(data_to_embed=data, payloads=payloads)

    while True:
        user_input = input("\nAsk a question:\n\n ")
        search_results = qdrant_client.search(collection_name="logs_index", query_text=user_input)
        # TODO: get item and 'chunk' from db
        print(search_results)

        if user_input.lower() == "exit":
            break


if __name__ == "__main__":
    cli()
