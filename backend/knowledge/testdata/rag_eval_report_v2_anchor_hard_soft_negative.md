# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-05T23:40:31`

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

## Summary

- Total cases: 82
- Normalization triggered: 19
- Normalization not triggered: 63
- Accepted with final docs: 68
- Low-confidence rejected: 2
- Top1 title weak hit: 10 (0.122)
- Top2 title weak hit: 15 (0.1829)
- Expected no-answer correctly rejected: 1
- Expected no-answer anchor rejected: 9
- Expected no-answer not rejected: 13
- Expected-answer false rejected: 4
- Strong anchor cases: 60
- Hard anchor cases: 18
- Soft anchor cases: 39
- Negative anchor cases: 5
- No anchor cases: 33
- Hard evidence outside TopK: 0
- Negative anchor penalties: 0
- ANCHOR_EVIDENCE_MISSING: 12

## Group Metrics

- C_generic_answerable: total=18, top1=0, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=17
- A_anchor_answerable: total=26, top1=8, top2=10, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=16
- E_confusing: total=15, top1=2, top2=4, false_rejected=3, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=3, manual_review=11
- B_anchor_unanswerable: total=15, top1=0, top2=0, false_rejected=0, no_answer_rejected=10, no_answer_accepted=5, anchor_missing=9, manual_review=5
- D_generic_unanswerable: total=8, top1=0, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0, manual_review=8

## A/B Comparison

- Positive: 0
- Neutral: 18
- Changed: 1
- Negative: 0

## Score Buckets

- >=0.50: 64
- <0.25: 1
- 0.35-0.50: 16
- 0.25-0.35: 1

## Threshold Recommendation

- Recommendation: `keep_0.35_pending_manual_review`
- Possible false rejections: ['case_025', 'case_069', 'case_070', 'case_080']
- Expected no-answer not rejected: ['case_042', 'case_043', 'case_047', 'case_048', 'case_052', 'case_061', 'case_062', 'case_063', 'case_064', 'case_065', 'case_066', 'case_067', 'case_068']
- Passed but title weak miss: ['case_001', 'case_004', 'case_007', 'case_011', 'case_012', 'case_015', 'case_017', 'case_018', 'case_019', 'case_020', 'case_021', 'case_026', 'case_027', 'case_028', 'case_029', 'case_030', 'case_031', 'case_033', 'case_034', 'case_037', 'case_038', 'case_039', 'case_040', 'case_053', 'case_054', 'case_055', 'case_056', 'case_057', 'case_058', 'case_059', 'case_060', 'case_071', 'case_072', 'case_073', 'case_074', 'case_075', 'case_077', 'case_079', 'case_081', 'case_082']

## Suspicious Cases

- case_001: score=0.6014237292392017, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6411872647317421, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_007: score=0.6746786809867049, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.59516816148101, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012: score=0.5523975784676328, rejected=False, reason=['top2_title_weak_miss'], top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.6014237292392017 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5394869763044614 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.5343379296104815 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6411872647317421 | top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.6129120461236077 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5710641717703838 | top_titles=['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6746786809867049 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6464543786940902 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.5756142981738701 | top_titles=['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5297932824077565 | top_titles=['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.59516816148101 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.5523975784676328 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.6101062713091114 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6276468722254123 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.6223229357658677 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5658026581665079 | top_titles=['Outlook为何没有已发送邮件的记录-', '彩色喷墨多功能一体机M920校准墨盒的操作']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5726598322978704 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.8245542570184057 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用导航光盘安装操作系统时提示CD-KEY序列号从何处查找-']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.6329922684781633 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '两台电脑如何共享访问']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.6062547705367336 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5765205821763761 | top_titles=['Windows XP 关机故障', '智能电视开不了机并且指示灯都不亮怎么办？']
- case_022 | dual=False | rejected=False | anchor_rejected=True | score=0.6247332738634324 | top_titles=[]
- case_023 | dual=False | rejected=False | anchor_rejected=True | score=0.5233667564190059 | top_titles=[]
- case_024 | dual=False | rejected=False | anchor_rejected=True | score=0.7031153753864848 | top_titles=[]
- case_025 | dual=False | rejected=True | anchor_rejected=False | score=0.2301961425105425 | top_titles=[]
- case_026 | dual=False | rejected=False | anchor_rejected=False | score=0.5524631159808335 | top_titles=['Windows 8.1 Update （KB2919355）常见问题', '联想手机如何在桌面上添加文件夹']
- case_027 | dual=False | rejected=False | anchor_rejected=False | score=0.6710121674243055 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '万全T168板载SATA RAID系统设置']
- case_028 | dual=False | rejected=False | anchor_rejected=False | score=0.4929329164670159 | top_titles=['万全T110 1510如何清除主板CMOS-', '万全3200C 系统用户手册']
- case_029 | dual=False | rejected=False | anchor_rejected=False | score=0.6699685616277585 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_030 | dual=False | rejected=False | anchor_rejected=False | score=0.7677791548079005 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_031 | dual=False | rejected=False | anchor_rejected=False | score=0.7173179559653438 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_032 | dual=False | rejected=False | anchor_rejected=False | score=0.43116274502981433 | top_titles=['Lenovo G485无线网络连接不上的解决方案', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”']
- case_033 | dual=False | rejected=False | anchor_rejected=False | score=0.43384642180450916 | top_titles=['关于系统提示登录进程初始化失败问题的解决方案', '常用的文件名后缀（扩展名）汇总']
- case_034 | dual=False | rejected=False | anchor_rejected=False | score=0.6994564207569423 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_035 | dual=False | rejected=False | anchor_rejected=False | score=0.5969407297566844 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_036 | dual=False | rejected=False | anchor_rejected=False | score=0.5707551498298329 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Lenovo G485 USB3.0驱动程序安装不上的解决方法']
- case_037 | dual=False | rejected=False | anchor_rejected=False | score=0.7305236802258677 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_038 | dual=False | rejected=False | anchor_rejected=False | score=0.6616932649942713 | top_titles=['Windows 2000蓝屏死机故障分析与排除（2）', '彩色喷墨多功能一体机M920用户使用手册']
- case_039 | dual=False | rejected=False | anchor_rejected=False | score=0.48608036880015054 | top_titles=['DP300如何恢复到出厂缺省设置？', '屏幕保护功能介绍以及不同系统下如何设置或取消屏幕保护（屏保）功能']
- case_040 | dual=False | rejected=False | anchor_rejected=False | score=0.5743453947748446 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', 'Intel SE7501HG2 服务器主板的故障代码。']
- case_041 | dual=False | rejected=False | anchor_rejected=True | score=0.7466859159296884 | top_titles=[]
- case_042 | dual=False | rejected=False | anchor_rejected=False | score=0.46206445889849657 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '联想ET360摄像头用户使用手册']
- case_043 | dual=False | rejected=False | anchor_rejected=False | score=0.5850820062323496 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_044 | dual=False | rejected=True | anchor_rejected=False | score=0.34451030129107907 | top_titles=[]
- case_045 | dual=False | rejected=False | anchor_rejected=True | score=0.5595323894839173 | top_titles=[]
- case_046 | dual=False | rejected=False | anchor_rejected=True | score=0.4549249890909363 | top_titles=[]
- case_047 | dual=False | rejected=False | anchor_rejected=False | score=0.5631144284260237 | top_titles=['万全T220&#38;amp;#38;270 G5系统用户手册', '彩色喷墨多功能一体机M920用户使用手册']
- case_048 | dual=False | rejected=False | anchor_rejected=False | score=0.4798791695921723 | top_titles=['如何使用鲁大师跑分？', '如何关闭网卡的电源管理选项']
- case_049 | dual=False | rejected=False | anchor_rejected=True | score=0.677997083812192 | top_titles=[]
- case_050 | dual=False | rejected=False | anchor_rejected=True | score=0.37280015303409686 | top_titles=[]
- case_051 | dual=False | rejected=False | anchor_rejected=True | score=0.5940633676301664 | top_titles=[]
- case_052 | dual=False | rejected=False | anchor_rejected=False | score=0.4584883115299476 | top_titles=['联想手机A820t备份联系人与短信的方法', '彩色喷墨多功能一体机M920用户使用手册']
- case_053 | dual=False | rejected=False | anchor_rejected=False | score=0.49867030388447503 | top_titles=['联想智能电视可以像电脑一样观看网页么？能看网页中的视频么？', '万全T200 2020 第五章 常用操作系统安装指南']
- case_054 | dual=False | rejected=False | anchor_rejected=False | score=0.6527746923424022 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '启天IV代保护卡多媒体教程']
- case_055 | dual=False | rejected=False | anchor_rejected=False | score=0.5003536712119137 | top_titles=['万全T200 2020 第五章 常用操作系统安装指南', '联想硬盘保护EDU7.X的安装方法']
- case_056 | dual=False | rejected=False | anchor_rejected=False | score=0.5115512648706189 | top_titles=['暴风影音的DLNA功能怎么用', '31018765A 扬天T系列用户手册 V1.0']
- case_057 | dual=False | rejected=False | anchor_rejected=False | score=0.514726528339156 | top_titles=['票据打印机DP600、DP8000用户手册', 'Lenovo Miix3-830使用说明书']
- case_058 | dual=False | rejected=False | anchor_rejected=False | score=0.46274648470945806 | top_titles=['WPS Office中如何打印稿纸', 'Windows 2000蓝屏死机故障分析与排除（2）']
- case_059 | dual=False | rejected=False | anchor_rejected=False | score=0.6881507389728521 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_060 | dual=False | rejected=False | anchor_rejected=False | score=0.6415502335725402 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在任务栏显示或隐藏电池图标']
- case_061 | dual=False | rejected=False | anchor_rejected=False | score=0.5987101041885762 | top_titles=['TR280 G3-TR350 G7 如何查看和清除主板BMC的 SEL日志？', '没有并口的笔记本如何接加密狗等并口设备？']
- case_062 | dual=False | rejected=False | anchor_rejected=False | score=0.4457255231451075 | top_titles=['联想ET360摄像头应用程序帮助文档', 'U160产品图示及功能键说明']
- case_063 | dual=False | rejected=False | anchor_rejected=False | score=0.44981614854447993 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）']
- case_064 | dual=False | rejected=False | anchor_rejected=False | score=0.5805283003140687 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'WinXP从待机状态唤醒后网络连接断开']
- case_065 | dual=False | rejected=False | anchor_rejected=False | score=0.5695910098526595 | top_titles=['31018765A 扬天T系列用户手册 V1.0', '如何备份幸福之家4.X中的日记']
- case_066 | dual=False | rejected=False | anchor_rejected=False | score=0.39857768530943094 | top_titles=['Intel SE7501HG2 服务器主板的故障代码。', '联想手机A820t备份联系人与短信的方法']
- case_067 | dual=False | rejected=False | anchor_rejected=False | score=0.463779023310132 | top_titles=['启天IV代保护卡多媒体教程', '笔记本双显卡如何切换']
- case_068 | dual=False | rejected=False | anchor_rejected=False | score=0.5463167350552038 | top_titles=['宽带连接频繁掉线', '每次打开“我的电脑”或者任意一个文件夹，都有读取软驱的动作']
- case_069 | dual=True | rejected=False | anchor_rejected=True | score=0.6558343739551264 | top_titles=[]
- case_070 | dual=True | rejected=False | anchor_rejected=True | score=0.6545358351480577 | top_titles=[]
- case_071 | dual=True | rejected=False | anchor_rejected=False | score=0.5393051046297166 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_072 | dual=True | rejected=False | anchor_rejected=False | score=0.7160927967199986 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_073 | dual=True | rejected=False | anchor_rejected=False | score=0.5747158017286327 | top_titles=['天权2000产品示意图及功能键说明', '如何控制 Internet Explorer 浏览器的进程数量？']
- case_074 | dual=True | rejected=False | anchor_rejected=False | score=0.6379417058026808 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何解决IE浏览器只能打开首页无法打开其他链接故障']
- case_075 | dual=True | rejected=False | anchor_rejected=False | score=0.6469656611636295 | top_titles=['万全2100如何设置启动顺序-', '没有并口的笔记本如何接加密狗等并口设备？']
- case_076 | dual=True | rejected=False | anchor_rejected=False | score=0.4308400503486453 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_077 | dual=False | rejected=False | anchor_rejected=False | score=0.6389369314650899 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_078 | dual=True | rejected=False | anchor_rejected=False | score=0.5753968173078591 | top_titles=['联想支持Windows 10系统升级的机型列表', 'Windows 8.1 Update （KB2919355）常见问题']
- case_079 | dual=True | rejected=False | anchor_rejected=False | score=0.6394527798993104 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '31018765A 扬天T系列用户手册 V1.0']
- case_080 | dual=True | rejected=False | anchor_rejected=True | score=0.5471923206583731 | top_titles=[]
- case_081 | dual=False | rejected=False | anchor_rejected=False | score=0.7150443146829589 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_082 | dual=False | rejected=False | anchor_rejected=False | score=0.5594157508860635 | top_titles=['彩色喷墨多功能一体机M920用户使用手册', 'WinXP从待机状态唤醒后网络连接断开']

> Title weak hit is an automatic weak label, not final business accuracy.