<div align="center">

# ⚡ INF-X-Retriever
### A Pragmatic & General Solution for Reasoning-Intensive Retrieval

[![Rank](https://img.shields.io/badge/BRIGHT_Benchmark-Rank_1st-8A2BE2)](https://brightbenchmark.github.io/)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Query--Aligner-blue)](https://huggingface.co/infly/inf-query-aligner)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Retriever-yellow)](https://huggingface.co/infly/inf-retriever-v1-pro)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**INF-X-Retriever** is a general-purpose dense reasoning retrieval solution developed by **Infinite Light Years (INF)**.  
It achieves high-quality retrieval given a task database ($X$) and few-shot examples, prioritizing industrial viability and reasoning capability over complexity.

[Introduction](#-introduction) • [Philosophy](#-philosophy--methodology) • [Performance](#-performance) • [Models](#-models) • [Citation](#-citation)

</div>

---

## 📖 Introduction

We are witnessing a paradigm shift in search behavior driven by the Large Language Model (LLM) era.

* **Pre-LLM Era:** Users provided short, keyword-centric queries.
* **LLM Era:** Users treat the engine as an intelligent processor. Queries are now complex, containing background descriptions, instruction constraints, and format requirements—elements that are "noise" to traditional retrievers.

To meet these new demands, a retrieval engine must possess deep reasoning capabilities to identify the core intent amidst complex instructions. **INF-X-Retriever** is designed to solve this challenge. We validate our approach on the **BRIGHT Benchmark**, a dataset derived from real-world human data that requires intensive reasoning to locate relevant documents.

---

## 💡 Philosophy & Methodology

Our solution is built on **Pragmatism** and **First Principles**. While observing many mature solutions on the BRIGHT leaderboard, we chose a different path focused on industrial application and logical consistency. We believe **"Less is More."**

### 1. Rejection of Rerankers (No Rerank)
> **Insight:** In industrial practice, the value added by a Rerank module is often marginal compared to its cost.

Many solutions rely on LLM-based Rerankers. However, downstream RAG tasks already involve an LLM for Quality Assurance (QA). We believe the QA LLM can inherently select relevant contexts from retrieved documents without an explicit, computationally expensive, and latency-inducing sorting module.

### 2. Rejection of HyDE (No Hypothetical Documents)
> **Insight:** HyDE contradicts the fundamental purpose of RAG.

Hypothetical Document Embeddings (HyDE) rely on an LLM to "hallucinate" a perfect answer to search against. We reject this based on first principles:
* If the LLM can generate a perfect hypothetical document, it already possesses the knowledge, rendering Retrieval-Augmented Generation (RAG) unnecessary.
* If the knowledge is outside the LLM's scope, the hypothetical document is likely a hallucination, leading to poor retrieval.
* While HyDE might boost scores on academic benchmarks (where data is often within the LLM's training set), it lacks robustness in real-world, unknown domains.

### 3. Radical Simplicity
* **No BM25:** We do not use sparse retrieval or complex fusion strategies.
* **Single-Pass Alignment:** We use a single query alignment step rather than multiple variations.

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
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
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
    title = {INF-X-Retriever},
    author = {Yichen Yao, Jiahe Wan, Yuxin Hong, Mengna Zhang, Junhan Yang, Yinhui Xu, Wei Chu, Yuan Qi},
    howpublished = {\url{[https://yaoyichen.github.io/INF-X-Retriever/](https://yaoyichen.github.io/INF-X-Retriever/)}},
    year = {2025},
    note = {GitHub repository}
}
