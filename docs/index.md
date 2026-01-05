<h1 align="center">INF-X-Retriever</h1>

<p align="center">
  <strong>A pragmatic, general solution for reasoning-intensive retrieval</strong>
</p>

<p align="center">
  <a href="https://brightbenchmark.github.io/"><img src="https://img.shields.io/badge/BRIGHT_Benchmark-Rank_1st-8A2BE2" alt="Rank"></a>
  <a href="https://huggingface.co/infly/inf-query-aligner"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Query--Aligner-blue" alt="Hugging Face"></a>
  <a href="https://huggingface.co/infly/inf-retriever-v1-pro"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-INF--Retriever-yellow" alt="Hugging Face"></a>
  <a href="https://github.com/yaoyichen/INF-X-Retriever"><img src="https://img.shields.io/badge/GitHub-Repo-black?logo=github" alt="GitHub Repo"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache--2.0-green.svg" alt="License"></a>
</p>

<p align="center">
  <strong>INF-X-Retriever</strong> is a production-grade dense reasoning retrieval framework developed by <strong><a href="https://inf.hk/">INF</a></strong>.<br>
  It delivers robust retrieval performance across arbitrary task collections (X) with minimal supervision, emphasizing deployability, reliability, and reasoning depth over architectural complexity.
</p>

<p align="center">
  <a href="#-introduction">Introduction</a> •
  <a href="#-design-principles">Design Principles</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-performance">Performance</a> •
  <a href="#-models">Models</a> •
  <a href="#-installation--quick-start">Installation & Quick Start</a> •
  <a href="#-evaluation--reproducibility">Evaluation & Reproducibility</a> •
  <a href="#-citation">Citation</a> •
  <a href="#-contact">Contact</a> •
  <a href="https://github.com/yaoyichen/INF-X-Retriever">GitHub</a>
</p>

---

## 📖 Introduction

Large Language Models (LLMs) have shifted information retrieval from keyword matching to intent-aware reasoning. Modern queries often include narrative context, constraints, and formatting directives—elements that are semantically noisy for conventional retrieval systems.

INF-X-Retriever addresses this shift by performing intent distillation on complex queries and executing single-stage dense retrieval. The approach is validated on the BRIGHT Benchmark, which reflects realistic, reasoning-heavy retrieval scenarios.

---

## 💡 Design Principles

Our design emphasizes engineering practicality and first-principles reasoning. We prioritize production readiness, architectural coherence, and computational efficiency.

<p align="center">
  <img src="assets/comparison.svg" alt="Pipeline Comparison" width="100%"/>
</p>

> 🎯 **Core Principle:** *"Less is More"* — Maximal efficacy through deliberate minimalism.

### ▫️ No Rerankers

Reranking stages add latency and operational overhead, while downstream LLMs in RAG pipelines already perform implicit context discrimination during answer synthesis. In production environments, the marginal gains from explicit reranking often do not justify the additional complexity in deployment, monitoring, and maintenance.

Our solution achieves robust performance via a single-stage dense retrieval pipeline, favoring operational simplicity and efficiency.

### ▫️ No HyDE

Hypothetical Document Embeddings (HyDE) first generate a hypothetical answer with an LLM and then retrieve documents similar to that answer. This introduces methodological risks:

- When the LLM already possesses the necessary knowledge, retrieval adds little value.
- When the LLM lacks the domain knowledge (the common case for RAG), the generated “hypothetical answer” may be unreliable, steering retrieval toward misleading content.

We therefore perform direct query alignment—extracting core retrieval intent without generating hypothetical content—so that retrieval remains grounded in user requirements and source documents.

### Operational Simplicity

We avoid techniques that introduce fragility or unnecessary complexity:

- No sparse retrieval (e.g., BM25) — eliminates hybrid fusion complexity and hyperparameter sensitivity
- No multi-query expansion — single-pass alignment minimizes latency
- No ensemble methods — favors robustness and maintainability

Result: a system that is streamlined, latency-conscious, and transparent for diagnostics in production.

---

## 🛠️ Architecture

Our system comprises two tightly integrated components:

### Query Aligner
* Model: <a href="https://huggingface.co/infly/inf-query-aligner"><strong>🤗 inf-query-aligner</strong></a>
* Method: Reinforcement Learning fine-tuning on <a href="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct">Qwen2.5-7B-Instruct</a>
* Function: Semantic intent distillation from verbally complex queries. Performs pure query alignment to extract core retrieval intent, avoiding hypothetical content generation.

### Retriever
* Model: <a href="https://huggingface.co/infly/inf-retriever-v1-pro"><strong>🤗 inf-retriever-v1-pro</strong></a>
* Method: Continual training on the general-purpose <a href="https://huggingface.co/infly/inf-retriever-v1">inf-retriever-v1</a> backbone with targeted long-query adaptation.
* Function: Generalized dense retrieval architecture built for cross-task transfer and stability.

<p align="center">
  <img src="assets/architecture.svg" alt="INF-X-Retriever Architecture" width="100%"/>
</p>

---

## 📊 Performance

**INF-X-Retriever** achieves state-of-the-art results on the [BRIGHT Benchmark](https://brightbenchmark.github.io/) (as of Dec 20, 2025).

The **BRIGHT** (Benchmark for Reasoning-Intensive Grounded HT) is a rigorous text retrieval benchmark designed to evaluate the capability of retrieval models in handling questions that require intensive reasoning and cross-document synthesis. Collected from real-world sources such as StackExchange, competitive programming platforms, and mathematical competitions, it comprises complex queries spanning diverse domains like mathematics, coding, biology, economics, and robotics.

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

#### Detailed Results Across 8 Datasets

| Model | Avg | Bio. | Earth. | Econ. | Pony | Psy. | Rob. | Stack. | Sus. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **INF-X-Retriever** | **54.6** | **73.2** | **59.6** | **69.3** | **12.1** | **74.3** | **55.9** | **27.8** | **64.8** |
| inf-retriever-v1-pro | 30.5 | 44.1 | 42.2 | 31.4 | 0.4 | 43.1 | 20.8 | 21.4 | 41.0 |

Notes:
- Results reflect end-to-end retrieval accuracy on BRIGHT under the official evaluation protocol.
- Performance may vary with hardware, index size, and dataset versions.

---

## 🧪 Models

- Query Aligner: <a href="https://huggingface.co/infly/inf-query-aligner"><strong>inf-query-aligner</strong></a>
- Retriever: <a href="https://huggingface.co/infly/inf-retriever-v1-pro"><strong>inf-retriever-v1-pro</strong></a>

Both models are released under Apache-2.0 for research and production use.

---

## 📄 License

INF-X-Retriever is released under the <a href="https://opensource.org/licenses/Apache-2.0">Apache-2.0</a> License.

---

## 📝 Citation

If you use INF-X-Retriever in your research or products, please cite:

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

We welcome collaboration and inquiries from researchers and practitioners interested in reasoning-intensive retrieval.

Email: <a href="mailto:eason.yyc@inftech.ai">eason.yyc@inftech.ai</a>

For technical discussions, collaborations, or deployment questions, please get in touch.
