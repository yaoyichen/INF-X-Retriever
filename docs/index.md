<h1 align="center">⚡ INF-X-Retriever</h1>

<p align="center">
  <strong>A Pragmatic & General Solution for Reasoning-Intensive Retrieval</strong>
</p>

<p align="center">
  <a href="https://brightbenchmark.github.io/"><img src="https://img.shields.io/badge/BRIGHT_Benchmark-Rank_1st-8A2BE2" alt="Rank"></a>
  <a href="https://huggingface.co/infly/inf-query-aligner"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Query--Aligner-blue" alt="Hugging Face"></a>
  <a href="https://huggingface.co/infly/inf-retriever-v1-pro"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Retriever-yellow" alt="Hugging Face"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
</p>

<p align="center">
  <strong>INF-X-Retriever</strong> is a production-grade dense reasoning retrieval framework developed by <strong>Infinite Light Years (INF)</strong>.<br>
  It delivers robust retrieval performance across arbitrary task databases (<mathcal>X</mathcal>) with minimal supervision, emphasizing industrial deployability and reasoning depth over architectural complexity.
</p>

<p align="center">
  <a href="#-introduction">Introduction</a> •
  <a href="#-philosophy--methodology">Philosophy</a> •
  <a href="#-performance">Performance</a> •
  <a href="#-models">Models</a> •
  <a href="#-citation">Citation</a>
</p>

---

## 📖 Introduction

The advent of Large Language Models (LLMs) has fundamentally transformed information retrieval paradigms.

* **Pre-LLM Era:** Users issued concise, keyword-driven queries optimized for lexical matching.
* **LLM Era:** Users engage with retrieval systems as reasoning agents. Queries now encompass contextual narratives, explicit constraints, and structured formatting requirements—elements that constitute semantic noise for conventional retrieval architectures.

Addressing this evolution demands retrieval systems capable of sophisticated intent distillation from verbally complex inputs. **INF-X-Retriever** is purpose-built for this challenge. We validate our methodology on the **BRIGHT Benchmark**, a curated dataset reflecting real-world query complexity that necessitates reasoning-intensive document matching.

---

## 💡 Design Philosophy

Our methodology is rooted in **Engineering Pragmatism** and **First Principles Reasoning**. While competitive solutions on the BRIGHT leaderboard gravitate toward elaborate multi-stage architectures, we pursue a fundamentally different trajectory—one that prioritizes **production readiness**, **architectural coherence**, and **computational parsimony**. 

> 🎯 **Core Principle:** *"Less is More"* — Maximal efficacy through deliberate minimalism.

### 🚫 No Rerankers

**Rationale:** *Architectural redundancy in RAG workflows*

Reranking stages introduce non-trivial latency and computational overhead while yielding diminishing returns. Given that downstream RAG systems invariably employ an LLM for answer synthesis, this component inherently performs context discrimination—rendering explicit reranking architecturally superfluous.

**Trade-off:** We sacrifice marginal ranking precision for substantial improvements in inference throughput and operational efficiency.

### 🚫 No HyDE

**Rationale:** *Epistemological inconsistency with RAG objectives*

Hypothetical Document Embeddings (HyDE) leverage LLMs to synthesize idealized answers, subsequently retrieving semantically proximate documents. This methodology embodies a fundamental logical contradiction:
- **If the LLM possesses domain knowledge** → Retrieval augmentation becomes obsolete
- **If the LLM lacks domain knowledge** → Synthesized hypotheses constitute hallucinated artifacts

While HyDE demonstrates benchmark efficacy (leveraging training data overlap), it **fundamentally fails in out-of-distribution domains**—precisely the scenarios for which RAG architectures are engineered.

### ⚡ Radical Simplicity

**Rationale:** *Architectural complexity constitutes operational debt*

We systematically eschew conventional techniques that introduce deployment fragility:

- **No sparse retrieval** (e.g., BM25) — Eliminates hybrid fusion complexity and hyperparameter sensitivity
- **No multi-query expansion** — Single-pass alignment minimizes inference latency
- **No ensemble methods** — Monolithic robustness supersedes fragile model combinations

**Result:** A system that is **operationally streamlined**, **latency-optimized**, and **diagnostically transparent** in production deployments.

---

## 🛠️ Architecture

Our system comprises two tightly integrated components:

### 🔍 Query Aligner
* **Model:** [🤗 infly/inf-query-aligner](https://huggingface.co/infly/inf-query-aligner)
* **Method:** Reinforcement Learning fine-tuning on [**Qwen2.5-7B-instruct**](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) foundation.
* **Function:** Performs semantic intent distillation from verbally complex queries. Executes pure **Query Alignment**—eliminating extraneous formatting directives and contextual noise to extract core retrieval intent—explicitly avoiding hypothetical document generation.

### 🚀 Retriever
* **Model:** [🤗 infly/inf-retriever-v1-pro](https://huggingface.co/infly/inf-retriever-v1-pro)
* **Method:** Continual training on the general-purpose [**inf-retriever-v1**](https://huggingface.co/infly/inf-retriever-v1) backbone with targeted long-query adaptation.
* **Function:** A generalized dense retrieval architecture resistant to depth-specific overfitting, ensuring robust cross-task transferability.

---

## 🏆 Performance

As of **November 20, 2025**, INF-X-Retriever holds the **No. 1 position** on the [BRIGHT Benchmark](https://brightbenchmark.github.io/).

### Overall & Category Performance

| Model | **Avg ALL** | **StackExchange** | **Code** | **Theorems** |
|:---|:---:|:---:|:---:|:---:|
| **INF-X-Retriever** | **55.04** | **55.03** | **65.98** | **47.77** |
| BGE-Reasoner-0928 | 46.40 | 52.00 | 35.30 | 40.70 |
| DIVER (v2) | 45.80 | 52.20 | 35.30 | 38.70 |

### Detailed Results Across 12 Datasets

| Model | Biology | Earth Sci | Economics | Psychology | Robotics | StackOverflow | Sustainable Living | LeetCode | Pony | AOPS | TheoremQA (Q) | TheoremQA (T) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **INF-X-Retriever** | **66.1** | **62.8** | **51.8** | **61.1** | 40.6 | **51.2** | **51.8** | **45.4** | **86.5** | **34.6** | **49.4** | **59.3** |
| BGE-Reasoner-0928 | 68.5 | 66.4 | 40.6 | 53.1 | **43.2** | 44.1 | 47.8 | 29.0 | 41.6 | 17.2 | 46.5 | 58.3 |
| DIVER (v2) | 68.0 | 62.5 | 42.0 | 58.2 | 41.5 | 44.3 | 49.2 | 34.8 | 32.9 | 19.1 | 44.3 | 52.6 |

---

## 📥 Models

We have released both components as open-source artifacts to facilitate community research and development.

* **Aligner:** [🤗 infly/inf-query-aligner](https://huggingface.co/infly/inf-query-aligner)
* **Retriever:** [🤗 infly/inf-retriever-v1-pro](https://huggingface.co/infly/inf-retriever-v1-pro)

---

## 🖊️ Citation

If INF-X-Retriever contributes to your research or production systems, please cite our work:

```bibtex
@misc{yao2025infx,
    title        = {INF-X-Retriever},
    author       = {Yichen Yao and Jiahe Wan and Yuxin Hong and Mengna Zhang and Junhan Yang and Yinhui Xu and Wei Chu and Yuan Qi},
    year         = {2025},
    url          = {https://yaoyichen.github.io/INF-X-Retriever/},
    note         = {GitHub repository}
}
```
