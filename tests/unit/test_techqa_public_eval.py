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
    assert report["metrics"]["retrieval_hit_rate_at_3"] == 1.0
    assert report["metrics"]["top1_citation_accuracy"] == 1.0
    assert report["metrics"]["impossible_abstention_rate"] == 1.0
    assert (tmp_path / "reports/techqa_public_rag_summary.json").exists()
    assert (tmp_path / "reports/techqa_public_rag_cases.jsonl").exists()

    persisted = json.loads(
        (tmp_path / "reports/techqa_public_rag_summary.json").read_text(encoding="utf-8")
    )
    assert persisted["license"] == "Apache-2.0"


def test_techqa_public_eval_writes_not_configured_report(tmp_path: Path) -> None:
    report = evaluate_techqa_public(tmp_path)

    assert report["status"] == "not_configured"
    assert report["case_count"] == 0
    assert (tmp_path / "reports/techqa_public_rag_summary.json").exists()
