# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-05T21:52:41`

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
- RAG_ANCHOR_EVIDENCE_MODE: legacy

## Summary

- Total cases: 82
- Normalization triggered: 19
- Normalization not triggered: 63
- Accepted with final docs: 60
- Low-confidence rejected: 3
- Top1 title weak hit: 13 (0.1585)
- Top2 title weak hit: 19 (0.2317)
- Expected no-answer correctly rejected: 2
- Expected no-answer anchor rejected: 7
- Expected no-answer not rejected: 14
- Expected-answer false rejected: 13
- Strong anchor cases: 49
- Hard anchor cases: 18
- Soft anchor cases: 39
- Negative anchor cases: 5
- No anchor cases: 33
- Hard evidence outside TopK: 0
- Negative anchor penalties: 0
- ANCHOR_EVIDENCE_MISSING: 19

## Group Metrics

- C_generic_answerable: total=18, top1=0, top2=1, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=1, manual_review=17
- A_anchor_answerable: total=26, top1=11, top2=13, false_rejected=6, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=5, manual_review=13
- E_confusing: total=15, top1=2, top2=5, false_rejected=6, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=6, manual_review=10
- B_anchor_unanswerable: total=15, top1=0, top2=0, false_rejected=0, no_answer_rejected=9, no_answer_accepted=6, anchor_missing=7, manual_review=6
- D_generic_unanswerable: total=8, top1=0, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0, manual_review=8

## A/B Comparison

- Positive: 0
- Neutral: 18
- Changed: 1
- Negative: 0

## Score Buckets

- >=0.50: 62
- <0.25: 1
- 0.35-0.50: 17
- 0.25-0.35: 2

## Threshold Recommendation

- Recommendation: `keep_0.35_pending_manual_review`
- Possible false rejections: ['case_025', 'case_026', 'case_027', 'case_030', 'case_039', 'case_040', 'case_057', 'case_070', 'case_071', 'case_072', 'case_074', 'case_077', 'case_080']
- Expected no-answer not rejected: ['case_042', 'case_043', 'case_047', 'case_048', 'case_049', 'case_052', 'case_061', 'case_062', 'case_063', 'case_064', 'case_065', 'case_066', 'case_067', 'case_068']
- Passed but title weak miss: ['case_001', 'case_004', 'case_007', 'case_011', 'case_012', 'case_017', 'case_018', 'case_019', 'case_020', 'case_021', 'case_029', 'case_033', 'case_034', 'case_037', 'case_038', 'case_053', 'case_054', 'case_055', 'case_056', 'case_058', 'case_059', 'case_060', 'case_069', 'case_075', 'case_079', 'case_081', 'case_082']

## Suspicious Cases

- case_001: score=0.6008744656644944, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6392528065200414, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_007: score=0.6753569962927506, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.5960423822155076, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012: score=0.5528272004696018, rejected=False, reason=['top2_title_weak_miss'], top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.6008744656644944 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5408365498966703 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Windows XP 关机故障']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.5334220277942212 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6392528065200414 | top_titles=['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.6136977712690107 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Windows XP 关机故障']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5540881137202314 | top_titles=['在Windows 7下如何配置无线网络', '联想手机A789如何连接无线网络上网']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6753569962927506 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6470809784673989 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.5763717477477452 | top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5306084949595348 | top_titles=['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.5960423822155076 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.5528272004696018 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.6091339920284081 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6257082250361561 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Excel表导入 Access 2010 后时间显示错误怎么办-']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.5976743842422776 | top_titles=['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5680190786359409 | top_titles=['Outlook为何没有已发送邮件的记录-', '将Outlook设为Mac默认程序后为何仍弹出Apple Mail？']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5709278805724769 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.8267902759219896 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用导航光盘安装操作系统时提示CD-KEY序列号从何处查找-']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.6330810459923838 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '两台电脑如何共享访问']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.6068842887143807 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5745253297903441 | top_titles=['Windows XP 关机故障', '智能电视开不了机并且指示灯都不亮怎么办？']
- case_022 | dual=False | rejected=False | anchor_rejected=True | score=0.6247332738634324 | top_titles=[]
- case_023 | dual=False | rejected=False | anchor_rejected=True | score=0.5226976597901252 | top_titles=[]
- case_024 | dual=False | rejected=False | anchor_rejected=True | score=0.7026640656366148 | top_titles=[]
- case_025 | dual=False | rejected=True | anchor_rejected=False | score=0.2304566867110534 | top_titles=[]
- case_026 | dual=False | rejected=False | anchor_rejected=True | score=0.5524631159808335 | top_titles=[]
- case_027 | dual=False | rejected=False | anchor_rejected=True | score=0.6764220613462408 | top_titles=[]
- case_028 | dual=False | rejected=False | anchor_rejected=False | score=0.49208120098477204 | top_titles=['将Outlook设为Mac默认程序后为何仍弹出Apple Mail？', '万全T110 1510如何清除主板CMOS-']
- case_029 | dual=False | rejected=False | anchor_rejected=False | score=0.6708427116651005 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_030 | dual=False | rejected=False | anchor_rejected=True | score=0.7692985463567618 | top_titles=[]
- case_031 | dual=False | rejected=False | anchor_rejected=False | score=0.7192581917010361 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何恢复Windows 7任务栏输入法图标']
- case_032 | dual=False | rejected=False | anchor_rejected=False | score=0.4314077200878146 | top_titles=['Lenovo G485无线网络连接不上的解决方案', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”']
- case_033 | dual=False | rejected=False | anchor_rejected=False | score=0.43336759098505473 | top_titles=['关于系统提示登录进程初始化失败问题的解决方案', '常用的文件名后缀（扩展名）汇总']
- case_034 | dual=False | rejected=False | anchor_rejected=False | score=0.6531708362784114 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', 'LSI MegaRAID阵列卡模拟界面']
- case_035 | dual=False | rejected=False | anchor_rejected=False | score=0.5846271189265217 | top_titles=['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '联想支持Windows 10系统升级的机型列表']
- case_036 | dual=False | rejected=False | anchor_rejected=False | score=0.5728133963421955 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Lenovo G485 USB3.0驱动程序安装不上的解决方法']
- case_037 | dual=False | rejected=False | anchor_rejected=False | score=0.6758955953315324 | top_titles=['联想支持Windows 10系统升级的机型列表', '万全2100如何设置启动顺序-']
- case_038 | dual=False | rejected=False | anchor_rejected=False | score=0.6602637790278683 | top_titles=['Windows 2000蓝屏死机故障分析与排除（2）', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_039 | dual=False | rejected=False | anchor_rejected=True | score=0.4857593690776704 | top_titles=[]
- case_040 | dual=False | rejected=False | anchor_rejected=True | score=0.5770873287821828 | top_titles=[]
- case_041 | dual=False | rejected=False | anchor_rejected=True | score=0.7473319323255511 | top_titles=[]
- case_042 | dual=False | rejected=False | anchor_rejected=False | score=0.46274917028409407 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '联想ET360摄像头用户使用手册']
- case_043 | dual=False | rejected=False | anchor_rejected=False | score=0.5826815394451205 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_044 | dual=False | rejected=True | anchor_rejected=False | score=0.34444634346994896 | top_titles=[]
- case_045 | dual=False | rejected=False | anchor_rejected=True | score=0.5589914356041555 | top_titles=[]
- case_046 | dual=False | rejected=False | anchor_rejected=True | score=0.45617584750403445 | top_titles=[]
- case_047 | dual=False | rejected=False | anchor_rejected=False | score=0.5624107042355654 | top_titles=['万全T220&#38;amp;#38;270 G5系统用户手册', '彩色喷墨多功能一体机M920用户使用手册']
- case_048 | dual=False | rejected=False | anchor_rejected=False | score=0.36441147210615726 | top_titles=['Windows 7 Windows 8下如何打开麦克风', '使用微软cleanup_tool清除Microsoft .NET Framework']
- case_049 | dual=False | rejected=False | anchor_rejected=False | score=0.6253725515794768 | top_titles=['万全2100如何设置启动顺序-', 'Intel SE7501HG2 服务器主板的故障代码。']
- case_050 | dual=False | rejected=True | anchor_rejected=False | score=0.34367854975700673 | top_titles=[]
- case_051 | dual=False | rejected=False | anchor_rejected=True | score=0.5959733580638135 | top_titles=[]
- case_052 | dual=False | rejected=False | anchor_rejected=False | score=0.4582155292916029 | top_titles=['联想手机A820t备份联系人与短信的方法', '彩色喷墨多功能一体机M920用户使用手册']
- case_053 | dual=False | rejected=False | anchor_rejected=False | score=0.49867030388447503 | top_titles=['联想智能电视可以像电脑一样观看网页么？能看网页中的视频么？', '万全T200 2020 第五章 常用操作系统安装指南']
- case_054 | dual=False | rejected=False | anchor_rejected=False | score=0.6511625522696222 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '启天IV代保护卡多媒体教程']
- case_055 | dual=False | rejected=False | anchor_rejected=False | score=0.4991018190400882 | top_titles=['万全T200 2020 第五章 常用操作系统安装指南', '联想硬盘保护EDU7.X的安装方法']
- case_056 | dual=False | rejected=False | anchor_rejected=False | score=0.5114368581395443 | top_titles=['暴风影音的DLNA功能怎么用', '31018765A 扬天T系列用户手册 V1.0']
- case_057 | dual=False | rejected=False | anchor_rejected=True | score=0.5151183387231875 | top_titles=[]
- case_058 | dual=False | rejected=False | anchor_rejected=False | score=0.46364327333733435 | top_titles=['WPS Office中如何打印稿纸', 'Windows 2000蓝屏死机故障分析与排除（2）']
- case_059 | dual=False | rejected=False | anchor_rejected=False | score=0.6862797120641954 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_060 | dual=False | rejected=False | anchor_rejected=False | score=0.6393179803425216 | top_titles=['联想支持Windows 10系统升级的机型列表', 'Windows 7下如何实现共享上网']
- case_061 | dual=False | rejected=False | anchor_rejected=False | score=0.6007119325690711 | top_titles=['TR280 G3-TR350 G7 如何查看和清除主板BMC的 SEL日志？', '没有并口的笔记本如何接加密狗等并口设备？']
- case_062 | dual=False | rejected=False | anchor_rejected=False | score=0.4422621297378252 | top_titles=['联想ET360摄像头应用程序帮助文档', 'LJ1700用户使用手册']
- case_063 | dual=False | rejected=False | anchor_rejected=False | score=0.4498756400464719 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）']
- case_064 | dual=False | rejected=False | anchor_rejected=False | score=0.580043465602339 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '在按下键盘上取消CapsLock,NumLock,ScrLock声音']
- case_065 | dual=False | rejected=False | anchor_rejected=False | score=0.5695910098526595 | top_titles=['31018765A 扬天T系列用户手册 V1.0', '如何备份幸福之家4.X中的日记']
- case_066 | dual=False | rejected=False | anchor_rejected=False | score=0.40189294773844564 | top_titles=['Intel SE7501HG2 服务器主板的故障代码。', '联想手机A820t备份联系人与短信的方法']
- case_067 | dual=False | rejected=False | anchor_rejected=False | score=0.46337847965057716 | top_titles=['启天IV代保护卡多媒体教程', '笔记本双显卡如何切换']
- case_068 | dual=False | rejected=False | anchor_rejected=False | score=0.5457247311670705 | top_titles=['宽带连接频繁掉线', '外接VGA设备后笔记本LCD没有显示而VGA显示正常']
- case_069 | dual=True | rejected=False | anchor_rejected=False | score=0.6584261285983796 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Windows 7下如何实现共享上网']
- case_070 | dual=True | rejected=False | anchor_rejected=True | score=0.654186466731582 | top_titles=[]
- case_071 | dual=True | rejected=False | anchor_rejected=True | score=0.5393128652070895 | top_titles=[]
- case_072 | dual=True | rejected=False | anchor_rejected=True | score=0.7174122960467699 | top_titles=[]
- case_073 | dual=True | rejected=False | anchor_rejected=False | score=0.4559020894791215 | top_titles=['windows 系统进程', 'Excel如何冻结首行首列 多行多列']
- case_074 | dual=True | rejected=False | anchor_rejected=True | score=0.6372348850112737 | top_titles=[]
- case_075 | dual=True | rejected=False | anchor_rejected=False | score=0.6257691458874628 | top_titles=['万全2100如何设置启动顺序-', 'cc300摄像头安装驱动程序时连接电脑的顺序']
- case_076 | dual=True | rejected=False | anchor_rejected=False | score=0.4319956534620342 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_077 | dual=False | rejected=False | anchor_rejected=True | score=0.6395659850954756 | top_titles=[]
- case_078 | dual=True | rejected=False | anchor_rejected=False | score=0.5721348975698355 | top_titles=['联想支持Windows 10系统升级的机型列表', 'Windows 8.1 Update （KB2919355）常见问题']
- case_079 | dual=True | rejected=False | anchor_rejected=False | score=0.6412804215477895 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '31018765A 扬天T系列用户手册 V1.0']
- case_080 | dual=True | rejected=False | anchor_rejected=True | score=0.5491564850554483 | top_titles=[]
- case_081 | dual=False | rejected=False | anchor_rejected=False | score=0.7179281092586698 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_082 | dual=False | rejected=False | anchor_rejected=False | score=0.5228379434888449 | top_titles=['Windows Storage Server 2003用户手册v1.0', '安装最新的 Windows 8.1 Update']

> Title weak hit is an automatic weak label, not final business accuracy.