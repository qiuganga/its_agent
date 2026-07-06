# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-06T13:53:59`

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
- RAG_BM25_MODE: off
- RAG_BM25_CANDIDATE_TOP_K: 10

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
- BM25 mode: off
- BM25 candidates: 0
- BM25 unique additions: 0
- BM25/vector overlap: 0 (0.0)
- BM25/title overlap: 0 (0.0)
- Missing source_id before rerank: 0

## Group Metrics

- C_generic_answerable: total=18, top1=0, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=17
- A_anchor_answerable: total=26, top1=8, top2=10, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=16
- E_confusing: total=15, top1=2, top2=4, false_rejected=3, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=3, manual_review=11
- B_anchor_unanswerable: total=15, top1=0, top2=0, false_rejected=0, no_answer_rejected=10, no_answer_accepted=5, anchor_missing=9, manual_review=5
- D_generic_unanswerable: total=8, top1=0, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0, manual_review=8

## A/B Comparison

- Positive: 0
- Neutral: 19
- Changed: 0
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

- case_001: score=0.6002226487630875, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6406379017678416, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_007: score=0.6757030774260901, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.5970389138222207, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012: score=0.5525611564456012, rejected=False, reason=['top2_title_weak_miss'], top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.6002226487630875 | bm25=0 unique=0 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5405179173684178 | bm25=0 unique=0 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.5342643260485382 | bm25=0 unique=0 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6406379017678416 | bm25=0 unique=0 | top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.6145974245505053 | bm25=0 unique=0 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5722795227547683 | bm25=0 unique=0 | top_titles=['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6757030774260901 | bm25=0 unique=0 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6464803308361637 | bm25=0 unique=0 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.5799463253122964 | bm25=0 unique=0 | top_titles=['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5298705776660186 | bm25=0 unique=0 | top_titles=['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.5970389138222207 | bm25=0 unique=0 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.5525611564456012 | bm25=0 unique=0 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.6068214543736046 | bm25=0 unique=0 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6265362901426996 | bm25=0 unique=0 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.6245951748730767 | bm25=0 unique=0 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5646940578797964 | bm25=0 unique=0 | top_titles=['Outlook为何没有已发送邮件的记录-', '彩色喷墨多功能一体机M920校准墨盒的操作']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5726908113206901 | bm25=0 unique=0 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.8245437052412785 | bm25=0 unique=0 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用导航光盘安装操作系统时提示CD-KEY序列号从何处查找-']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.633587028373329 | bm25=0 unique=0 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '两台电脑如何共享访问']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.610711747446053 | bm25=0 unique=0 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5765205825448232 | bm25=0 unique=0 | top_titles=['Windows XP 关机故障', '智能电视开不了机并且指示灯都不亮怎么办？']
- case_022 | dual=False | rejected=False | anchor_rejected=True | score=0.6248707379315541 | bm25=0 unique=0 | top_titles=[]
- case_023 | dual=False | rejected=False | anchor_rejected=True | score=0.5226951618288151 | bm25=0 unique=0 | top_titles=[]
- case_024 | dual=False | rejected=False | anchor_rejected=True | score=0.7042312876087977 | bm25=0 unique=0 | top_titles=[]
- case_025 | dual=False | rejected=True | anchor_rejected=False | score=0.230721069810123 | bm25=0 unique=0 | top_titles=[]
- case_026 | dual=False | rejected=False | anchor_rejected=False | score=0.552343374599052 | bm25=0 unique=0 | top_titles=['Windows 8.1 Update （KB2919355）常见问题', '联想手机如何在桌面上添加文件夹']
- case_027 | dual=False | rejected=False | anchor_rejected=False | score=0.67209759230952 | bm25=0 unique=0 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '万全T168板载SATA RAID系统设置']
- case_028 | dual=False | rejected=False | anchor_rejected=False | score=0.49233040622041047 | bm25=0 unique=0 | top_titles=['万全T110 1510如何清除主板CMOS-', '万全3200C 系统用户手册']
- case_029 | dual=False | rejected=False | anchor_rejected=False | score=0.6685463288344757 | bm25=0 unique=0 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_030 | dual=False | rejected=False | anchor_rejected=False | score=0.7718513041376308 | bm25=0 unique=0 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_031 | dual=False | rejected=False | anchor_rejected=False | score=0.7173662561725221 | bm25=0 unique=0 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_032 | dual=False | rejected=False | anchor_rejected=False | score=0.4314077200878146 | bm25=0 unique=0 | top_titles=['Lenovo G485无线网络连接不上的解决方案', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”']
- case_033 | dual=False | rejected=False | anchor_rejected=False | score=0.43384642180450916 | bm25=0 unique=0 | top_titles=['关于系统提示登录进程初始化失败问题的解决方案', '常用的文件名后缀（扩展名）汇总']
- case_034 | dual=False | rejected=False | anchor_rejected=False | score=0.7002852130957377 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_035 | dual=False | rejected=False | anchor_rejected=False | score=0.5970072999259861 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_036 | dual=False | rejected=False | anchor_rejected=False | score=0.573405029887053 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Lenovo G485 USB3.0驱动程序安装不上的解决方法']
- case_037 | dual=False | rejected=False | anchor_rejected=False | score=0.7303141429547291 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_038 | dual=False | rejected=False | anchor_rejected=False | score=0.661017649627808 | bm25=0 unique=0 | top_titles=['Windows 2000蓝屏死机故障分析与排除（2）', '彩色喷墨多功能一体机M920用户使用手册']
- case_039 | dual=False | rejected=False | anchor_rejected=False | score=0.4866467449461317 | bm25=0 unique=0 | top_titles=['S620充电时充电指示灯为常绿并伴有橙色闪烁', '屏幕保护功能介绍以及不同系统下如何设置或取消屏幕保护（屏保）功能']
- case_040 | dual=False | rejected=False | anchor_rejected=False | score=0.5766256174992614 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Intel SE7501HG2 服务器主板的故障代码。']
- case_041 | dual=False | rejected=False | anchor_rejected=True | score=0.7469955538301233 | bm25=0 unique=0 | top_titles=[]
- case_042 | dual=False | rejected=False | anchor_rejected=False | score=0.46134498977535243 | bm25=0 unique=0 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '联想ET360摄像头用户使用手册']
- case_043 | dual=False | rejected=False | anchor_rejected=False | score=0.5895539038205799 | bm25=0 unique=0 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_044 | dual=False | rejected=True | anchor_rejected=False | score=0.34451030129107907 | bm25=0 unique=0 | top_titles=[]
- case_045 | dual=False | rejected=False | anchor_rejected=True | score=0.5591482185589947 | bm25=0 unique=0 | top_titles=[]
- case_046 | dual=False | rejected=False | anchor_rejected=True | score=0.45629498287021253 | bm25=0 unique=0 | top_titles=[]
- case_047 | dual=False | rejected=False | anchor_rejected=False | score=0.5631439174959046 | bm25=0 unique=0 | top_titles=['万全T220&#38;amp;#38;270 G5系统用户手册', '彩色喷墨多功能一体机M920用户使用手册']
- case_048 | dual=False | rejected=False | anchor_rejected=False | score=0.3654649841012392 | bm25=0 unique=0 | top_titles=['Windows 7 Windows 8下如何打开麦克风', '使用微软cleanup_tool清除Microsoft .NET Framework']
- case_049 | dual=False | rejected=False | anchor_rejected=True | score=0.6750001900839881 | bm25=0 unique=0 | top_titles=[]
- case_050 | dual=False | rejected=False | anchor_rejected=True | score=0.37502129960626185 | bm25=0 unique=0 | top_titles=[]
- case_051 | dual=False | rejected=False | anchor_rejected=True | score=0.5937360404437741 | bm25=0 unique=0 | top_titles=[]
- case_052 | dual=False | rejected=False | anchor_rejected=False | score=0.45855286595716055 | bm25=0 unique=0 | top_titles=['联想手机A820t备份联系人与短信的方法', '彩色喷墨多功能一体机M920用户使用手册']
- case_053 | dual=False | rejected=False | anchor_rejected=False | score=0.49667702249992635 | bm25=0 unique=0 | top_titles=['联想智能电视可以像电脑一样观看网页么？能看网页中的视频么？', '万全T200 2020 第五章 常用操作系统安装指南']
- case_054 | dual=False | rejected=False | anchor_rejected=False | score=0.6510179279303911 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '启天IV代保护卡多媒体教程']
- case_055 | dual=False | rejected=False | anchor_rejected=False | score=0.5000503001160016 | bm25=0 unique=0 | top_titles=['万全T200 2020 第五章 常用操作系统安装指南', '联想硬盘保护EDU7.X的安装方法']
- case_056 | dual=False | rejected=False | anchor_rejected=False | score=0.5115512648706189 | bm25=0 unique=0 | top_titles=['暴风影音的DLNA功能怎么用', '31018765A 扬天T系列用户手册 V1.0']
- case_057 | dual=False | rejected=False | anchor_rejected=False | score=0.5158253831850605 | bm25=0 unique=0 | top_titles=['票据打印机DP600、DP8000用户手册', 'Lenovo Miix3-830使用说明书']
- case_058 | dual=False | rejected=False | anchor_rejected=False | score=0.4618578593259125 | bm25=0 unique=0 | top_titles=['WPS Office中如何打印稿纸', 'Windows 2000蓝屏死机故障分析与排除（2）']
- case_059 | dual=False | rejected=False | anchor_rejected=False | score=0.688337567789393 | bm25=0 unique=0 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_060 | dual=False | rejected=False | anchor_rejected=False | score=0.6428972928493634 | bm25=0 unique=0 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在任务栏显示或隐藏电池图标']
- case_061 | dual=False | rejected=False | anchor_rejected=False | score=0.6004330218511027 | bm25=0 unique=0 | top_titles=['TR280 G3-TR350 G7 如何查看和清除主板BMC的 SEL日志？', '没有并口的笔记本如何接加密狗等并口设备？']
- case_062 | dual=False | rejected=False | anchor_rejected=False | score=0.4450089797374612 | bm25=0 unique=0 | top_titles=['联想ET360摄像头应用程序帮助文档', 'LJ1700用户使用手册']
- case_063 | dual=False | rejected=False | anchor_rejected=False | score=0.4504924577718803 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）']
- case_064 | dual=False | rejected=False | anchor_rejected=False | score=0.5805283003140687 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'WinXP从待机状态唤醒后网络连接断开']
- case_065 | dual=False | rejected=False | anchor_rejected=False | score=0.5685334262904739 | bm25=0 unique=0 | top_titles=['31018765A 扬天T系列用户手册 V1.0', '如何备份幸福之家4.X中的日记']
- case_066 | dual=False | rejected=False | anchor_rejected=False | score=0.40064022057400095 | bm25=0 unique=0 | top_titles=['Intel SE7501HG2 服务器主板的故障代码。', '联想手机A820t备份联系人与短信的方法']
- case_067 | dual=False | rejected=False | anchor_rejected=False | score=0.4641911547307269 | bm25=0 unique=0 | top_titles=['启天IV代保护卡多媒体教程', '笔记本双显卡如何切换']
- case_068 | dual=False | rejected=False | anchor_rejected=False | score=0.5463167350552038 | bm25=0 unique=0 | top_titles=['宽带连接频繁掉线', '每次打开“我的电脑”或者任意一个文件夹，都有读取软驱的动作']
- case_069 | dual=True | rejected=False | anchor_rejected=True | score=0.6581713599135842 | bm25=0 unique=0 | top_titles=[]
- case_070 | dual=True | rejected=False | anchor_rejected=True | score=0.6549948076262232 | bm25=0 unique=0 | top_titles=[]
- case_071 | dual=True | rejected=False | anchor_rejected=False | score=0.5375819747214422 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_072 | dual=True | rejected=False | anchor_rejected=False | score=0.7180200559515104 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_073 | dual=True | rejected=False | anchor_rejected=False | score=0.5727141231487103 | bm25=0 unique=0 | top_titles=['天权2000产品示意图及功能键说明', '如何控制 Internet Explorer 浏览器的进程数量？']
- case_074 | dual=True | rejected=False | anchor_rejected=False | score=0.6374474398884538 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何解决IE浏览器只能打开首页无法打开其他链接故障']
- case_075 | dual=True | rejected=False | anchor_rejected=False | score=0.6413527887242109 | bm25=0 unique=0 | top_titles=['万全2100如何设置启动顺序-', '没有并口的笔记本如何接加密狗等并口设备？']
- case_076 | dual=True | rejected=False | anchor_rejected=False | score=0.4326575001178841 | bm25=0 unique=0 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_077 | dual=False | rejected=False | anchor_rejected=False | score=0.6404839546540535 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_078 | dual=True | rejected=False | anchor_rejected=False | score=0.5721348975698355 | bm25=0 unique=0 | top_titles=['联想支持Windows 10系统升级的机型列表', 'Windows 8.1 Update （KB2919355）常见问题']
- case_079 | dual=True | rejected=False | anchor_rejected=False | score=0.6392983576254556 | bm25=0 unique=0 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '31018765A 扬天T系列用户手册 V1.0']
- case_080 | dual=True | rejected=False | anchor_rejected=True | score=0.5508075314216021 | bm25=0 unique=0 | top_titles=[]
- case_081 | dual=False | rejected=False | anchor_rejected=False | score=0.721321063819363 | bm25=0 unique=0 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_082 | dual=False | rejected=False | anchor_rejected=False | score=0.5599713222117099 | bm25=0 unique=0 | top_titles=['彩色喷墨多功能一体机M920用户使用手册', 'WinXP从待机状态唤醒后网络连接断开']

> Title weak hit is an automatic weak label, not final business accuracy.