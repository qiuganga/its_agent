# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-04T22:13:22`

## Settings

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

- >=0.50: 21
- 0.35-0.50: 3

## Threshold Recommendation

- Recommendation: `consider_raising_to_0.40`
- Possible false rejections: []
- Expected no-answer not rejected: ['case_022', 'case_023', 'case_024']
- Passed but title weak miss: ['case_001', 'case_002', 'case_003', 'case_005', 'case_006', 'case_007', 'case_008', 'case_009', 'case_011', 'case_012', 'case_015', 'case_017', 'case_018', 'case_020', 'case_021']

## Suspicious Cases

- case_001: score=0.563663003915388, rejected=False, reason=['top2_title_weak_miss'], top_titles=['Visio 2010-2007 形状面板不见了怎么办？', 'Lenovo G485无线网络连接不上的解决方案']
- case_002: score=0.5465835408374322, rejected=False, reason=['top2_title_weak_miss'], top_titles=['电子词典LN4000操作汇总', 'Internet Explorer版本升级说明']
- case_003: score=0.5297994387191403, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何设置显卡的电源管理', '智能电视开不了机并且指示灯都不亮怎么办？']
- case_005: score=0.5852749184865331, rejected=False, reason=['top2_title_weak_miss'], top_titles=['新圆梦F系列电脑运行游戏卡', '电子词典LN4000操作汇总']
- case_006: score=0.5815056768454312, rejected=False, reason=['top2_title_weak_miss'], top_titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', 'Windows 2000蓝屏死机故障分析与排除']

## Case Details

- case_001 | dual=True | rejected=False | score=0.563663003915388 | top_titles=['Visio 2010-2007 形状面板不见了怎么办？', 'Lenovo G485无线网络连接不上的解决方案']
- case_002 | dual=True | rejected=False | score=0.5465835408374322 | top_titles=['电子词典LN4000操作汇总', 'Internet Explorer版本升级说明']
- case_003 | dual=True | rejected=False | score=0.5297994387191403 | top_titles=['如何设置显卡的电源管理', '智能电视开不了机并且指示灯都不亮怎么办？']
- case_004 | dual=False | rejected=False | score=0.6374676146212903 | top_titles=['开机蓝屏或提示登录进程初始化失败问题的解决方案（Vista）', 'Windows 2000蓝屏死机故障分析与排除']
- case_005 | dual=False | rejected=False | score=0.5852749184865331 | top_titles=['新圆梦F系列电脑运行游戏卡', '电子词典LN4000操作汇总']
- case_006 | dual=False | rejected=False | score=0.5815056768454312 | top_titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', 'Windows 2000蓝屏死机故障分析与排除']
- case_007 | dual=True | rejected=False | score=0.6403360786089017 | top_titles=['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '电子词典LN4000操作汇总']
- case_008 | dual=False | rejected=False | score=0.6063672042602983 | top_titles=['Windows 2000蓝屏死机故障分析与排除', '电子词典LN4000操作汇总']
- case_009 | dual=True | rejected=False | score=0.5346016565130154 | top_titles=['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '关于NOKIA手机通过红外线连接旭日150拨号上网的解决方案']
- case_010 | dual=True | rejected=False | score=0.4876205739251792 | top_titles=['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- case_011 | dual=True | rejected=False | score=0.4581206241694894 | top_titles=['如何通过联想电源管理软件调整电源模式', '电脑会自动开机启动，是什么问题？']
- case_012 | dual=True | rejected=False | score=0.5353152144285066 | top_titles=['电子词典LN4000操作汇总', 'Windows 2000蓝屏死机故障分析与排除']
- case_013 | dual=False | rejected=False | score=0.6088593635218738 | top_titles=['联想新圆梦F系列机型运行游戏卡或无法运行的解决方案', '电子词典LN4000操作汇总']
- case_014 | dual=False | rejected=False | score=0.6272676879763852 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Lenovo G485无线网络连接不上的解决方案']
- case_015 | dual=False | rejected=False | score=0.5935850226243552 | top_titles=['电子词典LN4000操作汇总', '单向可Ping通的原因与原理-']
- case_016 | dual=False | rejected=False | score=0.5187732179338329 | top_titles=['如何给某分区、光驱、U盘分配盘符', 'Outlook为何没有已发送邮件的记录-']
- case_017 | dual=False | rejected=False | score=0.5613529304366445 | top_titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', 'Lenovo G485无线网络连接不上的解决方案']
- case_018 | dual=False | rejected=False | score=0.4833466986507205 | top_titles=['联想摄像头随机软件能否保存视频捕捉属性以及视频捕捉参数？', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）']
- case_019 | dual=False | rejected=False | score=0.6332407979125517 | top_titles=['电子词典LN4000操作汇总', '手机或平板电脑无法访问百度相关网站的解决办法']
- case_020 | dual=False | rejected=False | score=0.5830428439338319 | top_titles=['鲁大师怎么用？有哪些功能？', '如何在任务栏显示或隐藏电池图标']
- case_021 | dual=False | rejected=False | score=0.5774448839957588 | top_titles=['电子词典LN4000操作汇总', '智能电视开不了机并且指示灯都不亮怎么办？']
- case_022 | dual=False | rejected=False | score=0.5807061824909716 | top_titles=['联想一键恢复的使用方法', '电子词典LN4000操作汇总']
- case_023 | dual=False | rejected=False | score=0.5213189565079955 | top_titles=['Windows自带电源管理（包括休眠、待机和睡眠）的设置方法', 'Windows 2000蓝屏死机故障分析与排除']
- case_024 | dual=False | rejected=False | score=0.6764614752909739 | top_titles=['在Windows XP下如何配置无线网络', '如何恢复Windows XP任务栏输入法图标']

> Title weak hit is an automatic weak label, not final business accuracy.