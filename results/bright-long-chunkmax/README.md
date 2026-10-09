# BRIGHT long-document result artifacts

**INF-X-Retriever + Chunk-Max · Recall@1 × 100: 60.9635**

Validated October 9, 2026. **Self-reported; pending submission and acceptance.**
This updates the long-document configuration only, not the short-document result.

## Downloads

| Artifact | Contents |
| --- | --- |
| [Complete scores (ZIP, approximately 8.3 MiB)](bright-long-chunkmax-20261009.zip) | Eight score JSON files, validator, validation report, method metadata, and instructions |
| [Validation report](validation.json) | Per-task metrics, query counts, corpus fingerprints, and score-file SHA-256 hashes |
| [Method metadata](method.json) | Dataset revision, chunking and inference configuration, query-rewrite hashes |
| [Archive checksum](SHA256SUMS) | SHA-256 of the downloadable ZIP |
| [Method and reproduction](../../docs/bright-long-chunkmax.md) | Algorithm, reproduction commands, and limitations |

## Results

| Dataset | Queries | Recall@1 × 100 |
| --- | ---: | ---: |
| biology | 103 | 76.133 |
| earth_science | 116 | 60.991 |
| economics | 103 | 73.139 |
| pony | 112 | 11.782 |
| psychology | 101 | 81.221 |
| robotics | 101 | 57.921 |
| stackoverflow | 117 | 53.419 |
| sustainable_living | 108 | 73.102 |
| **Macro average / total queries** | **861** | **60.9635** |

Scores use `{query_id: {original_document_id: score}}`, with at most 1,000
documents per query after exclusions. The metric is document-level Recall@1,
not hit rate or short-document nDCG@10.

## Verify

```bash
sha256sum -c SHA256SUMS
unzip bright-long-chunkmax-20261009.zip -d extracted
cd extracted
pip install datasets pytrec_eval
python validate_long_submission.py \
  --scores scores --expected validation.json \
  --report /tmp/bright-long-validation.json
```

The existing September score files were revalidated in October; this is not
a new October inference run. They were generated with the internal serving
configuration documented in `method.json`. Full score parity with the public
local-model runner remains unverified. No Wiki or reranker is used in this
submission candidate.
