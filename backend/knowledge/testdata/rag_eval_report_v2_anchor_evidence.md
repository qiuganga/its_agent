# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-05T19:46:38`

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

- Total cases: 82
- Normalization triggered: 19
- Normalization not triggered: 63
- Accepted with final docs: 65
- Low-confidence rejected: 1
- Top1 title weak hit: 13 (0.1585)
- Top2 title weak hit: 17 (0.2073)
- Expected no-answer correctly rejected: 0
- Expected no-answer anchor rejected: 7
- Expected no-answer not rejected: 16
- Expected-answer false rejected: 10
- Strong anchor cases: 39
- ANCHOR_EVIDENCE_MISSING: 16

## Group Metrics

- C_generic_answerable: total=20, top1=1, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=18
- E_confusing: total=15, top1=3, top2=4, false_rejected=4, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=4, manual_review=11
- A_anchor_answerable: total=24, top1=9, top2=11, false_rejected=6, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=5, manual_review=13
- B_anchor_unanswerable: total=15, top1=0, top2=0, false_rejected=0, no_answer_rejected=7, no_answer_accepted=8, anchor_missing=7, manual_review=8
- D_generic_unanswerable: total=8, top1=0, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0, manual_review=8

## A/B Comparison

- Positive: 0
- Neutral: 18
- Changed: 1
- Negative: 0

## Score Buckets

- >=0.50: 63
- <0.25: 1
- 0.35-0.50: 18

## Threshold Recommendation

- Recommendation: `keep_0.35_pending_manual_review`
- Possible false rejections: ['case_025', 'case_026', 'case_027', 'case_030', 'case_039', 'case_040', 'case_071', 'case_072', 'case_074', 'case_080']
- Expected no-answer not rejected: ['case_041', 'case_042', 'case_043', 'case_046', 'case_047', 'case_048', 'case_051', 'case_052', 'case_061', 'case_062', 'case_063', 'case_064', 'case_065', 'case_066', 'case_067', 'case_068']
- Passed but title weak miss: ['case_001', 'case_004', 'case_007', 'case_011', 'case_012', 'case_017', 'case_018', 'case_019', 'case_020', 'case_021', 'case_029', 'case_031', 'case_033', 'case_034', 'case_037', 'case_038', 'case_053', 'case_054', 'case_055', 'case_056', 'case_057', 'case_058', 'case_059', 'case_060', 'case_069', 'case_070', 'case_075', 'case_077', 'case_078', 'case_079', 'case_081', 'case_082']

## Suspicious Cases

- case_001: score=0.6010714103277515, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6405410011498778, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_007: score=0.6734221891745371, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.5961907212693416, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012: score=0.5532813623280735, rejected=False, reason=['top2_title_weak_miss'], top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.6010714103277515 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5418942996633378 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.5319039043907631 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6405410011498778 | top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.6129120461236077 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5540881137202314 | top_titles=['在Windows 7下如何配置无线网络', '联想手机A789如何连接无线网络上网']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6734221891745371 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6470897716682211 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.5798051182339028 | top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5298705776660186 | top_titles=['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.5961907212693416 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.5532813623280735 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.6101062713091114 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6279600568445349 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Excel表导入 Access 2010 后时间显示错误怎么办-']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.5988207047308607 | top_titles=['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5651323635204152 | top_titles=['Outlook为何没有已发送邮件的记录-', '将Outlook设为Mac默认程序后为何仍弹出Apple Mail？']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5688556858433309 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.8251646546285031 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用导航光盘安装操作系统时提示CD-KEY序列号从何处查找-']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.6334603191382513 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '两台电脑如何共享访问']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.610711747446053 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5982278931413747 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '联想V858-V658手机如何使用语音短信功能？']
- case_022 | dual=False | rejected=False | anchor_rejected=True | score=0.6248707379315541 | top_titles=[]
- case_023 | dual=False | rejected=False | anchor_rejected=True | score=0.5231294566538982 | top_titles=[]
- case_024 | dual=False | rejected=False | anchor_rejected=True | score=0.7031034160075843 | top_titles=[]
- case_025 | dual=False | rejected=True | anchor_rejected=False | score=0.2301961425105425 | top_titles=[]
- case_026 | dual=False | rejected=False | anchor_rejected=True | score=0.552343374599052 | top_titles=[]
- case_027 | dual=False | rejected=False | anchor_rejected=True | score=0.6757273542407465 | top_titles=[]
- case_028 | dual=False | rejected=False | anchor_rejected=False | score=0.45621040096358406 | top_titles=['Outlook为何没有已发送邮件的记录-', '将Outlook设为Mac默认程序后为何仍弹出Apple Mail？']
- case_029 | dual=False | rejected=False | anchor_rejected=False | score=0.6688060328980053 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_030 | dual=False | rejected=False | anchor_rejected=True | score=0.76748572046308 | top_titles=[]
- case_031 | dual=False | rejected=False | anchor_rejected=False | score=0.7172886097907042 | top_titles=['联想支持Windows 10系统升级的机型列表', '没有并口的笔记本如何接加密狗等并口设备？']
- case_032 | dual=False | rejected=False | anchor_rejected=False | score=0.43101895426792847 | top_titles=['Lenovo G485无线网络连接不上的解决方案', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”']
- case_033 | dual=False | rejected=False | anchor_rejected=False | score=0.4316453795557751 | top_titles=['关于系统提示登录进程初始化失败问题的解决方案', '常用的文件名后缀（扩展名）汇总']
- case_034 | dual=False | rejected=False | anchor_rejected=False | score=0.6993811451994599 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_035 | dual=False | rejected=False | anchor_rejected=False | score=0.5994274464897543 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_036 | dual=False | rejected=False | anchor_rejected=False | score=0.573405029887053 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Lenovo G485 USB3.0驱动程序安装不上的解决方法']
- case_037 | dual=False | rejected=False | anchor_rejected=False | score=0.6770984861018428 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '联想支持Windows 10系统升级的机型列表']
- case_038 | dual=False | rejected=False | anchor_rejected=False | score=0.6616932649942713 | top_titles=['Windows 2000蓝屏死机故障分析与排除（2）', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_039 | dual=False | rejected=False | anchor_rejected=True | score=0.48851626410048055 | top_titles=[]
- case_040 | dual=False | rejected=False | anchor_rejected=True | score=0.5775120548614656 | top_titles=[]
- case_041 | dual=False | rejected=False | anchor_rejected=False | score=0.7476476398625144 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_042 | dual=False | rejected=False | anchor_rejected=False | score=0.4624600260215982 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '联想ET360摄像头用户使用手册']
- case_043 | dual=False | rejected=False | anchor_rejected=False | score=0.588942178114295 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_044 | dual=False | rejected=False | anchor_rejected=True | score=0.3527098926613048 | top_titles=[]
- case_045 | dual=False | rejected=False | anchor_rejected=True | score=0.5592959189717521 | top_titles=[]
- case_046 | dual=False | rejected=False | anchor_rejected=False | score=0.45523686089931187 | top_titles=['万全R510 5B20 第一章 产品简介', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_047 | dual=False | rejected=False | anchor_rejected=False | score=0.5626694949818749 | top_titles=['万全T220&#38;amp;#38;270 G5系统用户手册', '彩色喷墨多功能一体机M920用户使用手册']
- case_048 | dual=False | rejected=False | anchor_rejected=False | score=0.47958122541070003 | top_titles=['如何使用鲁大师跑分？', '如何关闭网卡的电源管理选项']
- case_049 | dual=False | rejected=False | anchor_rejected=True | score=0.6791757861879872 | top_titles=[]
- case_050 | dual=False | rejected=False | anchor_rejected=True | score=0.37239819882434694 | top_titles=[]
- case_051 | dual=False | rejected=False | anchor_rejected=False | score=0.5959733580638135 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在任务栏显示或隐藏电池图标']
- case_052 | dual=False | rejected=False | anchor_rejected=False | score=0.45843877542078065 | top_titles=['联想手机A820t备份联系人与短信的方法', '彩色喷墨多功能一体机M920用户使用手册']
- case_053 | dual=False | rejected=False | anchor_rejected=False | score=0.49887846300380606 | top_titles=['联想智能电视可以像电脑一样观看网页么？能看网页中的视频么？', '万全T200 2020 第五章 常用操作系统安装指南']
- case_054 | dual=False | rejected=False | anchor_rejected=False | score=0.6537342953123007 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '启天IV代保护卡多媒体教程']
- case_055 | dual=False | rejected=False | anchor_rejected=False | score=0.4990195925214947 | top_titles=['万全T200 2020 第五章 常用操作系统安装指南', '联想硬盘保护EDU7.X的安装方法']
- case_056 | dual=False | rejected=False | anchor_rejected=False | score=0.5114897032007946 | top_titles=['暴风影音的DLNA功能怎么用', '31018765A 扬天T系列用户手册 V1.0']
- case_057 | dual=False | rejected=False | anchor_rejected=False | score=0.5150626878428554 | top_titles=['票据打印机DP600、DP8000用户手册', 'Lenovo Miix3-830使用说明书']
- case_058 | dual=False | rejected=False | anchor_rejected=False | score=0.4620238567017538 | top_titles=['WPS Office中如何打印稿纸', 'Windows 2000蓝屏死机故障分析与排除（2）']
- case_059 | dual=False | rejected=False | anchor_rejected=False | score=0.6902150739253878 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_060 | dual=False | rejected=False | anchor_rejected=False | score=0.641516110522186 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在任务栏显示或隐藏电池图标']
- case_061 | dual=False | rejected=False | anchor_rejected=False | score=0.5998376390864854 | top_titles=['TR280 G3-TR350 G7 如何查看和清除主板BMC的 SEL日志？', '没有并口的笔记本如何接加密狗等并口设备？']
- case_062 | dual=False | rejected=False | anchor_rejected=False | score=0.44431190304878787 | top_titles=['联想ET360摄像头应用程序帮助文档', 'LJ1700用户使用手册']
- case_063 | dual=False | rejected=False | anchor_rejected=False | score=0.44873763454450677 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_064 | dual=False | rejected=False | anchor_rejected=False | score=0.5712974129414239 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'WinXP从待机状态唤醒后网络连接断开']
- case_065 | dual=False | rejected=False | anchor_rejected=False | score=0.5693083245289445 | top_titles=['31018765A 扬天T系列用户手册 V1.0', '如何备份幸福之家4.X中的日记']
- case_066 | dual=False | rejected=False | anchor_rejected=False | score=0.4020377173367578 | top_titles=['Intel SE7501HG2 服务器主板的故障代码。', '联想手机A820t备份联系人与短信的方法']
- case_067 | dual=False | rejected=False | anchor_rejected=False | score=0.4629541357810158 | top_titles=['启天IV代保护卡多媒体教程', '笔记本双显卡如何切换']
- case_068 | dual=False | rejected=False | anchor_rejected=False | score=0.5460868718156373 | top_titles=['宽带连接频繁掉线', '外接VGA设备后笔记本LCD没有显示而VGA显示正常']
- case_069 | dual=True | rejected=False | anchor_rejected=False | score=0.6584261285983796 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Windows 7下如何实现共享上网']
- case_070 | dual=True | rejected=False | anchor_rejected=False | score=0.6543298062842458 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Windows 7下如何实现共享上网']
- case_071 | dual=True | rejected=False | anchor_rejected=True | score=0.5390850068057687 | top_titles=[]
- case_072 | dual=True | rejected=False | anchor_rejected=True | score=0.7153017589873147 | top_titles=[]
- case_073 | dual=True | rejected=False | anchor_rejected=False | score=0.5634665754755239 | top_titles=['Excel如何冻结首行首列 多行多列', 'Internet Explorer版本升级说明']
- case_074 | dual=True | rejected=False | anchor_rejected=True | score=0.6381895402389421 | top_titles=[]
- case_075 | dual=True | rejected=False | anchor_rejected=False | score=0.6478040582090405 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_076 | dual=True | rejected=False | anchor_rejected=False | score=0.4316128379056984 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_077 | dual=False | rejected=False | anchor_rejected=False | score=0.6394732878554963 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_078 | dual=True | rejected=False | anchor_rejected=False | score=0.5756077654520515 | top_titles=['联想支持Windows 10系统升级的机型列表', '没有并口的笔记本如何接加密狗等并口设备？']
- case_079 | dual=True | rejected=False | anchor_rejected=False | score=0.6390346226467817 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '31018765A 扬天T系列用户手册 V1.0']
- case_080 | dual=True | rejected=False | anchor_rejected=True | score=0.5479517181791456 | top_titles=[]
- case_081 | dual=False | rejected=False | anchor_rejected=False | score=0.7192699230338713 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_082 | dual=False | rejected=False | anchor_rejected=False | score=0.5239909586149151 | top_titles=['Windows Storage Server 2003用户手册v1.0', '安装最新的 Windows 8.1 Update']

> Title weak hit is an automatic weak label, not final business accuracy.