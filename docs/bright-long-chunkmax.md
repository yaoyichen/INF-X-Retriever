# BRIGHT long-document update: Chunk-Max

Validated: **2026-10-09**. Status: **self-reported, pending submission**.
This page does not claim official acceptance or a new leaderboard rank.

## Primary result

**60.9635 average Recall@1 × 100**, displayed as **60.96** (or **61.0** at
one decimal). All eight tasks and 861 official queries are included.
The previously published truncation result is 54.6. That comparison also
changes the inference backend/context policy; it is not a controlled
chunking-only ablation.

The [validation report](../results/bright-long-chunkmax/validation.json)
records per-task metrics, coverage, dataset fingerprints, and score-file SHA-256
checksums. It was recomputed from the existing September 2026 score files,
not from a new October model run.

## Frozen method

- Queries: the existing `rewrite_data/*_queries.json` from the released
  `inf-query-aligner`; no new rewriting or training.
- Retriever: `inf-retriever-v1-pro`, 3,584-dimensional last-token embeddings,
  normalized cosine similarity; no reranker.
- Corpus: `xlangai/bright`, `long_documents`; qrels: `examples.gold_ids_long`.
  Dataset revision: `3066d29c9651a576c8aba4832d249807b181ecae`.
- Documents: contiguous, non-overlapping **20,000-character** chunks. Each chunk
  receives its own embedding, subject to an **8,192-token** maximum.
  This character-based policy does not guarantee that every token is retained.
- Document score: `max(cosine(query, chunk))` across that document's chunks.
  Export score × 100, filter `excluded_ids`, return at most 1,000 original
  document IDs. No chunk IDs or generated pages are returned.
- Metric: official `pytrec_eval` Recall@1, rounded to five decimals per task,
  then macro-averaged across eight tasks and multiplied by 100.
  Recall@1 is **not hit rate**: 236 queries have multiple gold documents.

The internal serving configuration fingerprint was
`ddc36b5c898f9fa2bbad73051b624c52fd1d77855f71e05cf96bb2e5f8328d01`;
the query-prefix hash was
`df4b2898bf22e00bacddddd489243a3f8793730e38b842ec10161cebd94d36d6`.
These identify the measured service configuration, not a public checkpoint
revision. Its encoding used length buckets (512–8192 tokens, chosen by a
character-based estimate), so a local fixed-cap HF run is **not guaranteed
metric-identical**. Full local-model parity remains unverified.

## Validate the frozen scores (no GPU or inference API)

Download the [complete score archive (ZIP, approximately 8.3 MiB)](../results/bright-long-chunkmax/bright-long-chunkmax-20261009.zip).
It includes all eight score files, the validation report, method metadata, and
the standalone validator. [Archive SHA-256](../results/bright-long-chunkmax/SHA256SUMS)
and [artifact index](../results/bright-long-chunkmax/README.md) are also provided.
These are self-reported artifacts, not an official leaderboard acceptance.

```bash
pip install datasets pytrec_eval
python validate_long_submission.py \
  --scores /path/to/extracted/scores \
  --expected results/bright-long-chunkmax/validation.json \
  --report /tmp/bright-long-validation.json
```

The validator rejects missing/extra queries, duplicate JSON keys, nonfinite
scores, unknown/chunk-level IDs, exclusions, incomplete task sets, and a
different dataset-cache revision. `--expected` additionally checks the frozen
score hashes and metrics. It deliberately uses official examples rather than
trusting labels copied into rewritten query files.

## Rerun the public local-model implementation (GPU required)

```bash
pip install -r requirements.txt
LONG_CONTEXT=true CHUNK_CHARS=20000 \
DOC_MAX_LENGTH=8192 QUERY_MAX_LENGTH=8192 ENCODE_BATCH_SIZE=1 \
OUTPUT_DIR=./output/INF-X-Retriever-chunkmax ./run.sh
```

Long mode runs **only the eight supported tasks**. `CHUNK_CHARS=0` retains
truncation mode (40,960 document tokens by default). Chunked output directories
are separate from historical runs. Document embedding caches are keyed by
corpus content/IDs, model identity and revision, chunking, and context length.
Use a new output directory for a new experiment; completed directories are not
silently overwritten. Do not mix local rerun files with the frozen submission.

To validate a rerun, copy each task's `score.json` into a separate directory
named `<task>.json`, then run the validator **without** `--expected`; that is a
new experiment, not a claim of reproducing the frozen score hashes.

## Why submit without Wiki first?

A separate experimental corpus-Wiki configuration scores **61.0730**, only
**+0.1095 percentage points** over Chunk-Max. It uses candidate-restricted
fusion with weight 0.05 except **Pony, which uses 0.1**. Those exploratory
choices were examined on public benchmark results; they are not a held-out
development-set claim. Wiki compilation and fusion are not included in this
public runner.

The simpler 60.96 configuration requires no Wiki-building API, keeps the
single-stage retrieval design, and avoids making the initial submission
depend on Wiki preprocessing/exclusion-policy approval. The organizers still
decide whether to accept document-level chunk-max scoring. Short-document
results are unchanged.
