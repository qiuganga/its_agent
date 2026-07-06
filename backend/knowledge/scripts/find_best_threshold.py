from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
TESTDATA = KNOWLEDGE_ROOT / "testdata"

INPUT_REPORT = TESTDATA / "rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker.json"
OUT_JSON = TESTDATA / "rag_threshold_analysis.json"
OUT_MD = TESTDATA / "rag_threshold_analysis.md"
OUT_RECOMMENDATION_MD = TESTDATA / "rag_threshold_recommendation.md"
ROC_PNG = TESTDATA / "roc_curve.png"
PR_PNG = TESTDATA / "pr_curve.png"
F1_PNG = TESTDATA / "threshold_f1.png"
PRECISION_RECALL_PNG = TESTDATA / "threshold_precision_recall.png"

THRESHOLDS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
CURRENT_THRESHOLD = 0.35


@dataclass(frozen=True)
class CaseDecision:
    case_id: str
    question: str
    expected_answerability: str
    score: float
    anchor_rejected: bool
    accepted: bool
    correct: bool


def load_report(path: Path = INPUT_REPORT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    validate_report(report)
    return report


def validate_report(report: dict[str, Any]) -> None:
    summary = report.get("summary") or {}
    settings = report.get("settings") or {}
    errors = []
    if report.get("status") != "success":
        errors.append(f"report status is {report.get('status')}")
    if summary.get("total_cases") != 82:
        errors.append(f"total_cases must be 82, got {summary.get('total_cases')}")
    if summary.get("reranker_provider") != "siliconflow":
        errors.append("reranker_provider must be siliconflow")
    if summary.get("reranker_model") != "Qwen/Qwen3-Reranker-8B":
        errors.append(f"unexpected reranker_model={summary.get('reranker_model')}")
    if summary.get("reranker_success_count") != 82 or summary.get("reranker_failure_count") != 0:
        errors.append("reranker success/failure counts are not 82/0")
    if summary.get("anchor_evidence_mode") != "hard-soft-negative":
        errors.append("anchor_evidence_mode must be hard-soft-negative")
    if summary.get("bm25_mode") != "experimental":
        errors.append("bm25_mode must be experimental")
    if settings.get("collection_name") != "its-knowledge-clean-v1":
        errors.append(f"collection_name must be its-knowledge-clean-v1, got {settings.get('collection_name')}")
    if errors:
        raise ValueError("; ".join(errors))


def score_case(case: dict[str, Any], threshold: float) -> CaseDecision:
    score = float(case.get("top_score") or 0.0)
    expected = case.get("expected_answerability") or ("unanswerable" if case.get("expected_no_answer") else "answerable")
    anchor_rejected = bool(case.get("rejected_by_anchor_evidence"))
    accepted = score >= threshold and not anchor_rejected
    correct = accepted if expected == "answerable" else not accepted
    return CaseDecision(
        case_id=case["case_id"],
        question=case.get("original_question") or "",
        expected_answerability=expected,
        score=score,
        anchor_rejected=anchor_rejected,
        accepted=accepted,
        correct=correct,
    )


def evaluate_threshold(cases: list[dict[str, Any]], threshold: float, baseline: dict[str, CaseDecision]) -> dict[str, Any]:
    decisions = [score_case(case, threshold) for case in cases]
    tp = sum(1 for item in decisions if item.expected_answerability == "answerable" and item.accepted)
    fp = sum(1 for item in decisions if item.expected_answerability == "unanswerable" and item.accepted)
    tn = sum(1 for item in decisions if item.expected_answerability == "unanswerable" and not item.accepted)
    fn = sum(1 for item in decisions if item.expected_answerability == "answerable" and not item.accepted)
    total = len(decisions)
    accepted = tp + fp
    rejected = tn + fn
    current_decision_by_case = baseline

    newly_rejected = [item.case_id for item in decisions if current_decision_by_case[item.case_id].accepted and not item.accepted]
    newly_accepted = [item.case_id for item in decisions if not current_decision_by_case[item.case_id].accepted and item.accepted]
    false_reject_increase = [
        item.case_id
        for item in decisions
        if item.expected_answerability == "answerable" and current_decision_by_case[item.case_id].accepted and not item.accepted
    ]
    false_accept_increase = [
        item.case_id
        for item in decisions
        if item.expected_answerability == "unanswerable" and not current_decision_by_case[item.case_id].accepted and item.accepted
    ]
    improved_cases = [
        item.case_id
        for item in decisions
        if not current_decision_by_case[item.case_id].correct and item.correct
    ]
    regressed_cases = [
        item.case_id
        for item in decisions
        if current_decision_by_case[item.case_id].correct and not item.correct
    ]

    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    accuracy = safe_div(tp + tn, total)
    f1 = safe_div(2 * precision * recall, precision + recall)
    return {
        "threshold": threshold,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1": f1,
        "false_positive_rate": safe_div(fp, fp + tn),
        "false_negative_rate": safe_div(fn, fn + tp),
        "reject_rate": safe_div(rejected, total),
        "accepted_rate": safe_div(accepted, total),
        "newly_rejected_cases": newly_rejected,
        "newly_accepted_cases": newly_accepted,
        "false_reject_increase_cases": false_reject_increase,
        "false_accept_increase_cases": false_accept_increase,
        "improved_cases": improved_cases,
        "regressed_cases": regressed_cases,
    }


def safe_div(left: float, right: float) -> float:
    return round(left / right, 6) if right else 0.0


def best_by(rows: list[dict[str, Any]], metric: str) -> dict[str, Any]:
    return max(rows, key=lambda row: (row[metric], -abs(row["threshold"] - CURRENT_THRESHOLD)))


def build_case_change_summary(cases: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    case_map = {case["case_id"]: case for case in cases}
    counts: dict[str, dict[str, Any]] = {}
    for row in rows:
        threshold = row["threshold"]
        for kind in ("improved_cases", "regressed_cases", "newly_rejected_cases", "newly_accepted_cases"):
            for case_id in row[kind]:
                entry = counts.setdefault(
                    case_id,
                    {
                        "case_id": case_id,
                        "question": case_map[case_id].get("original_question") or "",
                        "expected_answerability": case_map[case_id].get("expected_answerability"),
                        "score": case_map[case_id].get("top_score"),
                        "change_count": 0,
                        "thresholds": [],
                        "change_types": set(),
                    },
                )
                entry["change_count"] += 1
                entry["thresholds"].append(threshold)
                entry["change_types"].add(kind)
    ranked = sorted(counts.values(), key=lambda item: (-item["change_count"], item["case_id"]))
    for item in ranked:
        item["change_types"] = sorted(item["change_types"])
        item["thresholds"] = sorted(set(item["thresholds"]))
    return ranked[:20]


def build_recommendation(rows: list[dict[str, Any]], case_changes: list[dict[str, Any]]) -> dict[str, Any]:
    current = next(row for row in rows if math.isclose(row["threshold"], CURRENT_THRESHOLD))
    best_f1 = best_by(rows, "f1")
    best_accuracy = best_by(rows, "accuracy")
    best_precision = best_by(rows, "precision")
    best_recall = best_by(rows, "recall")

    f1_delta = best_f1["f1"] - current["f1"]
    fp_delta = best_f1["FP"] - current["FP"]
    fn_delta = best_f1["FN"] - current["FN"]
    materially_better = f1_delta >= 0.01 and not (fn_delta > 0 and fp_delta >= 0)
    if materially_better:
        recommended_threshold = best_f1["threshold"]
        decision = "recommend_change"
        message = (
            f"建议将生产 Threshold 调整为 {recommended_threshold:.2f}，"
            f"F1 从 {current['f1']:.4f} 提升到 {best_f1['f1']:.4f}。"
        )
    else:
        recommended_threshold = CURRENT_THRESHOLD
        decision = "keep_current"
        message = "当前 0.35 已经接近最优，不建议调整生产 Threshold。"

    return {
        "current_threshold": CURRENT_THRESHOLD,
        "recommended_threshold": recommended_threshold,
        "decision": decision,
        "message": message,
        "current_metrics": summarize_row(current),
        "best_precision": summarize_row(best_precision),
        "best_recall": summarize_row(best_recall),
        "best_f1": summarize_row(best_f1),
        "best_accuracy": summarize_row(best_accuracy),
        "f1_delta_vs_current": round(f1_delta, 6),
        "fp_delta_at_best_f1": fp_delta,
        "fn_delta_at_best_f1": fn_delta,
        "top_changed_cases": case_changes[:20],
    }


def summarize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "threshold": row["threshold"],
        "precision": row["precision"],
        "recall": row["recall"],
        "f1": row["f1"],
        "accuracy": row["accuracy"],
        "FP": row["FP"],
        "FN": row["FN"],
        "reject_rate": row["reject_rate"],
        "accepted_rate": row["accepted_rate"],
    }


def write_plots(rows: list[dict[str, Any]]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("matplotlib is required to generate threshold PNG reports") from exc

    thresholds = [row["threshold"] for row in rows]

    plt.figure()
    plt.plot([row["false_positive_rate"] for row in rows], [row["recall"] for row in rows], marker="o")
    for row in rows:
        plt.annotate(f"{row['threshold']:.2f}", (row["false_positive_rate"], row["recall"]))
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate / Recall")
    plt.title("ROC Curve")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(ROC_PNG)
    plt.close()

    plt.figure()
    plt.plot([row["recall"] for row in rows], [row["precision"] for row in rows], marker="o")
    for row in rows:
        plt.annotate(f"{row['threshold']:.2f}", (row["recall"], row["precision"]))
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PR_PNG)
    plt.close()

    plt.figure()
    plt.plot(thresholds, [row["f1"] for row in rows], marker="o")
    plt.xlabel("Threshold")
    plt.ylabel("F1")
    plt.title("Threshold vs F1")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(F1_PNG)
    plt.close()

    plt.figure()
    plt.plot(thresholds, [row["precision"] for row in rows], marker="o", label="Precision")
    plt.plot(thresholds, [row["recall"] for row in rows], marker="o", label="Recall")
    plt.xlabel("Threshold")
    plt.ylabel("Score")
    plt.title("Threshold vs Precision / Recall")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PRECISION_RECALL_PNG)
    plt.close()


def render_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# RAG Threshold Analysis",
        "",
        f"- Input report: `{analysis['input_report']}`",
        f"- Current production threshold: `{CURRENT_THRESHOLD:.2f}`",
        f"- Recommendation: **{analysis['recommendation']['message']}**",
        "",
        "## Threshold Metrics",
        "",
        "| Threshold | TP | FP | TN | FN | Precision | Recall | F1 | Accuracy | Reject Rate | Accepted Rate | FPR | FNR |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in analysis["thresholds"]:
        lines.append(
            f"| {row['threshold']:.2f} | {row['TP']} | {row['FP']} | {row['TN']} | {row['FN']} | "
            f"{row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} | {row['accuracy']:.4f} | "
            f"{row['reject_rate']:.4f} | {row['accepted_rate']:.4f} | {row['false_positive_rate']:.4f} | "
            f"{row['false_negative_rate']:.4f} |"
        )
    lines.extend([
        "",
        "## Best Metrics",
        "",
    ])
    for key in ("best_precision", "best_recall", "best_f1", "best_accuracy"):
        lines.append(f"- {key}: {analysis['recommendation'][key]}")
    lines.extend([
        "",
        "## Top Changed Cases",
        "",
    ])
    for item in analysis["top_changed_cases"]:
        lines.append(
            f"- {item['case_id']} | expected={item['expected_answerability']} | score={item['score']} | "
            f"changes={item['change_count']} | types={item['change_types']} | thresholds={item['thresholds']}"
        )
    lines.extend([
        "",
        "## Notes",
        "",
        "- Positive means an answerable case should be accepted.",
        "- Negative means an unanswerable case should be rejected.",
        "- Anchor rejection from the source report is kept fixed for all thresholds because this script does not rerun retrieval.",
        "- No Reranker, Chroma, Embedding, or LLM calls are made.",
    ])
    return "\n".join(lines)


def render_recommendation(analysis: dict[str, Any]) -> str:
    rec = analysis["recommendation"]
    current = rec["current_metrics"]
    best = rec["best_f1"]
    lines = [
        "# RAG Threshold Recommendation",
        "",
        f"- 当前生产 Threshold: `{rec['current_threshold']:.2f}`",
        f"- F1 最佳 Threshold: `{best['threshold']:.2f}`",
        f"- 最终推荐 Threshold: `{rec['recommended_threshold']:.2f}`",
        f"- 是否值得修改: `{rec['decision']}`",
        "",
        "## 结论",
        "",
        rec["message"],
        "",
        "## 当前阈值指标",
        "",
        f"- Precision: {current['precision']:.4f}",
        f"- Recall: {current['recall']:.4f}",
        f"- F1: {current['f1']:.4f}",
        f"- Accuracy: {current['accuracy']:.4f}",
        f"- FP/FN: {current['FP']}/{current['FN']}",
        f"- Reject Rate: {current['reject_rate']:.4f}",
        "",
        "## F1 最佳阈值指标",
        "",
        f"- Threshold: {best['threshold']:.2f}",
        f"- Precision: {best['precision']:.4f}",
        f"- Recall: {best['recall']:.4f}",
        f"- F1: {best['f1']:.4f}",
        f"- Accuracy: {best['accuracy']:.4f}",
        f"- FP/FN: {best['FP']}/{best['FN']}",
        f"- F1 Delta vs Current: {rec['f1_delta_vs_current']:.6f}",
        f"- FP Delta at Best F1: {rec['fp_delta_at_best_f1']}",
        f"- FN Delta at Best F1: {rec['fn_delta_at_best_f1']}",
        "",
        "## 建议上线方案",
        "",
    ]
    if rec["decision"] == "keep_current":
        lines.append("保持当前 `0.35`，暂不调整生产阈值；继续用真实线上日志扩充样本后再复评。")
    else:
        lines.append("先以灰度方式使用推荐阈值，重点观察误拒的 answerable case 和无答案放行。")
    lines.extend([
        "",
        "## 主要风险",
        "",
        "- 本分析不重新运行 Anchor Gate；Anchor 拒答状态来自现有评测报告。",
        "- 样本量为 82 条，适合做方向判断，不适合过度拟合阈值。",
    ])
    return "\n".join(lines)


def main() -> int:
    report = load_report()
    cases = report["results"]
    baseline = {case["case_id"]: score_case(case, CURRENT_THRESHOLD) for case in cases}
    rows = [evaluate_threshold(cases, threshold, baseline) for threshold in THRESHOLDS]
    case_changes = build_case_change_summary(cases, rows)
    analysis = {
        "input_report": str(INPUT_REPORT),
        "thresholds": rows,
        "top_changed_cases": case_changes,
        "recommendation": build_recommendation(rows, case_changes),
        "plots": {
            "roc_curve": str(ROC_PNG),
            "pr_curve": str(PR_PNG),
            "threshold_f1": str(F1_PNG),
            "threshold_precision_recall": str(PRECISION_RECALL_PNG),
        },
    }
    write_plots(rows)
    OUT_JSON.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_markdown(analysis), encoding="utf-8")
    OUT_RECOMMENDATION_MD.write_text(render_recommendation(analysis), encoding="utf-8")
    print("RAG threshold analysis completed")
    print(f"best_f1={analysis['recommendation']['best_f1']}")
    print(f"recommendation={analysis['recommendation']['message']}")
    print(f"json_report={OUT_JSON}")
    print(f"md_report={OUT_MD}")
    print(f"recommendation_report={OUT_RECOMMENDATION_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
