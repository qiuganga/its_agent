# ITS / Knowledge RAG Final Experiment Summary

Generated at: `2026-07-06T22:05:38`

This report summarizes the existing local experiment artifacts only. No new RAG experiment, external API call, collection rebuild, BM25 rebuild, `/query` call, LLM call, MCP call, or git commit was performed while generating this report.

## 1. Current RAG Chain

```text
Query
-> Query Normalization
-> Alias Mapping
-> Vector Recall
-> Title Recall
-> BM25 Recall
-> Merge / Deduplicate
-> Embedding score
-> SiliconFlow Qwen Reranker
-> Anchor Adjustment
-> MMR
-> Threshold / Anchor Gate
-> Top2 documents
```

## 2. Current Best Experimental Configuration

| Area | Current value |
| --- | --- |
| Collection | `its-knowledge-clean-v1` |
| Embedding | `Qwen/Qwen3-Embedding-8B` |
| Reranker | `SiliconFlow Qwen/Qwen3-Reranker-8B` |
| BM25 | `experimental` |
| Anchor | `hard-soft-negative` |
| Alias Mapping | `enabled` |
| Production default threshold recommendation | `0.35` |
| Gray-test threshold candidate | `0.20` |
| Vector candidate top k | `15` |
| Title candidate top k | `10` |
| BM25 candidate top k | `10` |
| Final top k | `2` |

## 3. Experiment Conclusions

### A. Query Normalization

Query Normalization remains worth keeping. In the final 82-case Alias v2 report it triggered on `24` cases and left `58` unchanged. It provides a controlled rewrite step before retrieval, mainly for common symptom expressions such as boot failure, black screen, network, Bluetooth, and other high-frequency support language. The important guardrail is that it must not invent brand, model, OS version, or fault phenomena not present in the user query.

### B. Document Cleaning + clean-v1

The clean collection should be kept as the base collection. The clean collection comparison shows:

| Collection | Chunks | Metadata rate | Top1 hit | Top2 hit | Missing source topK |
| --- | ---: | ---: | ---: | ---: | ---: |
| old `its-knowledge` | 1101 | 0.0 | 4 | 6 | 36 |
| clean `its-knowledge-clean-v1` | 834 | 1.0 | 7 | 9 | 0 |
| clean chunk1000 | 974 | 1.0 | 4 | 6 | 0 |

`clean-v1` improved Top1 from 4 to 7 and Top2 from 6 to 9 versus the old collection, while metadata completeness improved from 0.0 to 1.0 and missing source in TopK dropped to 0. Chunk1000 did not improve Top1/Top2 versus old in this report, so it is not the current recommended default.

### C. Anchor Evidence

Legacy anchor behavior was too blunt: it improved some no-answer rejection but introduced too many false rejections. The hard / soft / negative split improved the tradeoff. In the HSN comparison:

- Baseline Top2: 9
- HSN experiment Top2: 15
- Legacy Top2: 19
- Baseline no-answer passed: 23
- HSN no-answer passed: 13
- Legacy no-answer passed: 14
- HSN false rejected answerable: 4
- Legacy false rejected answerable: 13

The conclusion is to keep HSN Anchor as an experimental guard and adjustment layer, but not to convert it into unconditional hard rejection for all cases. The report still listed anchor-missing cases and remaining accepted unanswerable cases, so manual review and gray rollout are required.

### D. BM25

BM25 is useful as candidate expansion, not as a standalone production answer selector. In the 82-case BM25 report:

- BM25 candidate delta: 889
- BM25 unique added delta: 687
- Top2 changed cases: 10
- Top1 changed from 10 to 11
- Top2 stayed 15 to 15
- Top2 weak-hit improved cases: none found in that comparison

The final Alias v2 report with BM25 experimental shows BM25 added `718` unique candidates. This is valuable recall insurance, but the direct hit-rate gain before reranking was limited; keep BM25 as experimental candidate expansion behind reranker and gates.

### E. SiliconFlow Reranker

Preflight passed: SiliconFlow `/rerank` returned HTTP 200, valid schema, valid ranking, model `Qwen/Qwen3-Reranker-8B`.

The 82-case reranker comparison showed the largest retrieval quality jump:

- Top1 weak-hit delta: `26`
- Top2 weak-hit delta: `23`
- Reranker improved cases: `24`
- Reranker regression cases: `1`
- Reranker success/failure: `82` / `0`
- Average latency: `3309.5853658536585` ms
- P95 latency: `5814.0` ms

It should not be directly full-volume enabled without operational controls because latency is material, Top2 changed in 79 cases, and 54 cases were classified as needing manual review.

### F. Threshold Calibration

Threshold analysis says 0.20 has the best F1, but 0.35 remains the safer production default.

| Threshold | Precision | Recall | F1 | Accuracy | FP | FN | Reject rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.35 current | 1.0 | 0.745763 | 0.854369 | 0.817073 | 0 | 15 | 0.463415 |
| 0.20 best F1 | 0.959184 | 0.79661 | 0.87037 | 0.829268 | 2 | 12 | 0.402439 |

0.20 improves F1 by `0.016001` and reduces FN by 3, but introduces 2 FP. Because this project is support-answer oriented and no-answer false acceptance is high-risk, 0.35 is the recommended production default; 0.20 is suitable for small-traffic gray testing with manual review.

### G. Alias Mapping

The confirmed Alias additions were:

- `win7`, `Win7` -> `Windows 7`
- `windows xp`, `xp`, `XP` -> `Windows XP`
- `Printer`, `printer` -> `打印机`

Alias v2 comparison results:

- Top1: `37` -> `37`, delta `0`
- Top2: `38` -> `38`, delta `0`
- False rejected answerable: `15` -> `14`
- Alias applied cases: `7`
- New alias hit cases: `6`
- Improved case: `case_082`
- Regression cases: none found in the comparison report

PowerPoint/PPT 和 任务栏输入法图标/输入法图标 were not added because the candidate mining stage marked them medium risk and the 82-case Alias v2 comparison did not provide enough confirmed benefit.

### H. MCP Contract / Harness

MCP/Harness changes address an engineering stability problem rather than RAG ranking quality. The contract layer standardizes dirty provider outputs into:

```python
McpResult(ok: bool, data: T | None, error: McpError | None, meta: McpMeta)
```

The stable semantic boundary is:

- `ok=True` with valid typed `data`: successful tool call.
- `ok=True` with empty items: successful empty result, not a technical failure.
- `ok=False` with `error`: technical/provider/input failure counted by Harness failure logic.

Covered error codes include `MCP_RESPONSE_JSON_INVALID`, `MCP_RESPONSE_SCHEMA_INVALID`, `MCP_TIMEOUT`, `MCP_NETWORK_ERROR`, `MCP_PROVIDER_AUTH_ERROR`, `MCP_PROVIDER_ERROR`, and `MCP_INPUT_VALIDATION_ERROR`. This helps Agent-visible tools avoid depending on provider-specific raw dict/string/error formats and gives Harness a reliable signal for observability, failure counts, and duplicate/limit controls.

## 4. Current Final 82-Case Metrics

From `rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker_alias_v2.json`:

| Metric | Value |
| --- | ---: |
| total_cases | 82 |
| accepted_count | 45 |
| total_rejected_count | 37 |
| top1_title_weak_hit_count / rate | 37 / 0.4512 |
| top2_title_weak_hit_count / rate | 38 / 0.4634 |
| expected_answer_false_rejected | 14 |
| expected_no_answer_correctly_rejected | 21 |
| expected_no_answer_not_rejected | 0 |
| reranker_success_count | 82 |
| reranker_failure_count | 0 |
| reranker_latency_avg_ms | 3385.0365853658536 |
| reranker_latency_p95_ms | 5928.0 |
| bm25_unique_added_total | 718 |
| source_id_missing_before_rerank_total | 0 |

## 5. Remaining Problems / Risks

- Generic answerable questions still have false rejections. Final report false rejected answerable count is `14`; listed possible false rejection cases include `case_003, case_012, case_021, case_053, case_055, case_056, case_057, case_058, case_059, case_060` and more.
- Confusing cases still need manual review; the final group metrics list confusing false rejected cases and manual-review cases.
- Alias Mapping is still incomplete; only low-risk high-confidence aliases were promoted. Medium-risk PowerPoint/PPT and 任务栏输入法图标/输入法图标 remain deferred.
- Threshold 0.20 improves F1 but introduces FP risk: FP 0 -> 2 versus 0.35 in threshold analysis.
- Reranker latency is non-trivial: final report avg `3385.0365853658536` ms, P95 `5928.0` ms.
- The current 82-case evaluation set is useful for direction but too small for final statistical confidence. It should be expanded to 150-200 cases.

## 6. Production / Gray Rollout Recommendation

Do not directly full-volume launch:

```text
BM25 experimental + Qwen Reranker + HSN Anchor + threshold 0.20
```

Recommended gray plan:

```text
clean-v1
BM25 experimental
SiliconFlow Reranker experimental
HSN Anchor
Alias enabled
Threshold 0.35 as safe default
Threshold 0.20 as small-traffic gray comparison
```

Production default should remain threshold 0.35 because it preserved precision at 1.0000 in the threshold report and avoided FP in the measured 82-case set. Threshold 0.20 should be evaluated on a small percentage of traffic with explicit no-answer false acceptance monitoring.

## 7. Pre-Launch Checklist

- API keys stay out of git and logs.
- Reranker timeout, retry, and fallback behavior defined before traffic rollout.
- Reranker cost and latency monitored, especially avg/P95.
- Manual audit for no-answer false acceptance.
- Manual audit for answerable false rejection.
- Logs and traces are scrubbed for API key, token, password, address, phone, and raw provider payload leakage.
- MCP contract tests pass.
- 82-case regression suite passes before each config change.
- Frontend displays refusal / low confidence / anchor gate reasons clearly.
- Gray rollout has rollback switch for Reranker, BM25, Anchor Gate, and threshold.

## 8. Lower-Priority Follow-Up Work

- Expand evaluation set to 150-200 cases.
- Manually review medium-risk aliases, especially PowerPoint/PPT and 任务栏输入法图标/输入法图标.
- Use MinerU/OCR only for a small set of problematic documents rather than full corpus rebuild.
- Consider LTR or learned hybrid weighting after more labeled data exists.
- Add production dashboards for accepted/rejected ratio, no-answer complaints, false rejection samples, and reranker latency.

## 9. Source Artifacts

| Artifact | Status |
| --- | --- |
| `backend/knowledge/config/query_aliases.yaml` | found |
| `backend/knowledge/testdata/alias_candidate_suggestions.md` | found |
| `backend/knowledge/testdata/rag_alias_mapping_v2_82_comparison.md` | found |
| `backend/knowledge/testdata/rag_cleaning_manifest.md` | found |
| `backend/knowledge/testdata/rag_clean_collection_comparison.md` | found |
| `backend/knowledge/testdata/rag_anchor_evidence_v2_hard_soft_negative_comparison.md` | found |
| `backend/knowledge/testdata/rag_anchor_evidence_v2_diagnosis.md` | found |
| `backend/knowledge/testdata/rag_bm25_clean_v1_manifest.md` | found |
| `backend/knowledge/testdata/rag_bm25_v2_82_comparison.md` | found |
| `backend/knowledge/testdata/rag_qwen_reranker_preflight.md` | found |
| `backend/knowledge/testdata/rag_siliconflow_reranker_v2_82_comparison.md` | found |
| `backend/knowledge/testdata/rag_threshold_analysis.md` | found |
| `backend/knowledge/testdata/rag_threshold_recommendation.md` | found |
| `backend/knowledge/testdata/rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker_alias_v2.md` | found |
| `backend/knowledge/testdata/rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker_alias_v2.json` | found |

## 10. Final Decision

The current best candidate for controlled gray rollout is:

```text
its-knowledge-clean-v1 + Query Normalization + Alias Mapping + Vector/Title/BM25 candidate recall + SiliconFlow Qwen3-Reranker-8B + HSN Anchor + MMR + threshold 0.35
```

Threshold 0.20 is worth a small gray comparison only, not a full production default. The project can move into code cleanup / pre-submit review after confirming operational safeguards around API keys, latency, fallback, logging, and manual audit sampling.
