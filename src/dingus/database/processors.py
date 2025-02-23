"""processor.py

Contains nlp functions to process data.
"""

import hashlib
import json
import logging

import numpy as np
from sentence_transformers import SentenceTransformer

from dingus.settings import SENTENCE_TRANSFORMER_MODEL

logger = logging.getLogger(__name__)


def generate_embeddings(texts: list) -> list:
    """
    Generate embeddings for the given texts using SentenceTransformer model.

    Args:
        texts (list): List of texts to generate embeddings for.

    Returns:
        list: List of embeddings for the given texts.
    """
    try:
        logger.info("Generating embeddings for the given texts.")

        model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        return [np.array(vec) for vec in model.encode(texts, convert_to_numpy=True)]

    except Exception as e:
        logger.error(f"Failed to generate embeddings. Error: {e}")
        raise Exception("Failed embedding text to vectors") from e


def generate_id(payload):
    payload_json = json.dumps(payload, sort_keys=True)
    hash_bytes = hashlib.sha256(payload_json.encode("utf-8")).digest()
    return int.from_bytes(hash_bytes[:8], byteorder="big")
