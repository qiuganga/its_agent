# BM25 Evaluation Scope Correction

## Background

The following report files were generated with names that include `v2`, but their actual `total_cases` value is `24`:

- `rag_eval_report_v2_hsn_bm25_baseline.json`
- `rag_eval_report_v2_hsn_bm25_experimental.json`
- `rag_bm25_v2_comparison.json`

These files used the default evaluation file:

- `rag_eval_cases.json`

That default file contains 24 cases.

## Scope

The old reports can only be used as local observations for the 24-case evaluation set.

They must not be treated as the BM25 A/B conclusion for the 82-case v2 evaluation set.

## Correct 82-Case Reports

The corrected 82-case BM25 A/B evaluation uses the explicit v2 case file:

- `rag_eval_cases_v2.json`

The corrected output files use independent names:

- `rag_eval_report_v2_82_hsn_bm25_baseline.json`
- `rag_eval_report_v2_82_hsn_bm25_baseline.md`
- `rag_eval_report_v2_82_hsn_bm25_experimental.json`
- `rag_eval_report_v2_82_hsn_bm25_experimental.md`
- `rag_bm25_v2_82_comparison.json`
- `rag_bm25_v2_82_comparison.md`

The comparison script now validates that both reports are comparable before generating the 82-case A/B conclusion.
