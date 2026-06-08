from __future__ import annotations

import json
from pathlib import Path

from internal_ai_agent.evals.wixqa_public import (
    evaluate_wixqa_public,
    write_wixqa_sample,
)
from internal_ai_agent.io import write_jsonl


def test_wixqa_public_eval_scores_public_enterprise_rag_sample(
    tmp_path: Path,
) -> None:
    sample_path = tmp_path / "data/public/wixqa_public_rag_sample.jsonl"
    expected_doc_id = "doc-payments"
    write_jsonl(
        sample_path,
        [
            {
                "id": "WIXQA-001",
                "question": "Can I accept payments before Wix Payments verification finishes?",
                "answer": "You can start accepting payments while verification is pending.",
                "article_ids": [expected_doc_id],
                "contexts": [
                    {
                        "id": expected_doc_id,
                        "title": "Accepting Payments While Wix Payments Verification Is Pending",
                        "url": "https://support.wix.com/en/article/payments-verification",
                        "article_type": "article",
                        "text": (
                            "Accepting Payments While Wix Payments Verification Is Pending\n"
                            "You can start accepting payments while account verification is "
                            "still under review, but payouts may wait until verification."
                        ),
                    },
                    {
                        "id": "doc-domain",
                        "title": "Claiming a Free Domain Voucher",
                        "url": "https://support.wix.com/en/article/domain-voucher",
                        "article_type": "article",
                        "text": "A yearly premium plan can include a free domain voucher.",
                    },
                ],
            }
        ],
    )

    report = evaluate_wixqa_public(tmp_path)

    assert report["status"] == "evaluated"
    assert report["case_count"] == 1
    assert report["document_count"] == 2
    assert report["license"] == "MIT"
    assert report["primary_retriever"]["system_id"] == "local_tfidf_wixqa_retriever"
    assert report["metrics"]["retrieval_hit_rate_at_3"] == 1.0
    assert report["metrics"]["top1_citation_accuracy"] == 1.0
    assert (tmp_path / "reports/wixqa_public_rag_summary.json").exists()
    assert (tmp_path / "reports/wixqa_public_benchmark_profile.json").exists()
    assert (tmp_path / "reports/wixqa_public_rag_cases.jsonl").exists()
    assert (tmp_path / "reports/wixqa_public_retriever_comparison.json").exists()
    assert (tmp_path / "reports/wixqa_public_retriever_cases.jsonl").exists()

    persisted = json.loads(
        (tmp_path / "reports/wixqa_public_rag_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert persisted["source_url"] == "https://huggingface.co/datasets/Wix/WixQA"


def test_wixqa_public_eval_writes_not_configured_report(tmp_path: Path) -> None:
    report = evaluate_wixqa_public(tmp_path)

    assert report["status"] == "not_configured"
    assert report["case_count"] == 0
    assert report["benchmark_profile"]["sample_case_count"] == 0
    assert (tmp_path / "reports/wixqa_public_rag_summary.json").exists()
    assert (tmp_path / "reports/wixqa_public_benchmark_profile.json").exists()
    assert (tmp_path / "reports/wixqa_public_retriever_comparison.json").exists()
    assert (tmp_path / "reports/wixqa_public_retriever_cases.jsonl").exists()


def test_write_wixqa_sample_compacts_raw_public_dataset(tmp_path: Path) -> None:
    article_id = "article-1"
    write_jsonl(
        tmp_path / "data/public/wixqa_expertwritten_test.jsonl",
        [
            {
                "question": "How do I claim the yearly plan domain voucher?",
                "answer": "Claim it after purchasing the yearly plan.",
                "article_ids": [article_id],
            }
        ],
    )
    write_jsonl(
        tmp_path / "data/public/wixqa_kb_corpus.jsonl",
        [
            {
                "id": article_id,
                "title": "Claiming a Free Domain Voucher",
                "url": "https://support.wix.com/en/article/domain-voucher",
                "article_type": "article",
                "contents": "Claiming a Free Domain Voucher\nAfter purchase, open vouchers.",
            }
        ],
    )

    output_path = write_wixqa_sample(tmp_path, limit=1, max_context_chars=32)

    rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["id"] == "WIXQA-EXPERT-0001"
    assert rows[0]["article_ids"] == [article_id]
    assert rows[0]["contexts"][0]["text"].startswith("Claiming a Free Domain Voucher")
    assert len(rows[0]["contexts"][0]["text"]) == 32
