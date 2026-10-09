"""Validate existing long-track scores without model/API calls.

Dependencies: datasets, pytrec_eval. The same file is shipped in INF-X-Retriever.
Scores are document-level, not chunk-level. Never average a partial task set.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import zipfile

import pytrec_eval

TASKS = (
    "biology", "earth_science", "economics", "pony", "psychology",
    "robotics", "stackoverflow", "sustainable_living",
)
DATASET_REVISION = "3066d29c9651a576c8aba4832d249807b181ecae"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_task(run, examples, doc_ids):
    """Fail closed on incomplete runs, invalid scores, IDs, or exclusions."""
    examples = list(examples)
    qids = [str(e["id"]) for e in examples]
    if len(set(qids)) != len(qids) or not qids:
        raise ValueError("Empty or duplicate query IDs")
    corpus = set(doc_ids)
    if len(corpus) != len(doc_ids):
        raise ValueError("Duplicate document IDs")
    if not isinstance(run, dict) or set(run) != set(qids):
        raise ValueError("Score query IDs must exactly match official examples")
    qrels = {}
    multi_gold = 0
    for e in examples:
        qid = str(e["id"])
        gold = set(e["gold_ids_long"])
        excluded = set(e["excluded_ids"]) - {"N/A"}
        if not gold or not gold <= corpus or gold & excluded:
            raise ValueError(f"{qid}: invalid long-document qrels")
        multi_gold += len(gold) > 1
        scores = run[qid]
        if not isinstance(scores, dict) or not 1 <= len(scores) <= 1000:
            raise ValueError(f"{qid}: expected 1..1000 document scores")
        if not set(scores) <= corpus or set(scores) & excluded:
            raise ValueError(f"{qid}: unknown/chunk-level/excluded document ID")
        if any(isinstance(s, bool) or not isinstance(s, (int, float))
               or not math.isfinite(s) for s in scores.values()):
            raise ValueError(f"{qid}: scores must be finite numbers")
        qrels[qid] = {gid: 1 for gid in gold}
    metrics = pytrec_eval.RelevanceEvaluator(qrels, {"recall.1"}).evaluate(run)
    if set(metrics) != set(qids):
        raise ValueError("Evaluator did not cover every query")
    recall = sum(m["recall_1"] for m in metrics.values()) / len(metrics)
    return {
        "queries": len(qids), "documents": len(corpus),
        "queries_with_multiple_gold_documents": multi_gold,
        "Recall@1": round(recall, 5),
        "Recall@1_unrounded": recall,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--expected", type=Path,
                        help="Previously frozen report: require identical score hashes and metrics")
    args = parser.parse_args()
    from datasets import load_dataset

    examples = load_dataset("xlangai/bright", "examples", revision=DATASET_REVISION)
    corpus = load_dataset("xlangai/bright", "long_documents", revision=DATASET_REVISION)
    # datasets' offline fallback can silently select a different cached revision.
    for dataset in (examples, corpus):
        for task in TASKS:
            if not dataset[task].cache_files or any(
                DATASET_REVISION not in f["filename"] for f in dataset[task].cache_files
            ):
                raise ValueError("Cannot verify pinned dataset cache revision")
    if {p.name for p in args.scores.glob("*.json")} != {f"{t}.json" for t in TASKS}:
        raise ValueError("Submission must contain exactly eight task JSON files")
    report = {
        "track": "BRIGHT long document", "metric": "macro-average Recall@1 x 100",
        "dataset": "xlangai/bright", "dataset_revision": DATASET_REVISION,
        "status": "locally validated; not an official leaderboard acceptance",
        "tasks": {},
    }
    for task in TASKS:
        path = args.scores / f"{task}.json"
        run = json.loads(path.read_text(), object_pairs_hook=unique_object)
        result = validate_task(run, examples[task], list(corpus[task]["id"]))
        result.update({
            "score_sha256": sha256(path),
            "examples_fingerprint": examples[task]._fingerprint,
            "corpus_fingerprint": corpus[task]._fingerprint,
        })
        report["tasks"][task] = result
        print(f"{task}: {result['queries']} queries; Recall@1={result['Recall@1']}")
    report["average_recall_at_1_percent"] = round(
        sum(r["Recall@1"] for r in report["tasks"].values()) / len(TASKS) * 100, 6)
    if args.expected:
        expected = json.loads(args.expected.read_text())
        if report != expected:
            raise ValueError("Scores/data/metrics differ from frozen validation report")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, indent=2) + "\n"
    args.report.write_text(text)
    if args.archive:
        args.archive.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.archive, "w", zipfile.ZIP_DEFLATED) as archive:
            for task in TASKS:
                archive.write(args.scores / f"{task}.json", f"scores/{task}.json")
            archive.writestr("validation.json", text)
            archive.write(__file__, "validate_long_submission.py")
    print(f"Average Recall@1: {report['average_recall_at_1_percent']:.4f}")


if __name__ == "__main__":
    main()
