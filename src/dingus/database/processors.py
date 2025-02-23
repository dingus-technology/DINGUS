"""processor.py

Contains nlp functions to process data.
"""

import logging

import numpy as np
from sentence_transformers import SentenceTransformer

from dingus.settings import SENTENCE_TRANSFORMER_MODEL

logger = logging.getLogger(__name__)


def generate_embeddings(texts: list) -> list | None:
    """
    Generate embeddings for the given texts using SentenceTransformer model.

    Args:
        texts (list): List of texts to generate embeddings for.

    Returns:
        list | None: List of embeddings for the given texts.
    """
    try:
        logger.info("Generating embeddings for the given texts.")

        model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        return [np.array(vec) for vec in model.encode(texts, convert_to_numpy=True)]

    except Exception as e:
        logger.error(f"Failed to generate embeddings. Error: {e}")
        return None
