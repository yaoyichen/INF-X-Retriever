"""CPU-only, testable helpers for document-level chunk-max retrieval."""
import hashlib
import json

import numpy as np

LONG_TASKS = (
    "biology", "earth_science", "economics", "pony", "psychology",
    "robotics", "stackoverflow", "sustainable_living",
)


def chunk_documents(documents, chunk_chars):
    if chunk_chars <= 0:
        raise ValueError("chunk_chars must be positive")
    texts, owners = [], []
    for i, text in enumerate(documents):
        for start in range(0, max(1, len(text)), chunk_chars):
            texts.append(text[start:start + chunk_chars])
            owners.append(i)
    return texts, np.asarray(owners, dtype=np.int64)


def pool_to_documents(scores, owners, n_docs):
    scores = np.asarray(scores)
    owners = np.asarray(owners)
    if scores.ndim != 2 or scores.shape[1] != len(owners):
        raise ValueError("Chunk scores and document mapping must align")
    if set(owners.tolist()) != set(range(n_docs)):
        raise ValueError("Each document must have at least one chunk")
    pooled = np.full((len(scores), n_docs), -np.inf, dtype=scores.dtype)
    for i, row in enumerate(scores):
        np.maximum.at(pooled[i], owners, row)
    return pooled


def corpus_cache_key(doc_ids, documents, **config):
    """Do not reuse truncated/chunked or different-corpus embeddings."""
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode())
    for did, text in zip(doc_ids, documents, strict=True):
        for value in (did, text):
            encoded = value.encode()
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
    return digest.hexdigest()[:24]
