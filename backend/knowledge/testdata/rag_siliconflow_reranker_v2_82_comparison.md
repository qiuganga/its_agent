# SiliconFlow Reranker A/B Comparison

- Generated at: `2026-07-06T16:56:00`
- Baseline: `backend\knowledge\testdata\rag_eval_report_v2_82_hsn_bm25_experimental.json`
- Experiment: `backend\knowledge\testdata\rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker.json`

## Metrics

- top1_title_weak_hit_delta: 26
- top2_title_weak_hit_delta: 23
- expected_answer_false_rejected_delta: 11
- expected_no_answer_anchor_rejected_delta: -7
- expected_no_answer_still_accepted_delta: -13
- top2_changed_count: 79
- bm25_added_to_top2_count: 71
- reranker_latency_avg_ms: 3309.5853658536585
- reranker_latency_p95_ms: 5814.0
- reranker_success_count: 82
- reranker_failure_count: 0
- reranker_invalid_result_count: 0

## Classification Counts

- RERANKER_IMPROVED: 24
- NEEDS_MANUAL_REVIEW: 54
- RERANKER_REGRESSION: 1
- RERANKER_NO_EFFECT: 3

## Focus Cases

### case_001
- Question: 开不了机，屏幕不亮怎么办
- Candidate count: 52
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Reranker Top2: ['智能电视开不了机并且指示灯都不亮怎么办？', '开机之后无任何反应怎么办？']

### case_004
- Question: 开机蓝屏提示登录进程初始化失败怎么解决
- Candidate count: 35
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['Windows XP 关机故障', '智能电视在观看过程中出现了花屏是什么原因？']
- Reranker Top2: ['开机蓝屏或提示登录进程初始化失败问题的解决方案（Vista）', '开机蓝屏或提示登录进程初始化失败问题的解决方案（XP）']

### case_005
- Question: 电脑蓝屏报错0x0000007B怎么办
- Candidate count: 34
- Classification: `RERANKER_NO_EFFECT`
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', 'Windows 2000蓝屏死机故障分析与排除']
- Reranker Top2: ['台式和一体机蓝屏报错代码：0x0000007B', 'Windows 2000蓝屏死机故障分析与排除']

### case_006
- Question: 无线网络连不上怎么办
- Candidate count: 33
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- Reranker Top2: ['手动添加无线网络方法', '在Windows 8下连接无线网络']

### case_007
- Question: 连不上网，怎么检查网络是否通畅
- Candidate count: 48
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['Windows XP 关机故障', 'WPS Office中如何打印稿纸']
- Reranker Top2: ['在Windows 7下如何检查判断网络是否通畅', '在Windows 8系统下如何检查网络连接']

### case_009
- Question: 搜不到蓝牙设备怎么办
- Candidate count: 50
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Reranker Top2: ['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']

### case_010
- Question: 连不上蓝牙设备怎么添加
- Candidate count: 53
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Reranker Top2: ['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']

### case_011
- Question: 电脑没声音，音量怎么调
- Candidate count: 36
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？']
- Reranker Top2: ['Windows XP下如何调节音量大小', '如何调整合成器内应用程序音量控制']

### case_012
- Question: 系统卡死没有响应怎么办
- Candidate count: 42
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动']
- Reranker Top2: ['开机之后无任何反应怎么办？', '联想手机K900常见问题汇总']

### case_014
- Question: Excel 文件菜单和相关功能灰色不可用怎么办
- Candidate count: 34
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Reranker Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '暴风影音的DLNA功能怎么用']

### case_015
- Question: Word 插入的图片都变成空白框了怎么办
- Candidate count: 34
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Reranker Top2: ['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '如何观看SD卡、U盘及移动硬盘中的文件']

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Candidate count: 39
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Reranker Top2: ['在Windows 8系统下如何查看网络IP地址', '如何安装网络打印机（XP Win7 Win8）']

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Candidate count: 35
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Reranker Top2: ['宽带连接频繁掉线', '联想台式机模式转换功能介绍']

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Candidate count: 35
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Reranker Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '如何用一个手机号注册多个微信帐号']

### case_025
- Question: PowerPoint 2007 cannot input Chinese
- Candidate count: 37
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['ET960如何启动“照相机”软件的方法及“照相机”软件功能按键说明-', 'Windows 2000蓝屏死机故障分析与排除']
- Reranker Top2: ['在 PowerPoint 2007 中无法输入中文怎么办？', '在Lync中如何共享桌面、ppt等？']

### case_026
- Question: How to modify Microsoft Word default style
- Candidate count: 41
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['Windows 8.1 Update （KB2919355）常见问题', '联想手机如何在桌面上添加文件夹']
- Reranker Top2: ['如何修改 Microsoft Word 的默认样式？', 'Intel SE7501HG2 服务器主板的故障代码。']

### case_027
- Question: Outlook paragraph marks should be hidden
- Candidate count: 34
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '万全T168板载SATA RAID系统设置']
- Reranker Top2: ['如何去掉Outlook中的段落标记等符号-', '联想支持Windows 10系统升级的机型列表']

### case_030
- Question: Excel shows #VALUE! error
- Candidate count: 35
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['联想支持Windows 10系统升级的机型列表', '同禧有内置音箱的机型如何屏蔽内置音箱']
- Reranker Top2: ['如何解决 Excel 显示 #VALUE! 错误信息的问题-', 'Excel表导入 Access 2010 后时间显示错误怎么办-']

### case_039
- Question: How to turn on Bluetooth module
- Candidate count: 39
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['S620充电时充电指示灯为常绿并伴有橙色闪烁', '屏幕保护功能介绍以及不同系统下如何设置或取消屏幕保护（屏保）功能']
- Reranker Top2: ['如何添加启用蓝牙的设备', 'Intel SE7501HG2 服务器主板的故障代码。']

### case_040
- Question: How to add Bluetooth device
- Candidate count: 34
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['没有并口的笔记本如何接加密狗等并口设备？', 'Intel SE7501HG2 服务器主板的故障代码。']
- Reranker Top2: ['如何添加启用蓝牙的设备', 'Intel SE7501HG2 服务器主板的故障代码。']

### case_069
- Question: Wi-Fi cannot connect, not wireless keyboard mouse
- Candidate count: 37
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '如何解决IE浏览器只能打开首页无法打开其他链接故障']
- Reranker Top2: ['Lenovo G485无线网络连接不上的解决方案', '联想支持Windows 10系统升级的机型列表']

### case_070
- Question: Wireless keyboard and mouse suddenly fail, not Wi-Fi
- Candidate count: 36
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- Reranker Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', 'DPSD 865PE主板的商用机型如何设置开机密码及BIOS密码？']

### case_071
- Question: Word inserted pictures become blank boxes, not black screen
- Candidate count: 44
- Classification: `RERANKER_IMPROVED`
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '如何在WINDOWS 2000SERVER下安装T168-T468的USB2.0驱动？']
- Reranker Top2: ['为什么 Word 2010-2007 中插入的图片都变成空白框了？', 'DPSD 865PE主板的商用机型如何设置开机密码及BIOS密码？']

### case_072
- Question: Screen brightness is too low, not Word blank picture
- Candidate count: 39
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '联想支持Windows 10系统升级的机型列表']
- Reranker Top2: ['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '在按下键盘上取消CapsLock,NumLock,ScrLock声音']

### case_074
- Question: Bluetooth device cannot be found, not infrared or Wi-Fi
- Candidate count: 40
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '如何解决IE浏览器只能打开首页无法打开其他链接故障']
- Reranker Top2: ['如何添加启用蓝牙的设备', '联想支持Windows 10系统升级的机型列表']

### case_080
- Question: Taskbar input method icon disappeared, not Word input issue
- Candidate count: 45
- Classification: `NEEDS_MANUAL_REVIEW`
- Baseline Top2: ['在联系人窗口中怎样查看SIM卡上的号码？', '联想支持Windows 10系统升级的机型列表']
- Reranker Top2: ['在联系人窗口中怎样查看SIM卡上的号码？', 'DPSD 865PE主板的商用机型如何设置开机密码及BIOS密码？']
