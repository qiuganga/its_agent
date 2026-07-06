# Qwen Reranker Preflight

- Generated at: `2026-07-06T15:45:07`
- Provider: `SiliconFlow`
- Base URL: `https://api.siliconflow.cn/v1`
- Endpoint: `POST /rerank`
- SILICONFLOW_API_KEY configured: `True`
- RAG_RERANKER_MODEL configured: `True`
- Model: `Qwen/Qwen3-Reranker-8B`
- HTTP status: `200`
- Schema valid: `True`
- Ranking valid: `True`
- Passed: `True`

## Probe

- Query: `蓝屏 0x0000007B 怎么处理`
- Documents: `blue_screen`, `wallpaper`

## Results

```json
[
  {
    "index": 0,
    "relevance_score": 0.9962132573127747,
    "rank": 1,
    "document_label": "blue_screen"
  },
  {
    "index": 1,
    "relevance_score": 2.8715128337353235e-06,
    "rank": 2,
    "document_label": "wallpaper"
  }
]
```

## Decision

Preflight passed. The 82-case reranker experiment can run.