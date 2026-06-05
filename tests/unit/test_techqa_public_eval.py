from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.techqa_public import evaluate_techqa_public
from internal_ai_agent.io import write_jsonl


def test_techqa_public_eval_scores_public_rag_sample(tmp_path: Path) -> None:
    sample_path = tmp_path / "data/public/techqa_rag_eval_sample.jsonl"
    write_jsonl(
        sample_path,
        [
            {
                "id": "TECHQA-001",
                "question": "How do I configure SSL mutual authentication in IBM HTTP Server?",
                "answer": "Configure GSKit, create a key database, and enable SSL directives.",
                "is_impossible": False,
                "contexts": [
                    {
                        "filename": "ssl_setup.txt",
                        "text": (
                            "Title: IBM HTTP Server SSL mutual authentication setup\n\n"
                            "Text: Configure GSKit, create the key database, create certificates, "
                            "and enable SSL directives in httpd.conf."
                        ),
                    }
                ],
            },
            {
                "id": "TECHQA-002",
                "question": "Where is the unsupported queue manager cluster answer?",
                "answer": "-",
                "is_impossible": True,
                "contexts": [],
            },
        ],
    )

    report = evaluate_techqa_public(tmp_path)

    assert report["status"] == "evaluated"
    assert report["case_count"] == 2
    assert report["answerable_case_count"] == 1
    assert report["impossible_case_count"] == 1
    assert report["benchmark_profile"]["sample_case_count"] == 2
    assert report["benchmark_profile"]["unique_document_count"] == 1
    assert report["benchmark_profile"]["provider_backed_embedding_result_published"] is False
    assert report["primary_retriever"]["system_id"] == "local_tfidf_public_retriever"
    assert report["retriever_comparison"]["system_count"] == 2
    assert {system["system_id"] for system in report["retriever_systems"]} == {
        "keyword_title_baseline",
        "local_tfidf_public_retriever",
    }
    assert report["metrics"]["retrieval_hit_rate_at_3"] == 1.0
    assert report["metrics"]["top1_citation_accuracy"] == 1.0
    assert report["metrics"]["impossible_abstention_rate"] == 1.0
    assert (tmp_path / "reports/techqa_public_rag_summary.json").exists()
    assert (tmp_path / "reports/techqa_public_benchmark_profile.json").exists()
    assert (tmp_path / "reports/techqa_public_rag_cases.jsonl").exists()
    assert (tmp_path / "reports/techqa_public_retriever_comparison.json").exists()
    assert (tmp_path / "reports/techqa_public_retriever_cases.jsonl").exists()

    persisted = json.loads(
        (tmp_path / "reports/techqa_public_rag_summary.json").read_text(encoding="utf-8")
    )
    assert persisted["license"] == "Apache-2.0"
    profile = json.loads(
        (tmp_path / "reports/techqa_public_benchmark_profile.json").read_text(
            encoding="utf-8"
        )
    )
    assert profile["summary"]["sample_scope"] == "tracked_compact_public_sample"


def test_techqa_public_eval_writes_not_configured_report(tmp_path: Path) -> None:
    report = evaluate_techqa_public(tmp_path)

    assert report["status"] == "not_configured"
    assert report["case_count"] == 0
    assert report["benchmark_profile"]["sample_case_count"] == 0
    assert (tmp_path / "reports/techqa_public_rag_summary.json").exists()
    assert (tmp_path / "reports/techqa_public_benchmark_profile.json").exists()
    assert (tmp_path / "reports/techqa_public_retriever_comparison.json").exists()
    assert (tmp_path / "reports/techqa_public_retriever_cases.jsonl").exists()
