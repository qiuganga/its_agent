# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-05T15:48:14`

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
- RAG_ANCHOR_EVIDENCE_MODE: off

## Summary

- Total cases: 24
- Normalization triggered: 8
- Normalization not triggered: 16
- Accepted with final docs: 24
- Low-confidence rejected: 0
- Top1 title weak hit: 7 (0.2917)
- Top2 title weak hit: 10 (0.4167)
- Expected no-answer correctly rejected: 0
- Expected no-answer anchor rejected: 0
- Expected no-answer not rejected: 3
- Expected-answer false rejected: 0
- Strong anchor cases: 0
- ANCHOR_EVIDENCE_MISSING: 0

## A/B Comparison

- Positive: 0
- Neutral: 8
- Changed: 0
- Negative: 0

## Score Buckets

- >=0.50: 24

## Threshold Recommendation

- Recommendation: `consider_raising_to_0.40`
- Possible false rejections: []
- Expected no-answer not rejected: ['case_022', 'case_023', 'case_024']
- Passed but title weak miss: ['case_001', 'case_004', 'case_006', 'case_007', 'case_011', 'case_012', 'case_015', 'case_017', 'case_018', 'case_020', 'case_021']

## Suspicious Cases

- case_001: score=0.6014237292392017, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6398713576854296, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_006: score=0.5815833111323668, rejected=False, reason=['top2_title_weak_miss'], top_titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_007: score=0.6757480292553618, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.5963855354023719, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.6014237292392017 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5413101032781463 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.5321642180818598 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6398713576854296 | top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.614588728835987 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5815833111323668 | top_titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6757480292553618 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6460229698479021 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.5768177504998382 | top_titles=['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5298705776660186 | top_titles=['如何添加启用蓝牙的设备', '如何备份幸福之家4.X中的日记']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.5963855354023719 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.550884899206314 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.6101062713091114 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6271280799224179 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.6223052100195168 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5670175690866464 | top_titles=['Outlook为何没有已发送邮件的记录-', '彩色喷墨多功能一体机M920校准墨盒的操作']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5728822796271322 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.8245542570184057 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.6344706527350856 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.6097650799951573 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5961266483074488 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '联想V858-V658手机如何使用语音短信功能？']
- case_022 | dual=False | rejected=False | anchor_rejected=False | score=0.626027680661962 | top_titles=['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- case_023 | dual=False | rejected=False | anchor_rejected=False | score=0.5226976597901252 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_024 | dual=False | rejected=False | anchor_rejected=False | score=0.700076821946277 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']

> Title weak hit is an automatic weak label, not final business accuracy.