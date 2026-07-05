# RAG Normalization A/B Comparison

- Generated at: `2026-07-04T22:27:05`
- Before report: `D:\sgg-agent\code\its_multi_agent\backend\knowledge\testdata\rag_eval_report_before_normalization_fix.json`
- Before generated at: `2026-07-03T01:11:38`
- After report: `D:\sgg-agent\code\its_multi_agent\backend\knowledge\testdata\rag_eval_report_after_normalization_fix.json`
- After generated at: `2026-07-04T22:13:22`

## Overall Delta

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| total_cases | 24 | 24 | 0 |
| normalization_triggered | 8 | 8 | 0 |
| normalization_not_triggered | 16 | 16 | 0 |
| dual_retrieval_count | 8 | 8 | 0 |
| single_retrieval_count | 16 | 16 | 0 |
| accepted_count | 24 | 24 | 0 |
| low_confidence_rejected_count | 0 | 0 | 0 |
| top1_title_weak_hit_count | 4 | 4 | 0 |
| top2_title_weak_hit_count | 6 | 6 | 0 |
| expected_no_answer_correctly_rejected | 0 | 0 | 0 |
| expected_no_answer_not_rejected | 3 | 3 | 0 |

## Classification Counts

- requires_manual_review: 7
- unchanged: 17

## Focus Cases

### case_001
- Question: 开不了机，屏幕不亮怎么办
- Normalized before: 无法开机，黑屏怎么办
- Normalized after: 无法开机，黑屏怎么办
- Dual before/after: True / True
- Candidates before/after: 36 / 36
- Top titles before: ['Excel文件菜单及相关功能灰色不可用怎么办？', 'Lenovo G485无线网络连接不上的解决方案']
- Top titles after: ['Visio 2010-2007 形状面板不见了怎么办？', 'Lenovo G485无线网络连接不上的解决方案']
- Scores before: [0.5793053643639449, 0.55943148704695]
- Scores after: [0.563663003915388, 0.560278031542995]
- Top2 weak hit before/after: False / False
- Classification: `requires_manual_review`

### case_002
- Question: 开机没反应怎么办
- Normalized before: 无法开机怎么办
- Normalized after: 无法开机怎么办
- Dual before/after: True / True
- Candidates before/after: 33 / 32
- Top titles before: ['电子词典LN4000操作汇总', 'Internet Explorer版本升级说明']
- Top titles after: ['电子词典LN4000操作汇总', 'Internet Explorer版本升级说明']
- Scores before: [0.5455114883812666, 0.4976137946277454]
- Scores after: [0.5465835408374322, 0.5005123284478692]
- Top2 weak hit before/after: False / False
- Classification: `unchanged`

### case_003
- Question: 屏幕不亮但风扇会转，电脑黑屏怎么处理
- Normalized before: 黑屏但风扇会转，电脑黑屏怎么处理
- Normalized after: 黑屏但风扇会转怎么处理
- Dual before/after: True / True
- Candidates before/after: 30 / 41
- Top titles before: ['如何设置显卡的电源管理', '智能电视开不了机并且指示灯都不亮怎么办？']
- Top titles after: ['如何设置显卡的电源管理', '智能电视开不了机并且指示灯都不亮怎么办？']
- Scores before: [0.5248353800296048, 0.5192173477280958]
- Scores after: [0.5297994387191403, 0.5241215375221333]
- Top2 weak hit before/after: False / False
- Classification: `requires_manual_review`

### case_006
- Question: 无线网络连不上怎么办
- Normalized before: 无线网络连不上怎么办
- Normalized after: 无线网络连不上怎么办
- Dual before/after: False / False
- Candidates before/after: 25 / 24
- Top titles before: ['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', 'Windows 2000蓝屏死机故障分析与排除']
- Top titles after: ['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', 'Windows 2000蓝屏死机故障分析与排除']
- Scores before: [0.5815833111323668, 0.5558632272453514]
- Scores after: [0.5815056768454312, 0.5569448633769168]
- Top2 weak hit before/after: False / False
- Classification: `unchanged`

### case_009
- Question: 搜不到蓝牙设备怎么办
- Normalized before: 蓝牙设备无法被发现设备怎么办
- Normalized after: 蓝牙设备无法被发现怎么办
- Dual before/after: True / True
- Candidates before/after: 35 / 44
- Top titles before: ['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '关于NOKIA手机通过红外线连接旭日150拨号上网的解决方案']
- Top titles after: ['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '关于NOKIA手机通过红外线连接旭日150拨号上网的解决方案']
- Scores before: [0.5351049396979934, 0.5026722549816113]
- Scores after: [0.5346016565130154, 0.5014754493385694]
- Top2 weak hit before/after: False / False
- Classification: `requires_manual_review`

### case_010
- Question: 连不上蓝牙设备怎么添加
- Normalized before: 蓝牙连接失败设备怎么添加
- Normalized after: 蓝牙连接失败怎么添加
- Dual before/after: True / True
- Candidates before/after: 39 / 40
- Top titles before: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Top titles after: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Scores before: [0.4873127870390048, 0.4728534396382682]
- Scores after: [0.4876205739251792, 0.4727344861039579]
- Top2 weak hit before/after: True / True
- Classification: `requires_manual_review`

### case_011
- Question: 电脑没声音，音量怎么调
- Normalized before: 电脑无声音，音量怎么调
- Normalized after: 电脑无声音，音量怎么调
- Dual before/after: True / True
- Candidates before/after: 26 / 26
- Top titles before: ['如何通过联想电源管理软件调整电源模式', '电脑会自动开机启动，是什么问题？']
- Top titles after: ['如何通过联想电源管理软件调整电源模式', '电脑会自动开机启动，是什么问题？']
- Scores before: [0.4600642260640116, 0.41659694797227853]
- Scores after: [0.4581206241694894, 0.41587147165802685]
- Top2 weak hit before/after: False / False
- Classification: `unchanged`

### case_012
- Question: 系统卡死没有响应怎么办
- Normalized before: 系统系统无响应没有响应怎么办
- Normalized after: 系统无响应怎么办
- Dual before/after: True / True
- Candidates before/after: 27 / 29
- Top titles before: ['电子词典LN4000操作汇总', 'Windows 2000蓝屏死机故障分析与排除']
- Top titles after: ['电子词典LN4000操作汇总', 'Windows 2000蓝屏死机故障分析与排除']
- Scores before: [0.5367050178905809, 0.5206517243986455]
- Scores after: [0.5353152144285066, 0.5196695378000058]
- Top2 weak hit before/after: False / False
- Classification: `requires_manual_review`


## No-answer Cases

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Normalized before: 火星基地打印机怎么连接量子网络
- Normalized after: 火星基地打印机怎么连接量子网络
- Dual before/after: False / False
- Candidates before/after: 28 / 28
- Top titles before: ['联想一键恢复的使用方法', '电子词典LN4000操作汇总']
- Top titles after: ['联想一键恢复的使用方法', '电子词典LN4000操作汇总']
- Scores before: [0.5811882773227754, 0.580441939741655]
- Scores after: [0.5807061824909716, 0.5789821693271096]
- Top2 weak hit before/after: False / False
- Classification: `unchanged`

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Normalized before: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Normalized after: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Dual before/after: False / False
- Candidates before/after: 25 / 25
- Top titles before: ['Windows自带电源管理（包括休眠、待机和睡眠）的设置方法', 'Windows 2000蓝屏死机故障分析与排除']
- Top titles after: ['Windows自带电源管理（包括休眠、待机和睡眠）的设置方法', 'Windows 2000蓝屏死机故障分析与排除']
- Scores before: [0.5207358518223606, 0.5131528476840912]
- Scores after: [0.5213189565079955, 0.5128259625352594]
- Top2 weak hit before/after: False / False
- Classification: `unchanged`

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Normalized before: 手机屏幕进水后如何更换折叠屏铰链
- Normalized after: 手机屏幕进水后如何更换折叠屏铰链
- Dual before/after: False / False
- Candidates before/after: 24 / 24
- Top titles before: ['在Windows XP下如何配置无线网络', '如何恢复Windows XP任务栏输入法图标']
- Top titles after: ['在Windows XP下如何配置无线网络', '如何恢复Windows XP任务栏输入法图标']
- Scores before: [0.6768102130290894, 0.6691003149094358]
- Scores after: [0.6764614752909739, 0.6663083807965813]
- Top2 weak hit before/after: False / False
- Classification: `unchanged`


## Notes

- expected_title_contains is only a weak automatic label, not final retrieval accuracy.
- requires_manual_review means title/score changes are insufficient for reliable automatic judgment.
- This comparison only analyzes report deltas and does not call external services.