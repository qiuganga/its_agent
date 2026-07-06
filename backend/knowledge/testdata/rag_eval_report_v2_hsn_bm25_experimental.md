# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-06T13:07:14`

## Settings

- Collection: its-knowledge-clean-v1
- CHUNK_SIZE: 3000
- CHUNK_OVERLAP: 200
- EMBEDDING_MODEL: Qwen/Qwen3-Embedding-8B
- VECTOR_DISTANCE_SPACE: cosine
- RAG_VECTOR_CANDIDATE_TOP_K: 15
- RAG_TITLE_CANDIDATE_TOP_K: 10
- RAG_FINAL_TOP_K: 2
- RAG_MIN_RERANK_SCORE: 0.35
- RAG_ANCHOR_EVIDENCE_MODE: hard-soft-negative
- RAG_BM25_MODE: experimental
- RAG_BM25_CANDIDATE_TOP_K: 10

## Summary

- Total cases: 24
- Normalization triggered: 8
- Normalization not triggered: 16
- Accepted with final docs: 21
- Low-confidence rejected: 0
- Top1 title weak hit: 8 (0.3333)
- Top2 title weak hit: 10 (0.4167)
- Expected no-answer correctly rejected: 0
- Expected no-answer anchor rejected: 3
- Expected no-answer not rejected: 0
- Expected-answer false rejected: 0
- Strong anchor cases: 21
- Hard anchor cases: 4
- Soft anchor cases: 11
- Negative anchor cases: 0
- No anchor cases: 10
- Hard evidence outside TopK: 0
- Negative anchor penalties: 0
- ANCHOR_EVIDENCE_MISSING: 3
- BM25 mode: experimental
- BM25 candidates: 320
- BM25 unique additions: 243
- BM25/vector overlap: 21 (0.0656)
- BM25/title overlap: 0 (0.0)
- Missing source_id before rerank: 0

## Group Metrics

- C_generic_answerable: total=8, top1=0, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=7
- A_anchor_answerable: total=10, top1=7, top2=7, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=3
- E_confusing: total=3, top1=1, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=1
- B_anchor_unanswerable: total=3, top1=0, top2=0, false_rejected=0, no_answer_rejected=3, no_answer_accepted=0, anchor_missing=3, manual_review=0

## A/B Comparison

- Positive: 0
- Neutral: 8
- Changed: 0
- Negative: 0

## Score Buckets

- >=0.50: 24

## Threshold Recommendation

- Recommendation: `keep_0.35_pending_manual_review`
- Possible false rejections: []
- Expected no-answer not rejected: []
- Passed but title weak miss: ['case_001', 'case_004', 'case_007', 'case_011', 'case_012', 'case_015', 'case_017', 'case_018', 'case_019', 'case_020', 'case_021']

## Suspicious Cases

- case_001: score=0.602014417810451, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6398319390632037, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_007: score=0.6757480292553618, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.5984403142788329, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012: score=0.5525611564456012, rejected=False, reason=['top2_title_weak_miss'], top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.602014417810451 | bm25=20 unique=15 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5418856671685435 | bm25=20 unique=13 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.5317792222381008 | bm25=20 unique=10 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6398319390632037 | bm25=10 unique=10 | top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.6141365615763263 | bm25=10 unique=9 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Windows 2000蓝屏死机故障分析与排除']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5708817034261632 | bm25=10 unique=8 | top_titles=['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6757480292553618 | bm25=20 unique=13 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6470393588052064 | bm25=10 unique=9 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.5791816013604253 | bm25=20 unique=10 | top_titles=['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5307124324756816 | bm25=20 unique=11 | top_titles=['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.5984403142788329 | bm25=20 unique=10 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.5525611564456012 | bm25=20 unique=12 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.608670883406653 | bm25=10 unique=8 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6269816268504407 | bm25=10 unique=9 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.622751950806534 | bm25=10 unique=9 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5668078741846164 | bm25=10 unique=9 | top_titles=['Outlook为何没有已发送邮件的记录-', '彩色喷墨多功能一体机M920校准墨盒的操作']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5717720657854188 | bm25=10 unique=10 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.8239809967475114 | bm25=10 unique=10 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用导航光盘安装操作系统时提示CD-KEY序列号从何处查找-']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.6346188366220523 | bm25=10 unique=9 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '两台电脑如何共享访问']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.610711747446053 | bm25=10 unique=10 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5735363559879451 | bm25=10 unique=9 | top_titles=['Windows XP 关机故障', '智能电视开不了机并且指示灯都不亮怎么办？']
- case_022 | dual=False | rejected=False | anchor_rejected=True | score=0.6248821369412623 | bm25=10 unique=10 | top_titles=[]
- case_023 | dual=False | rejected=False | anchor_rejected=True | score=0.5226976597901252 | bm25=10 unique=10 | top_titles=[]
- case_024 | dual=False | rejected=False | anchor_rejected=True | score=0.7023231102412939 | bm25=10 unique=10 | top_titles=[]

> Title weak hit is an automatic weak label, not final business accuracy.