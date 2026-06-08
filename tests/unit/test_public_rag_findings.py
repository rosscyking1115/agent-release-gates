from pathlib import Path

from internal_ai_agent.evals.public_rag_findings import write_public_rag_findings


def test_public_rag_findings_writes_not_configured_report(tmp_path: Path) -> None:
    report = write_public_rag_findings(tmp_path)

    assert report["status"] == "not_configured"
    assert report["summary"]["evaluated_track_count"] == 0
    assert (tmp_path / "reports/public_rag_findings.json").exists()


def test_public_rag_findings_combines_public_tracks(tmp_path: Path) -> None:
    techqa = _public_report(
        dataset="nvidia/TechQA-RAG-Eval",
        benchmark_track="external_public_rag",
        case_count=4,
        document_count=6,
        failed_case_count=1,
        retrieval_hit_rate_at_3=0.75,
        top1_citation_accuracy=0.5,
        retrieval_lift=0.25,
        top1_lift=0.2,
        taxonomy_labels={"weak_evidence_treated_as_strong": 1},
        dataset_specific_metrics={
            "impossible_abstention_rate": 0.5,
            "answerable_false_abstention_rate": 0.0,
        },
    )
    wixqa = _public_report(
        dataset="Wix/WixQA expert-written",
        benchmark_track="external_public_enterprise_rag",
        case_count=6,
        document_count=8,
        failed_case_count=2,
        retrieval_hit_rate_at_3=0.5,
        top1_citation_accuracy=0.3333,
        retrieval_lift=0.1,
        top1_lift=0.05,
        taxonomy_labels={"wrong_citation": 2},
        dataset_specific_metrics={"multi_article_retrieval_hit_rate_at_3": 0.8},
    )

    report = write_public_rag_findings(
        tmp_path,
        techqa_public=techqa,
        wixqa_public=wixqa,
    )

    summary = report["summary"]
    assert report["status"] == "evaluated"
    assert summary["evaluated_track_count"] == 2
    assert summary["total_case_count"] == 10
    assert summary["total_document_count"] == 14
    assert summary["total_failed_case_count"] == 3
    assert summary["weighted_retrieval_hit_rate_at_3"] == 0.6
    assert summary["weighted_top1_citation_accuracy"] == 0.4
    assert summary["weighted_failure_rate"] == 0.3
    assert summary["top_cross_track_failure_label"] == "wrong_citation (2)"
    assert summary["largest_retrieval_lift_track"] == "nvidia/TechQA-RAG-Eval (+25.00%)"
    assert any("WixQA adds multi-article" in item for item in report["findings"])


def _public_report(
    *,
    dataset: str,
    benchmark_track: str,
    case_count: int,
    document_count: int,
    failed_case_count: int,
    retrieval_hit_rate_at_3: float,
    top1_citation_accuracy: float,
    retrieval_lift: float,
    top1_lift: float,
    taxonomy_labels: dict[str, int],
    dataset_specific_metrics: dict[str, float],
) -> dict[str, object]:
    metrics = {
        "retrieval_hit_rate_at_3": retrieval_hit_rate_at_3,
        "top1_citation_accuracy": top1_citation_accuracy,
        "mean_reciprocal_rank_at_3": top1_citation_accuracy,
        **dataset_specific_metrics,
    }
    primary_id = "primary"
    baseline_id = "baseline"
    return {
        "status": "evaluated",
        "dataset": dataset,
        "benchmark_track": benchmark_track,
        "license": "MIT",
        "case_count": case_count,
        "document_count": document_count,
        "metrics": metrics,
        "benchmark_profile": {
            "failed_case_count": failed_case_count,
            "failure_rate": failed_case_count / case_count,
        },
        "primary_retriever": {"system_id": primary_id, "label": "Primary"},
        "retriever_systems": [
            {"system_id": baseline_id, "label": "Baseline"},
            {"system_id": primary_id, "label": "Primary"},
        ],
        "retriever_comparison": {
            "baseline_system_id": baseline_id,
            "primary_system_id": primary_id,
            "retrieval_hit_rate_at_3_lift": retrieval_lift,
            "top1_citation_accuracy_lift": top1_lift,
        },
        "failure_reasons": {},
        "taxonomy_labels": taxonomy_labels,
    }
