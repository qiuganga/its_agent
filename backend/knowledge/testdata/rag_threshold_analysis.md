# RAG Threshold Analysis

- Input report: `D:\sgg-agent\code\its_multi_agent\backend\knowledge\testdata\rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker.json`
- Current production threshold: `0.35`
- Recommendation: **建议将生产 Threshold 调整为 0.20，F1 从 0.8544 提升到 0.8704。**

## Threshold Metrics

| Threshold | TP | FP | TN | FN | Precision | Recall | F1 | Accuracy | Reject Rate | Accepted Rate | FPR | FNR |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 47 | 2 | 21 | 12 | 0.9592 | 0.7966 | 0.8704 | 0.8293 | 0.4024 | 0.5976 | 0.0870 | 0.2034 |
| 0.25 | 46 | 1 | 22 | 13 | 0.9787 | 0.7797 | 0.8679 | 0.8293 | 0.4268 | 0.5732 | 0.0435 | 0.2203 |
| 0.30 | 44 | 1 | 22 | 15 | 0.9778 | 0.7458 | 0.8462 | 0.8049 | 0.4512 | 0.5488 | 0.0435 | 0.2542 |
| 0.35 | 44 | 0 | 23 | 15 | 1.0000 | 0.7458 | 0.8544 | 0.8171 | 0.4634 | 0.5366 | 0.0000 | 0.2542 |
| 0.40 | 44 | 0 | 23 | 15 | 1.0000 | 0.7458 | 0.8544 | 0.8171 | 0.4634 | 0.5366 | 0.0000 | 0.2542 |
| 0.45 | 44 | 0 | 23 | 15 | 1.0000 | 0.7458 | 0.8544 | 0.8171 | 0.4634 | 0.5366 | 0.0000 | 0.2542 |
| 0.50 | 44 | 0 | 23 | 15 | 1.0000 | 0.7458 | 0.8544 | 0.8171 | 0.4634 | 0.5366 | 0.0000 | 0.2542 |
| 0.55 | 44 | 0 | 23 | 15 | 1.0000 | 0.7458 | 0.8544 | 0.8171 | 0.4634 | 0.5366 | 0.0000 | 0.2542 |
| 0.60 | 42 | 0 | 23 | 17 | 1.0000 | 0.7119 | 0.8317 | 0.7927 | 0.4878 | 0.5122 | 0.0000 | 0.2881 |

## Best Metrics

- best_precision: {'threshold': 0.35, 'precision': 1.0, 'recall': 0.745763, 'f1': 0.854369, 'accuracy': 0.817073, 'FP': 0, 'FN': 15, 'reject_rate': 0.463415, 'accepted_rate': 0.536585}
- best_recall: {'threshold': 0.2, 'precision': 0.959184, 'recall': 0.79661, 'f1': 0.87037, 'accuracy': 0.829268, 'FP': 2, 'FN': 12, 'reject_rate': 0.402439, 'accepted_rate': 0.597561}
- best_f1: {'threshold': 0.2, 'precision': 0.959184, 'recall': 0.79661, 'f1': 0.87037, 'accuracy': 0.829268, 'FP': 2, 'FN': 12, 'reject_rate': 0.402439, 'accepted_rate': 0.597561}
- best_accuracy: {'threshold': 0.25, 'precision': 0.978723, 'recall': 0.779661, 'f1': 0.867924, 'accuracy': 0.829268, 'FP': 1, 'FN': 13, 'reject_rate': 0.426829, 'accepted_rate': 0.573171}

## Top Changed Cases

- case_023 | expected=unanswerable | score=0.32175037264823914 | changes=6 | types=['newly_accepted_cases', 'regressed_cases'] | thresholds=[0.2, 0.25, 0.3]
- case_021 | expected=answerable | score=0.26707783341407776 | changes=4 | types=['improved_cases', 'newly_accepted_cases'] | thresholds=[0.2, 0.25]
- case_069 | expected=answerable | score=0.2679237723350525 | changes=4 | types=['improved_cases', 'newly_accepted_cases'] | thresholds=[0.2, 0.25]
- case_045 | expected=unanswerable | score=0.2478993982076645 | changes=2 | types=['newly_accepted_cases', 'regressed_cases'] | thresholds=[0.2]
- case_058 | expected=answerable | score=0.2097383290529251 | changes=2 | types=['improved_cases', 'newly_accepted_cases'] | thresholds=[0.2]
- case_074 | expected=answerable | score=0.5562381148338318 | changes=2 | types=['newly_rejected_cases', 'regressed_cases'] | thresholds=[0.6]
- case_077 | expected=answerable | score=0.5515531301498413 | changes=2 | types=['newly_rejected_cases', 'regressed_cases'] | thresholds=[0.6]

## Notes

- Positive means an answerable case should be accepted.
- Negative means an unanswerable case should be rejected.
- Anchor rejection from the source report is kept fixed for all thresholds because this script does not rerun retrieval.
- No Reranker, Chroma, Embedding, or LLM calls are made.