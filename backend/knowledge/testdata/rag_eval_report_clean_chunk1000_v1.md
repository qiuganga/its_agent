# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-05T00:24:03`

## Settings

- Collection: its-knowledge-clean-chunk1000-v1
- CHUNK_SIZE: 3000
- CHUNK_OVERLAP: 200
- EMBEDDING_MODEL: Qwen/Qwen3-Embedding-8B
- VECTOR_DISTANCE_SPACE: cosine
- RAG_VECTOR_CANDIDATE_TOP_K: 15
- RAG_TITLE_CANDIDATE_TOP_K: 10
- RAG_FINAL_TOP_K: 2
- RAG_MIN_RERANK_SCORE: 0.35

## Summary

- Total cases: 24
- Normalization triggered: 8
- Normalization not triggered: 16
- Accepted with final docs: 24
- Low-confidence rejected: 0
- Top1 title weak hit: 4 (0.1667)
- Top2 title weak hit: 6 (0.25)
- Expected no-answer correctly rejected: 0
- Expected no-answer not rejected: 3
- Expected-answer false rejected: 0

## A/B Comparison

- Positive: 0
- Neutral: 7
- Changed: 0
- Negative: 1

## Score Buckets

- >=0.50: 24

## Threshold Recommendation

- Recommendation: `consider_raising_to_0.40`
- Possible false rejections: []
- Expected no-answer not rejected: ['case_022', 'case_023', 'case_024']
- Passed but title weak miss: ['case_001', 'case_002', 'case_003', 'case_004', 'case_006', 'case_007', 'case_008', 'case_011', 'case_012', 'case_015', 'case_017', 'case_018', 'case_019', 'case_020', 'case_021']

## Suspicious Cases

- case_001: score=0.6563383328111727, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Windows XP 关机故障']
- case_002: score=0.6053414805643793, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想支持Windows 10系统升级的机型列表']
- case_003: score=0.5351204301667424, rejected=False, reason=['top2_title_weak_miss', 'dual_retrieval_possible_negative'], top_titles=['宽带连接频繁掉线', 'Excel文件菜单及相关功能灰色不可用怎么办？']
- case_004: score=0.6398319390632037, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'Excel文件菜单及相关功能灰色不可用怎么办？']
- case_006: score=0.6343395195709776, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？']

## Case Details

- case_001 | dual=True | rejected=False | score=0.6563383328111727 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Windows XP 关机故障']
- case_002 | dual=True | rejected=False | score=0.6053414805643793 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想支持Windows 10系统升级的机型列表']
- case_003 | dual=True | rejected=False | score=0.5351204301667424 | top_titles=['宽带连接频繁掉线', 'Excel文件菜单及相关功能灰色不可用怎么办？']
- case_004 | dual=False | rejected=False | score=0.6398319390632037 | top_titles=['Windows XP 关机故障', 'Excel文件菜单及相关功能灰色不可用怎么办？']
- case_005 | dual=False | rejected=False | score=0.6371012340684956 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_006 | dual=False | rejected=False | score=0.6343395195709776 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？']
- case_007 | dual=True | rejected=False | score=0.6753417730088334 | top_titles=['Windows XP 关机故障', 'Excel文件菜单及相关功能灰色不可用怎么办？']
- case_008 | dual=False | rejected=False | score=0.6471269899143023 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Excel文件菜单及相关功能灰色不可用怎么办？']
- case_009 | dual=True | rejected=False | score=0.5756142981738701 | top_titles=['如何添加启用蓝牙的设备', 'Excel文件菜单及相关功能灰色不可用怎么办？']
- case_010 | dual=True | rejected=False | score=0.5312089507043656 | top_titles=['如何添加启用蓝牙的设备', '如何备份幸福之家4.X中的日记']
- case_011 | dual=True | rejected=False | score=0.5950282509558078 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | score=0.5824659911185619 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”']
- case_013 | dual=False | rejected=False | score=0.6369384517428107 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '新圆梦F系列电脑运行游戏卡']
- case_014 | dual=False | rejected=False | score=0.7025039970698292 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_015 | dual=False | rejected=False | score=0.6624465902741279 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_016 | dual=False | rejected=False | score=0.565492461976571 | top_titles=['Outlook为何没有已发送邮件的记录-', '彩色喷墨多功能一体机M920校准墨盒的操作']
- case_017 | dual=False | rejected=False | score=0.5872409414406407 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？']
- case_018 | dual=False | rejected=False | score=0.8268134132940277 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）']
- case_019 | dual=False | rejected=False | score=0.6423213492399225 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '视频指导：IE10浏览器如何显示快速导航界面']
- case_020 | dual=False | rejected=False | score=0.6093757128876189 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | score=0.6342897701562792 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想台式机模式转换功能介绍']
- case_022 | dual=False | rejected=False | score=0.6241570894314977 | top_titles=['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- case_023 | dual=False | rejected=False | score=0.5912533848365349 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '改善手机或平板机身发热的办法']
- case_024 | dual=False | rejected=False | score=0.7042312876087977 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'SecureBoot未正确配置']

> Title weak hit is an automatic weak label, not final business accuracy.