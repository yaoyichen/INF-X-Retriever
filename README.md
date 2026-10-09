<h1 align="center">⚡ INF-X-Retriever</h1>

<p align="center">
  <strong>A Pragmatic & General Solution for Reasoning-Intensive Retrieval</strong>
</p>

<p align="center">
  <a href="https://brightbenchmark.github.io/"><img src="https://img.shields.io/badge/BRIGHT-Long_60.96_self--reported-8A2BE2" alt="BRIGHT long-document: 60.96, self-reported"></a>
  <a href="https://huggingface.co/infly/inf-query-aligner"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Query--Aligner-blue" alt="Hugging Face"></a>
  <a href="https://huggingface.co/infly/inf-retriever-v1-pro"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Retriever-yellow" alt="Hugging Face"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache--2.0-green.svg" alt="License"></a>
</p>

## 📖 Overview

**INF-X-Retriever** is a production-grade dense retrieval framework designed to handle the complex, reasoning-intensive queries of the LLM era. Rooted in **engineering pragmatism**, it eschews complex multi-stage pipelines (like Rerankers or HyDE) in favor of a streamlined **Query Aligner + Dense Retriever** architecture. This "less is more" approach prioritizes low latency and robust cross-task transferability, with a **self-reported long-document Recall@1 of 60.96** (validated October 9, 2026; pending submission). Historical leaderboard results are listed separately below.

For a deep dive into our design philosophy and methodology, please refer to our [Documentation](docs/index.md).

---

## 🛠️ Architecture

Our system comprises two tightly integrated components:

1.  **🚀 Query Aligner** ([inf-query-aligner](https://huggingface.co/infly/inf-query-aligner)): Distills core retrieval intent from verbally complex queries using a Qwen2.5-7B-instruct foundation tuned via Reinforcement Learning.
2.  **🔍 Retriever** ([inf-retriever-v1-pro](https://huggingface.co/infly/inf-retriever-v1-pro)): A generalized dense retrieval model optimized for long-query adaptation and resistant to domain overfitting.

<p align="center">
  <img src="docs/assets/architecture.svg" alt="INF-X-Retriever Architecture" width="100%"/>
</p>

---

## 🚀 Quick Start

Requirements: Python 3.10, Linux/macOS recommended.

### Installation

```bash
pip install -r requirements.txt
```

### 1. Query Rewriting (Optional)

To process raw parquet files and rewrite queries using the `inf-query-aligner`:

```bash
python rewrite_queries.py \
    --data_folder_path xlangai/bright \
    --model_name_or_path infly/inf-query-aligner \
    --output_path ./rewrite_data
```

### 2. Short-document evaluation

To evaluate the model on supported tasks, run:

```bash
./run.sh
```

**Configuration:**  
The evaluation pipeline can be customized via environment variables:

```bash
# Use the supported retriever backend name ("inf"), not a checkpoint path.
MODEL_NAME=inf \
ENCODE_BATCH_SIZE=32 \
REWRITE_EVAL=false \
./run.sh
```

### 3. Long-document evaluation (Chunk-Max)

To run the **Chunk-Max configuration** described in the new long-document
result, reuse the released query rewrites and explicitly enable chunking:

```bash
MODEL_NAME=inf REWRITE_EVAL=true \
LONG_CONTEXT=true CHUNK_CHARS=20000 \
DOC_MAX_LENGTH=8192 QUERY_MAX_LENGTH=8192 ENCODE_BATCH_SIZE=1 \
OUTPUT_DIR=./output/INF-X-Retriever-chunkmax ./run.sh
```

This runs only the **eight long-document tasks**, without Wiki or reranking,
and writes to a separate output directory. Use a fresh output directory for
each new experiment. `LONG_CONTEXT=true` alone retains the legacy truncation
configuration (`CHUNK_CHARS=0`); it does **not** enable Chunk-Max.

The published **60.96** score was measured with the internal serving
configuration; this public local-model command has not been verified to
produce identical scores. See [the method and reproduction notes](docs/bright-long-chunkmax.md)
or [download and validate the frozen scores without a GPU](results/bright-long-chunkmax/README.md).

---

## 🏆 Performance

The short-document tables below are a **historical December 20, 2025 snapshot**, not a current ranking. The long-document section adds the **October 9, 2026 locally validated Chunk-Max result**, pending official submission and acceptance.

**BRIGHT** is a rigorous text retrieval benchmark designed to evaluate the capability of retrieval models in handling questions that require intensive reasoning and cross-document synthesis. Collected from real-world sources such as StackExchange, competitive programming platforms, and mathematical competitions, it comprises complex queries spanning diverse domains like mathematics, coding, biology, economics, and robotics.

**Why BRIGHT Matters:**
- **High Reasoning Complexity:** Unlike traditional keyword-centric benchmarks, BRIGHT queries often demand multi-step reasoning, evidence aggregation across documents, and theoretical mapping. This effectively exposes the limitations of standard models in complex "understanding + retrieval" tasks.
- **Authentic & Interdisciplinary:** By leveraging real-world data from varied professional fields, BRIGHT provides a faithful assessment of a model's generalization capabilities in specialized, high-stakes environments.
- **Critical for RAG:** As a stress test for modern Retrieval-Augmented Generation (RAG) systems, it serves as a key indicator for performance in demanding industrial applications such as scientific research, legal analysis, and medical Q&A.

### Short document

#### Overall & Category Performance

| Model | **Avg ALL** | **StackExchange** | **Coding** | **Theorem-based** |
|:---|:---:|:---:|:---:|:---:|
| **INF-X-Retriever** | **63.4** | **68.3** | **55.3** | **57.7** |
| DIVER (v3) | 46.8 | 51.8 | 39.9 | 39.7 |
| BGE-Reasoner-0928 | 46.4 | 52.0 | 35.3 | 40.7 |
| LATTICE | 42.1 | 51.6 | 26.9 | 30.0 |
| ReasonRank | 40.8 | 46.9 | 27.6 | 35.5 |
| XDR2 | 40.3 | 47.1 | 28.5 | 32.1 |

#### Detailed Results Across 12 Datasets

| Model | Avg | Bio. | Earth. | Econ. | Psy. | Rob. | Stack. | Sus. | Leet. | Pony | AoPS | TheoQ. | TheoT. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **INF-X-Retriever** | **63.4** | **79.8** | **70.9** | **69.9** | **73.3** | **57.7** | **64.3** | **61.9** | **56.1** | **54.5** | **51.9** | **53.1** | **67.9** |
| DIVER (v3) | 46.8 | 66.0 | 63.7 | 42.4 | 55.0 | 40.6 | 44.7 | 50.4 | 32.5 | 47.3 | 17.2 | 46.4 | 55.6 |
| BGE-Reasoner-0928 | 46.4 | 68.5 | 66.4 | 40.6 | 53.1 | 43.2 | 44.1 | 47.8 | 29.0 | 41.6 | 17.2 | 46.5 | 58.4 |
| LATTICE | 42.1 | 64.4 | 62.4 | 45.4 | 57.4 | 47.6 | 37.6 | 46.4 | 19.9 | 34.0 | 12.0 | 30.1 | 47.8 |
| ReasonRank | 40.8 | 62.7 | 55.5 | 36.7 | 54.6 | 35.7 | 38.0 | 44.8 | 29.5 | 25.6 | 14.4 | 42.0 | 50.1 |
| XDR2 | 40.3 | 63.1 | 55.4 | 38.5 | 52.9 | 37.1 | 38.2 | 44.6 | 21.9 | 35.0 | 15.7 | 34.4 | 46.2 |

### Long document

**Metric:** macro-average document-level Recall@1 × 100 across all eight tasks.
**Update (October 9, 2026):** the frozen Chunk-Max score files were independently
re-evaluated against the official `gold_ids_long`: **60.9635 → 60.96**.
All **861 queries** are covered; document IDs and per-query exclusions pass validation.
This is a **self-reported result, not yet submitted or accepted by the leaderboard**.
The previously published 54.6 result is retained for comparison.

**Reproducibility:** [Method](https://github.com/yaoyichen/INF-X-Retriever/blob/5575f6c376bb0aa0bb304578ae11c8e8b6f7529f/docs/bright-long-chunkmax.md) · [Download all eight score files (ZIP)](https://raw.githubusercontent.com/yaoyichen/INF-X-Retriever/54af35d78d244bbd05863349c65e9ac102557cc9/results/bright-long-chunkmax/bright-long-chunkmax-20261009.zip) · [Validation report](https://github.com/yaoyichen/INF-X-Retriever/blob/54af35d78d244bbd05863349c65e9ac102557cc9/results/bright-long-chunkmax/validation.json) · [SHA-256](https://github.com/yaoyichen/INF-X-Retriever/blob/54af35d78d244bbd05863349c65e9ac102557cc9/results/bright-long-chunkmax/SHA256SUMS)


#### Detailed Results Across 8 Datasets

| Model | Avg | Bio. | Earth. | Econ. | Pony | Psy. | Rob. | Stack. | Sus. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **INF-X-Retriever + Chunk-Max (self-reported; pending submission)** | **60.96** | **76.13** | **60.99** | **73.14** | **11.78** | **81.22** | **57.92** | **53.42** | **73.10** |
| INF-X-Retriever (previously published, truncation) | **54.6** | **73.2** | **59.6** | **69.3** | **12.1** | **74.3** | **55.9** | **27.8** | **64.8** |
| inf-retriever-v1-pro | 30.5 | 44.1 | 42.2 | 31.4 | 0.4 | 43.1 | 20.8 | 21.4 | 41.0 |

#### Long-document method: Chunk-Max (no reranker, no Wiki)

Reuse the released query-aligner rewrites, split each document into contiguous
**20,000-character chunks**, embed each chunk with an **8,192-token cap**, and use
its maximum query–chunk cosine similarity as the original document's score.
Return only original document IDs after applying `excluded_ids`.
Character chunks are not guaranteed to fit the token cap; tokenization can still
truncate individual chunks. No new training or query expansion is introduced.

The validated result was produced by the internal `inf-retriever-v1-pro` serving
configuration; the public local-model runner now supports the same chunk-max
algorithm, but has **not** been rerun end to end to establish score parity.
The separate experimental Wiki variant scored 61.07 (+0.11 points), but is not
part of this primary submission or the public runner.

See [method, validation, and reproduction](https://github.com/yaoyichen/INF-X-Retriever/blob/5575f6c376bb0aa0bb304578ae11c8e8b6f7529f/docs/bright-long-chunkmax.md) for the frozen dataset
revision, score checksums, inference differences, and commands.



---
 
## 📥 Models

* **Aligner:** [🤗 inf-query-aligner](https://huggingface.co/infly/inf-query-aligner)
* **Retriever:** [🤗 inf-retriever-v1-pro](https://huggingface.co/infly/inf-retriever-v1-pro)

---

## 🖊️ Citation

```text
@misc{inf-x-retriever-2025,
    title        = {INF-X-Retriever},
    author       = {Yichen Yao, Jiahe Wan, Yuxin Hong, Mengna Zhang, Junhan Yang, Zhouyu Jiang, Qing Xu, Kuan Lu, Yinghui Xu, Wei Chu, Emma Wang, Yuan Qi},
    year         = {2025},
    url          = {https://yaoyichen.github.io/INF-X-Retriever},
    publisher    = {GitHub repository}
}
```

---

## 📬 Contact

Email: [eason.yyc@inftech.ai](mailto:eason.yyc@inftech.ai)
