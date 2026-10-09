import unittest

import numpy as np

from long_document import chunk_documents, corpus_cache_key, pool_to_documents


class ChunkMaxTest(unittest.TestCase):
    def test_chunk_boundaries_and_empty_document(self):
        texts, owners = chunk_documents(["abcdef", "", "123"], 3)
        self.assertEqual(texts, ["abc", "def", "", "123"])
        self.assertEqual(owners.tolist(), [0, 0, 1, 2])
        with self.assertRaises(ValueError):
            chunk_documents(["abc"], 0)

    def test_pooling_preserves_negative_scores(self):
        result = pool_to_documents(np.array([[-0.9, -0.2, -0.5]]), [0, 0, 1], 2)
        np.testing.assert_allclose(result, [[-0.2, -0.5]])

    def test_pooling_rejects_missing_documents(self):
        with self.assertRaises(ValueError):
            pool_to_documents(np.array([[0.5]]), [0], 2)

    def test_cache_identity_changes(self):
        key = corpus_cache_key(["a"], ["abc"], chunk_chars=3, max_length=8192)
        for ids, texts, config in [
            (["b"], ["abc"], dict(chunk_chars=3, max_length=8192)),
            (["a"], ["xyz"], dict(chunk_chars=3, max_length=8192)),
            (["a"], ["abc"], dict(chunk_chars=0, max_length=8192)),
            (["a"], ["abc"], dict(chunk_chars=3, max_length=40960)),
        ]:
            self.assertNotEqual(key, corpus_cache_key(ids, texts, **config))


if __name__ == "__main__":
    unittest.main()
