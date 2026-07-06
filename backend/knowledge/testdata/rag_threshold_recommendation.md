# RAG Threshold Recommendation

- 当前生产 Threshold: `0.35`
- F1 最佳 Threshold: `0.20`
- 最终推荐 Threshold: `0.20`
- 是否值得修改: `recommend_change`

## 结论

建议将生产 Threshold 调整为 0.20，F1 从 0.8544 提升到 0.8704。

## 当前阈值指标

- Precision: 1.0000
- Recall: 0.7458
- F1: 0.8544
- Accuracy: 0.8171
- FP/FN: 0/15
- Reject Rate: 0.4634

## F1 最佳阈值指标

- Threshold: 0.20
- Precision: 0.9592
- Recall: 0.7966
- F1: 0.8704
- Accuracy: 0.8293
- FP/FN: 2/12
- F1 Delta vs Current: 0.016001
- FP Delta at Best F1: 2
- FN Delta at Best F1: -3

## 建议上线方案

先以灰度方式使用推荐阈值，重点观察误拒的 answerable case 和无答案放行。

## 主要风险

- 本分析不重新运行 Anchor Gate；Anchor 拒答状态来自现有评测报告。
- 样本量为 82 条，适合做方向判断，不适合过度拟合阈值。