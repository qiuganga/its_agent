# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-05T18:56:53`

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

- Total cases: 82
- Normalization triggered: 19
- Normalization not triggered: 63
- Accepted with final docs: 81
- Low-confidence rejected: 1
- Top1 title weak hit: 7 (0.0854)
- Top2 title weak hit: 9 (0.1098)
- Expected no-answer correctly rejected: 0
- Expected no-answer anchor rejected: 0
- Expected no-answer not rejected: 23
- Expected-answer false rejected: 1
- Strong anchor cases: 0
- ANCHOR_EVIDENCE_MISSING: 0

## Group Metrics

- C_generic_answerable: total=20, top1=1, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=18
- E_confusing: total=15, top1=1, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=13
- A_anchor_answerable: total=24, top1=5, top2=5, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=19
- B_anchor_unanswerable: total=15, top1=0, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=15, anchor_missing=0, manual_review=15
- D_generic_unanswerable: total=8, top1=0, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0, manual_review=8

## A/B Comparison

- Positive: 0
- Neutral: 17
- Changed: 2
- Negative: 0

## Score Buckets

- >=0.50: 63
- <0.25: 1
- 0.35-0.50: 18

## Threshold Recommendation

- Recommendation: `keep_0.35_pending_manual_review`
- Possible false rejections: ['case_025']
- Expected no-answer not rejected: ['case_022', 'case_023', 'case_024', 'case_041', 'case_042', 'case_043', 'case_044', 'case_045', 'case_046', 'case_047', 'case_048', 'case_049', 'case_050', 'case_051', 'case_052', 'case_061', 'case_062', 'case_063', 'case_064', 'case_065', 'case_066', 'case_067', 'case_068']
- Passed but title weak miss: ['case_001', 'case_004', 'case_006', 'case_007', 'case_011', 'case_012', 'case_015', 'case_017', 'case_018', 'case_019', 'case_020', 'case_021', 'case_026', 'case_027', 'case_028', 'case_029', 'case_030', 'case_031', 'case_032', 'case_033', 'case_034', 'case_035', 'case_036', 'case_037', 'case_038', 'case_039', 'case_040', 'case_053', 'case_054', 'case_055', 'case_056', 'case_057', 'case_058', 'case_059', 'case_060', 'case_069', 'case_070', 'case_071', 'case_072', 'case_073', 'case_074', 'case_075', 'case_076', 'case_077', 'case_078', 'case_079', 'case_080', 'case_081', 'case_082']

## Suspicious Cases

- case_001: score=0.5996320427889443, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004: score=0.6378567701270021, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_006: score=0.5827017107573725, rejected=False, reason=['top2_title_weak_miss'], top_titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_007: score=0.6737145710754403, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_011: score=0.5937000844636269, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.5996320427889443 | top_titles=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.5418942996633378 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_003 | dual=True | rejected=False | anchor_rejected=False | score=0.5321294400005172 | top_titles=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.6378567701270021 | top_titles=['Windows XP 关机故障', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.6147525830605863 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- case_006 | dual=False | rejected=False | anchor_rejected=False | score=0.5827017107573725 | top_titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.6737145710754403 | top_titles=['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.6464543786940902 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '关于电池充电、保养、设置、较准的方法汇总']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.5788143784246169 | top_titles=['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.5307983527644906 | top_titles=['如何添加启用蓝牙的设备', '如何备份幸福之家4.X中的日记']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.5937000844636269 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- case_012 | dual=True | rejected=False | anchor_rejected=False | score=0.5527975914307299 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.608228833243917 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '台式和一体机蓝屏报错代码：0x0000007B']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.6256422368289987 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.6220325995450947 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.5673946931934832 | top_titles=['Outlook为何没有已发送邮件的记录-', '彩色喷墨多功能一体机M920校准墨盒的操作']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.5692075749724964 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', 'Vista系统下随机软件的安装与卸载']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.8251703878532951 | top_titles=['联想硬盘保护EDU7.X的安装方法', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.6342763782272519 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '两台电脑如何共享访问']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.6087566556231153 | top_titles=['万全T100-T400-T468 1008的硬盘配置方案', '天权2000产品示意图及功能键说明']
- case_021 | dual=False | rejected=False | anchor_rejected=False | score=0.5979516077584652 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', '联想V858-V658手机如何使用语音短信功能？']
- case_022 | dual=False | rejected=False | anchor_rejected=False | score=0.6240284527596849 | top_titles=['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- case_023 | dual=False | rejected=False | anchor_rejected=False | score=0.5234135880204545 | top_titles=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- case_024 | dual=False | rejected=False | anchor_rejected=False | score=0.7034783852489642 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- case_025 | dual=False | rejected=True | anchor_rejected=False | score=0.23050427501101342 | top_titles=[]
- case_026 | dual=False | rejected=False | anchor_rejected=False | score=0.552589285282708 | top_titles=['联想手机如何在桌面上添加文件夹', 'Windows 8.1 Update （KB2919355）常见问题']
- case_027 | dual=False | rejected=False | anchor_rejected=False | score=0.674435526402449 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '万全T168板载SATA RAID系统设置']
- case_028 | dual=False | rejected=False | anchor_rejected=False | score=0.49249328611550547 | top_titles=['万全T110 1510如何清除主板CMOS-', '万全3200C 系统用户手册']
- case_029 | dual=False | rejected=False | anchor_rejected=False | score=0.6699499351481921 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_030 | dual=False | rejected=False | anchor_rejected=False | score=0.76748572046308 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_031 | dual=False | rejected=False | anchor_rejected=False | score=0.7173662561725221 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_032 | dual=False | rejected=False | anchor_rejected=False | score=0.48212185738266783 | top_titles=['Lenovo Miix3-830使用说明书', '联想各机型升级Windows 8.1操作指导及注意事项汇总']
- case_033 | dual=False | rejected=False | anchor_rejected=False | score=0.4317689674547863 | top_titles=['关于系统提示登录进程初始化失败问题的解决方案', '万全1160-1060服务器使用板载声卡跳线说明']
- case_034 | dual=False | rejected=False | anchor_rejected=False | score=0.6976268915773206 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_035 | dual=False | rejected=False | anchor_rejected=False | score=0.5994755751971191 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想存储光纤通道卡Qlogic Qla23XX HBA用户使用手册']
- case_036 | dual=False | rejected=False | anchor_rejected=False | score=0.5728133963421955 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_037 | dual=False | rejected=False | anchor_rejected=False | score=0.729563309867394 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_038 | dual=False | rejected=False | anchor_rejected=False | score=0.6631062191748385 | top_titles=['Windows 2000蓝屏死机故障分析与排除（2）', '彩色喷墨多功能一体机M920用户使用手册']
- case_039 | dual=False | rejected=False | anchor_rejected=False | score=0.48851626410048055 | top_titles=['DP300如何恢复到出厂缺省设置？', '屏幕保护功能介绍以及不同系统下如何设置或取消屏幕保护（屏保）功能']
- case_040 | dual=False | rejected=False | anchor_rejected=False | score=0.5775120548614656 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'Intel SE7501HG2 服务器主板的故障代码。']
- case_041 | dual=False | rejected=False | anchor_rejected=False | score=0.7481672560608225 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_042 | dual=False | rejected=False | anchor_rejected=False | score=0.4610644560370447 | top_titles=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '联想ET360摄像头用户使用手册']
- case_043 | dual=False | rejected=False | anchor_rejected=False | score=0.5855192624449211 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_044 | dual=False | rejected=False | anchor_rejected=False | score=0.3516448216972082 | top_titles=['视频指导：Win7系统下如何解决缺少VC++ 2010文件问题', '宽带连接频繁掉线']
- case_045 | dual=False | rejected=False | anchor_rejected=False | score=0.5592064626360325 | top_titles=['如何解决IE浏览器只能打开首页无法打开其他链接故障', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_046 | dual=False | rejected=False | anchor_rejected=False | score=0.4564858805563042 | top_titles=['万全R510 5B20 第一章 产品简介', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_047 | dual=False | rejected=False | anchor_rejected=False | score=0.5614944551492607 | top_titles=['万全T220&#38;amp;#38;270 G5系统用户手册', '彩色喷墨多功能一体机M920用户使用手册']
- case_048 | dual=False | rejected=False | anchor_rejected=False | score=0.36535272276390723 | top_titles=['Windows 7 Windows 8下如何打开麦克风', '使用微软cleanup_tool清除Microsoft .NET Framework']
- case_049 | dual=False | rejected=False | anchor_rejected=False | score=0.675793572613701 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_050 | dual=False | rejected=False | anchor_rejected=False | score=0.37583511392237245 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '万全R510 5B20 第一章 产品简介']
- case_051 | dual=False | rejected=False | anchor_rejected=False | score=0.5940633676301664 | top_titles=['如何解决IE浏览器只能打开首页无法打开其他链接故障', '联想支持Windows 10系统升级的机型列表']
- case_052 | dual=False | rejected=False | anchor_rejected=False | score=0.459293183380843 | top_titles=['数码学习机D100如何播放SD-MMC存储卡上的MP3歌曲', '联想手机A820t备份联系人与短信的方法']
- case_053 | dual=False | rejected=False | anchor_rejected=False | score=0.4988447848124805 | top_titles=['联想智能电视可以像电脑一样观看网页么？能看网页中的视频么？', '万全T200 2020 第五章 常用操作系统安装指南']
- case_054 | dual=False | rejected=False | anchor_rejected=False | score=0.6518262329116526 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '启天IV代保护卡多媒体教程']
- case_055 | dual=False | rejected=False | anchor_rejected=False | score=0.4996936651240132 | top_titles=['万全T200 2020 第五章 常用操作系统安装指南', '联想硬盘保护EDU7.X的安装方法']
- case_056 | dual=False | rejected=False | anchor_rejected=False | score=0.5111423087606276 | top_titles=['暴风影音的DLNA功能怎么用', '31018765A 扬天T系列用户手册 V1.0']
- case_057 | dual=False | rejected=False | anchor_rejected=False | score=0.5148227194864595 | top_titles=['票据打印机DP600、DP8000用户手册', 'Lenovo Miix3-830使用说明书']
- case_058 | dual=False | rejected=False | anchor_rejected=False | score=0.46285666796023794 | top_titles=['WPS Office中如何打印稿纸', 'Windows 2000蓝屏死机故障分析与排除（2）']
- case_059 | dual=False | rejected=False | anchor_rejected=False | score=0.6892448055962526 | top_titles=['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_060 | dual=False | rejected=False | anchor_rejected=False | score=0.6375543957266583 | top_titles=['联想支持Windows 10系统升级的机型列表', '如何在任务栏显示或隐藏电池图标']
- case_061 | dual=False | rejected=False | anchor_rejected=False | score=0.5987101041885762 | top_titles=['TR280 G3-TR350 G7 如何查看和清除主板BMC的 SEL日志？', '没有并口的笔记本如何接加密狗等并口设备？']
- case_062 | dual=False | rejected=False | anchor_rejected=False | score=0.4397109220252249 | top_titles=['联想ET360摄像头应用程序帮助文档', 'LJ1700用户使用手册']
- case_063 | dual=False | rejected=False | anchor_rejected=False | score=0.4515992463066031 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_064 | dual=False | rejected=False | anchor_rejected=False | score=0.5772869376853643 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', 'WinXP从待机状态唤醒后网络连接断开']
- case_065 | dual=False | rejected=False | anchor_rejected=False | score=0.5689694143688193 | top_titles=['31018765A 扬天T系列用户手册 V1.0', '如何备份幸福之家4.X中的日记']
- case_066 | dual=False | rejected=False | anchor_rejected=False | score=0.3995650098544243 | top_titles=['Intel SE7501HG2 服务器主板的故障代码。', '联想手机A820t备份联系人与短信的方法']
- case_067 | dual=False | rejected=False | anchor_rejected=False | score=0.46476173479583327 | top_titles=['启天IV代保护卡多媒体教程', '笔记本双显卡如何切换']
- case_068 | dual=False | rejected=False | anchor_rejected=False | score=0.5464838246227095 | top_titles=['宽带连接频繁掉线', '外接VGA设备后笔记本LCD没有显示而VGA显示正常']
- case_069 | dual=True | rejected=False | anchor_rejected=False | score=0.6537533499014949 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何解决IE浏览器只能打开首页无法打开其他链接故障']
- case_070 | dual=True | rejected=False | anchor_rejected=False | score=0.6549948076262232 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_071 | dual=True | rejected=False | anchor_rejected=False | score=0.5370798347973094 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- case_072 | dual=True | rejected=False | anchor_rejected=False | score=0.7174122960467699 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_073 | dual=True | rejected=False | anchor_rejected=False | score=0.5726788838774828 | top_titles=['天权2000产品示意图及功能键说明', '如何控制 Internet Explorer 浏览器的进程数量？']
- case_074 | dual=True | rejected=False | anchor_rejected=False | score=0.6374474398884538 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '如何解决IE浏览器只能打开首页无法打开其他链接故障']
- case_075 | dual=True | rejected=False | anchor_rejected=False | score=0.6469656611636295 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '同禧有内置音箱的机型如何屏蔽内置音箱']
- case_076 | dual=True | rejected=False | anchor_rejected=False | score=0.45219775650291427 | top_titles=['Lenovo Miix3-830使用说明书', '联想硬盘保护EDU7.X的安装方法']
- case_077 | dual=False | rejected=False | anchor_rejected=False | score=0.6392359129605507 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_078 | dual=True | rejected=False | anchor_rejected=False | score=0.5766461594294431 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_079 | dual=True | rejected=False | anchor_rejected=False | score=0.6397339466004388 | top_titles=['没有并口的笔记本如何接加密狗等并口设备？', '31018765A 扬天T系列用户手册 V1.0']
- case_080 | dual=True | rejected=False | anchor_rejected=False | score=0.5471923206583731 | top_titles=['在联系人窗口中怎样查看SIM卡上的号码？', '联想支持Windows 10系统升级的机型列表']
- case_081 | dual=False | rejected=False | anchor_rejected=False | score=0.7184231166418007 | top_titles=['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- case_082 | dual=False | rejected=False | anchor_rejected=False | score=0.5585660052417283 | top_titles=['彩色喷墨多功能一体机M920用户使用手册', 'WinXP从待机状态唤醒后网络连接断开']

> Title weak hit is an automatic weak label, not final business accuracy.