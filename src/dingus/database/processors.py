"""processor.py

Contains nlp functions to process data.
"""

import hashlib
import json
import logging
import numpy as np
import spacy


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

        nlp = spacy.load('en_core_web_sm')
        return [doc.vector for doc in nlp.pipe(texts)]

    except Exception as e:
        logger.error(f"Failed to generate embeddings. Error: {e}")
        raise Exception("Failed embedding text to vectors") from e


def generate_id(payload):
    payload_json = json.dumps(payload, sort_keys=True)
    hash_bytes = hashlib.sha256(payload_json.encode("utf-8")).digest()
    return int.from_bytes(hash_bytes[:8], byteorder="big")
