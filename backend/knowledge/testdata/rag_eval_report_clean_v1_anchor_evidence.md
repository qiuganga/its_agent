# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-05T15:57:50`

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
- RAG_ANCHOR_EVIDENCE_MODE: experimental

## Summary

- Total cases: 24
- Normalization triggered: 8
- Normalization not triggered: 16
- Accepted with final docs: 21
- Low-confidence rejected: 0
- Top1 title weak hit: 9 (0.375)
- Top2 title weak hit: 11 (0.4583)
- Expected no-answer correctly rejected: 0
- Expected no-answer anchor rejected: 3
- Expected no-answer not rejected: 0
- Expected-answer false rejected: 0
- Strong anchor cases: 11
- ANCHOR_EVIDENCE_MISSING: 3

## A/B Comparison

- Positive: 0
- Neutral: 7
- Changed: 1
- Negative: 0

## Score Buckets

- >=0.50: 24

## Threshold Recommendation

- Recommendation: `keep_0.35_pending_manual_review`
- Possible false rejections: []
- Expected no-answer not rejected: []
- Passed but title weak miss: ['case_001', 'case_004', 'case_007', 'case_011', 'case_012', 'case_017', 'case_018', 'case_019', 'case_020', 'case_021']

## Suspicious Cases

- case_001: score=0.5988386462917739, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6395515220813949, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_007: score=0.6751524121935604, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.5969357222656353, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012: score=0.5523975784676328, rejected=False, reason=['top2_title_weak_miss'], top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.5988386462917739 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5391750934721173 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.53221143390196 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6395515220813949 | top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.6133300324409076 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5537360675001923 | top_titles=['在Windows 7下如何配置无线网络', '联想手机A789如何连接无线网络上网']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6751524121935604 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6464543786940902 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.577574535638185 | top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5307616001953248 | top_titles=['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.5969357222656353 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.5523975784676328 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.6078380614558603 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6265706662738548 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Excel表导入 Access 2010 后时间显示错误怎么办-']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.5998925110912356 | top_titles=['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5680568626982915 | top_titles=['Outlook为何没有已发送邮件的记录-', '将Outlook设为Mac默认程序后为何仍弹出Apple Mail？']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5721589250812719 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.825057241001603 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用导航光盘安装操作系统时提示CD-KEY序列号从何处查找-']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.6340806446022158 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '两台电脑如何共享访问']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.610711747446053 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5979516077584652 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '联想V858-V658手机如何使用语音短信功能？']
- case_022 | dual=False | rejected=False | anchor_rejected=True | score=0.6248707379315541 | top_titles=[]
- case_023 | dual=False | rejected=False | anchor_rejected=True | score=0.5216628282865722 | top_titles=[]
- case_024 | dual=False | rejected=False | anchor_rejected=True | score=0.7042312876087977 | top_titles=[]

> Title weak hit is an automatic weak label, not final business accuracy.