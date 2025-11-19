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
  <strong>INF-X-Retriever</strong> is a general-purpose dense reasoning retrieval solution developed by <strong>Infinite Light Years (INF)</strong>.<br>
  It achieves high-quality retrieval given a task database (<mathcal>X</mathcal>) and few-shot examples, prioritizing industrial viability and reasoning capability over complexity.
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

We are witnessing a paradigm shift in search behavior driven by the Large Language Model (LLM) era.

* **Pre-LLM Era:** Users provided short, keyword-centric queries.
* **LLM Era:** Users treat the engine as an intelligent processor. Queries are now complex, containing background descriptions, instruction constraints, and format requirements—elements that are "noise" to traditional retrievers.

To meet these new demands, a retrieval engine must possess deep reasoning capabilities to identify the core intent amidst complex instructions. **INF-X-Retriever** is designed to solve this challenge. We validate our approach on the **BRIGHT Benchmark**, a dataset derived from real-world human data that requires intensive reasoning to locate relevant documents.

---

## 💡 Design Philosophy

Our approach is grounded in **Pragmatism** and **First Principles Thinking**. While many solutions on the BRIGHT leaderboard employ complex multi-stage pipelines, we deliberately chose a different path—one optimized for **industrial deployability**, **logical consistency**, and **computational efficiency**. 

> 🎯 **Core Principle:** *"Less is More"* — Maximum effectiveness through minimal complexity.

### 🚫 No Rerankers

**Rationale:** *Redundant computation in RAG pipelines*

Reranking modules add latency and cost, yet provide marginal value. Since downstream RAG systems already employ an LLM for answer generation (QA), this LLM can inherently discriminate among retrieved contexts—making explicit reranking redundant.

**Trade-off:** We exchange slight ranking precision for substantial gains in inference speed and resource efficiency.

### 🚫 No HyDE

**Rationale:** *Contradicts RAG's fundamental purpose*

Hypothetical Document Embeddings (HyDE) prompt an LLM to generate ideal answers, then retrieve similar documents. This approach suffers from a logical paradox:
- **If the LLM knows the answer** → RAG is unnecessary
- **If the LLM doesn't know** → Generated hypothesis is likely hallucinated

While HyDE may boost benchmarks (where answers lie within training data), it **fails in truly novel domains**—the exact scenario RAG is designed for.

### ⚡ Radical Simplicity

**Rationale:** *Complexity is a liability in production*

We deliberately avoid common techniques that complicate deployment:

- **No sparse retrieval** (e.g., BM25) — No hybrid fusion pipelines to tune and maintain
- **No multi-query expansion** — Single-pass query alignment reduces latency
- **No ensemble methods** — One robust model beats brittle combinations

**Result:** A solution that is **easier to deploy**, **faster to run**, and **simpler to debug** in production environments.

---

## 🛠️ Architecture

Our pipeline consists of two streamlined components:

### 🔍 Query Aligner
* **Model:** `inf-query-aligner`
* **Method:** Fine-tuned on **Qwen2.5-7B-instruct** using **Reinforcement Learning**.
* **Function:** Bridges the gap between the user's raw input and the retriever. It performs pure **Query Alignment**—stripping away noise and formatting instructions to isolate the search intent—without generating hypothetical documents.

### 🚀 Retriever
* **Model:** `inf-retriever-v1-pro`
* **Method:** Post-trained on the generic `inf-retriever-v1` with a small amount of long-query data.
* **Function:** A robust dense retrieval model that is not overfitted to specific search depths, ensuring generalization across tasks.

---

## 🏆 Performance

As of **November 20, 2025**, INF-X-Retriever holds the **No. 1 position** on the [BRIGHT Benchmark](https://brightbenchmark.github.io/).

| Model | **Avg** | Biology | Earth Sci | Economics | Psychology | Robotics | StackOverflow | LeetCode | TheoremQA (T) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **INF-X-Retriever** | **55.04** | **0.661** | **0.628** | **0.518** | **0.611** | 0.406 | **0.512** | **0.454** | **0.593** |
| BGE-Reasoner-0928 | 46.40 | 0.685 | 0.664 | 0.406 | 0.531 | **0.432** | 0.441 | 0.290 | 0.583 |
| DIVER (v2) | 45.80 | 0.680 | 0.625 | 0.420 | 0.582 | 0.415 | 0.443 | 0.348 | 0.526 |

*(Note: Selected columns shown for brevity. See the official leaderboard for full metrics.)*

---

## 📥 Models

We have open-sourced our models to contribute to the community.

* **Aligner:** [🤗 infly/inf-query-aligner](https://huggingface.co/infly/inf-query-aligner)
* **Retriever:** [🤗 infly/inf-retriever-v1-pro](https://huggingface.co/infly/inf-retriever-v1-pro)

---

## 🖊️ Citation

If you find INF-X-Retriever helpful for your research or business, please cite our work:

```bibtex
@misc{yao2025infx,
    title        = {INF-X-Retriever},
    author       = {Yichen Yao and Jiahe Wan and Yuxin Hong and Mengna Zhang and Junhan Yang and Yinhui Xu and Wei Chu and Yuan Qi},
    year         = {2025},
    url          = {https://yaoyichen.github.io/INF-X-Retriever/},
    note         = {GitHub repository}
}
```
