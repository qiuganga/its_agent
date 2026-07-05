# RAG Retrieval Diagnosis Report

- Status: `success`
- Generated at: `2026-07-04T18:23:09`

## Summary

- Total cases: 24
- Dual retrieval count: 8
- Single retrieval count: 16
- Accepted count: 24
- Low-confidence rejected count: 0
- Classification counts: {'rerank_problem': 14, 'requires_manual_review': 24, 'chunk_quality_problem': 6, 'candidate_recall_problem': 1, 'likely_false_positive': 3}
- Correct loss statistics: {'knowledge_missing': 0, 'candidate_recall_failed': 1, 'rerank_failed': 14, 'chunk_quality_problem': 6, 'requires_manual_review': 24}

## No-answer Cases

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Rejected by low confidence: False
- Top score: 0.5825273307138562
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
  - 联想一键恢复的使用方法 | score=0.5825273307138562 | anchor=NO_ANCHOR_EVIDENCE | matched=[]
  - 电子词典LN4000操作汇总 | score=0.5798263117690505 | anchor=NO_ANCHOR_EVIDENCE | matched=[]

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Rejected by low confidence: False
- Top score: 0.5208196896740005
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
  - Windows自带电源管理（包括休眠、待机和睡眠）的设置方法 | score=0.5208196896740005 | anchor=NO_ANCHOR_EVIDENCE | matched=[]
  - Windows 2000蓝屏死机故障分析与排除 | score=0.5133315102171117 | anchor=NO_ANCHOR_EVIDENCE | matched=[]

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Rejected by low confidence: False
- Top score: 0.6762497545568469
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
  - 在Windows XP下如何配置无线网络 | score=0.6762497545568469 | anchor=NO_ANCHOR_EVIDENCE | matched=[]
  - 如何恢复Windows XP任务栏输入法图标 | score=0.6689153231690946 | anchor=NO_ANCHOR_EVIDENCE | matched=[]

## Top Suspicious Cases

- case_022 | score=0.5825273307138562 | titles=['联想一键恢复的使用方法', '电子词典LN4000操作汇总'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
- case_023 | score=0.5208196896740005 | titles=['Windows自带电源管理（包括休眠、待机和睡眠）的设置方法', 'Windows 2000蓝屏死机故障分析与排除'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
- case_024 | score=0.6762497545568469 | titles=['在Windows XP下如何配置无线网络', '如何恢复Windows XP任务栏输入法图标'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
- case_012 | score=0.536024394563095 | titles=['电子词典LN4000操作汇总', 'Windows 2000蓝屏死机故障分析与排除'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': True, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- case_001 | score=0.5798987259114792 | titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Lenovo G485无线网络连接不上的解决方案'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- case_002 | score=0.5455560006716262 | titles=['电子词典LN4000操作汇总', 'Internet Explorer版本升级说明'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- case_003 | score=0.525306757271404 | titles=['如何设置显卡的电源管理', '智能电视开不了机并且指示灯都不亮怎么办？'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- case_005 | score=0.5839253531365958 | titles=['新圆梦F系列电脑运行游戏卡', '电子词典LN4000操作汇总'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- case_006 | score=0.5827017107573725 | titles=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', 'Windows 2000蓝屏死机故障分析与排除'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- case_007 | score=0.6405305309924323 | titles=['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '电子词典LN4000操作汇总'] | classification={'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}

## Case Details

### case_001
- Original: 开不了机，屏幕不亮怎么办
- Normalized: 无法开机，黑屏怎么办
- Dual retrieval: True
- Candidates: vector=30, title=20, dedup=38
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - Excel文件菜单及相关功能灰色不可用怎么办？ | source=None | route=vector | distance=0.9267228841781616 | rerank=0.5798987259114792 | mmr=0.5798987259114792 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Excel文件菜单及相关功能灰色不可用怎么办？ **故障现象：** 在使用 Excel 的时候，发现“文件”菜单下的“新建”“打开”“保存”“打印文件”等功能都显示为灰色，无法正常使用。 **解决方案：** 我们知道对于计算机来说，所有的改动都要保存，如果不保存的话电脑是不会自动记忆用户做的改动的。Excel 也一样，虽然它没有弹出保存提示，但实际上它已经在一个文件中写下了这个改动，这个文件就是“Excelxx.xlb”。在 Excel 2010 中该文件名为 Excel14.xlb；如果是 Excel 2007，文件名则为 Excel12.xlb。 对于 Windows 7/Vis...
  - Lenovo G485无线网络连接不上的解决方案 | source=None | route=vector | distance=0.8751043081283569 | rerank=0.5595815421765659 | mmr=0.27049871440255263 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Lenovo G485无线网络连接不上的解决方案 ## 解决方案 [联想远程软件服务](https://activity.lenovo.com.cn/ecare365/index.html?&pmf_group=dj&pmf_medium=dj&pmf_source=Z00007165T000)，可远程帮您电脑加速、游戏加速、磁盘分区、重装系统、网络与浏览器修复、软件和驱动的激活、安装调试及配置优化、一对一应用指导等，让您足不出户，轻松解决电脑问题！ -------------------------------------------------------------------...

### case_002
- Original: 开机没反应怎么办
- Normalized: 无法开机怎么办
- Dual retrieval: True
- Candidates: vector=29, title=20, dedup=32
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.8952114582061768 | rerank=0.5455560006716262 | mmr=0.5455560006716262 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)
  - Internet Explorer版本升级说明 | source=None | route=vector | distance=0.9997392892837524 | rerank=0.4991972140793969 | mmr=0.2450348084257112 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Internet Explorer版本升级说明 ![](https://webdoc.lenovo.com.cn/lenovowsi/20120806/1344236192413_349.png) Windows 7、Windows Server 2008 R2： Windows 7、Windows Server 2008 R2 集成的默认版本是 IE 8，可以选择升级至 IE 9。IE 9 是惟一没有被集成在任何 Windows 中的 IE 版本，它只能在 Windows 7、Windows Server 2008 R2 中单独安装升级。 您可以通过 Windows 自动更新、Mi...

### case_003
- Original: 屏幕不亮但风扇会转，电脑黑屏怎么处理
- Normalized: 黑屏但风扇会转，电脑黑屏怎么处理
- Dual retrieval: True
- Candidates: vector=30, title=20, dedup=30
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 如何设置显卡的电源管理 | source=None | route=vector | distance=0.9404280185699463 | rerank=0.525306757271404 | mmr=0.525306757271404 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:如何设置显卡的电源管理 # 知识库 219 ## 标题 如何设置显卡的电源管理 ## 问题描述 由于驱动程序版本的不同，即使是同一显卡的设置界面也可能不同。此外，ATI显卡（即AMD显卡）在Windows XP下、Nvidia显卡在Windows 7/8下可能没有电源设置选项。那么我们如何设置显卡的电源管理呢？一起来看下本文。 ## 分类 主类别: 操作系统故障 子类别: 系统应用操作 ## 关键词 显卡, 电源管理, ATI显卡, Nvidia显卡, 电源 ## 元信息 创建时间:2024-12-15|版本:2.0
  - 智能电视开不了机并且指示灯都不亮怎么办？ | source=0192-智能电视开不了机并且指示灯都不亮怎么办？.md | route=title | distance=None | rerank=0.5195026261401393 | mmr=0.2292171402230858 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:智能电视开不了机并且指示灯都不亮怎么办？ # 知识库 192 ## 标题 智能电视开不了机并且指示灯都不亮怎么办？ ## 问题描述 智能电视开不了机并且指示灯都不亮怎么办，下面给您介绍遇到此现象怎么处理。 ## 分类 主类别: 显示相关 子类别: 黑屏 ## 关键词 联想, 智能电视, 开关, 电源, 开机 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 1、请首先确保电视机已经正确连接了电源线，并且电源插座或插孔中有电； 2、如果排除连接原因，请分别按遥控器上的电源按钮和机器右侧的电源按钮测试； 3、如仍无法开机，请联系联想客服人员上门检查。

### case_004
- Original: 开机蓝屏提示登录进程初始化失败怎么解决
- Normalized: 开机蓝屏提示登录进程初始化失败怎么解决
- Dual retrieval: False
- Candidates: vector=13, title=10, dedup=23
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': True, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 开机蓝屏或提示登录进程初始化失败问题的解决方案（Vista） | source=None | route=vector | distance=0.7580568790435791 | rerank=0.6382098105431147 | mmr=0.6382098105431147 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:开机蓝屏或提示登录进程初始化失败问题的解决方案（Vista） ## 解决方案 **故障现象：** 6月12日，部分用户在启动时出现“蓝屏”或提示“登录进程初始化失败”，无法进入桌面， Windows Vista用户，如下图。 Windows 7用户，请点击[这里](http://support1.lenovo.com.cn/lenovo/wsi/htmls/detail_1371129679703.html) Windows XP用户，请点击[这里](http://support1.lenovo.com.cn/lenovo/wsi/htmls/detail_1371130865828...
  - Windows 2000蓝屏死机故障分析与排除 | source=None | route=vector | distance=0.8078322410583496 | rerank=0.5996155947103308 | mmr=0.29537180878229996 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:Windows 2000蓝屏死机故障分析与排除 ## 解决方案 从理论上讲，纯32位的Windows 2000是不会出现[死机](/detail/kd_17517.html)的，但是这仅仅是理论上。病毒或[硬件](/detail/kd_17962.html)和硬件[驱动](/detail/kd_17488.html)程序不匹配等原因将造成Windows 2000的崩溃，当Windows 2000出现死机时，显示器屏幕将变为蓝色，然后出现STOP故障提示信息。下面我们分别介绍通用的STOP故障处理方法和特殊的STOP故障排除。 一、通用STOP故障处理 1、首先使用新版杀毒[软件](/...

### case_005
- Original: 电脑蓝屏报错0x0000007B怎么办
- Normalized: 电脑蓝屏报错0x0000007B怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 新圆梦F系列电脑运行游戏卡 | source=0076-新圆梦F系列电脑运行游戏卡.md | route=title | distance=None | rerank=0.5839253531365958 | mmr=0.5839253531365958 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:新圆梦F系列电脑运行游戏卡 # 知识库 76 ## 标题 新圆梦F系列电脑运行游戏卡 ## 问题描述 新圆梦F系列电脑运行游戏卡、不流畅，需要ikan是否达到要求配置，如果达到要求配置请根据指导操作。 ## 分类 主类别: 游戏专区 子类别: 游戏卡顿 ## 关键词 新圆梦, 运行卡, 游戏卡, 机器慢 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 1、核实您的机器硬件配置是否符合游戏官网推荐的[硬件配置](http://support.lenovo.com.cn/lenovo/wsi/htmls/detail_1376891082659.html#pe...
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.839343786239624 | rerank=0.5742013680307897 | mmr=0.2796110696293357 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)

### case_006
- Original: 无线网络连不上怎么办
- Normalized: 无线网络连不上怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？ | source=0785-联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？.md | route=title | distance=None | rerank=0.5827017107573725 | mmr=0.5827017107573725 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？ # 知识库 785 ## 标题 联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？ ## 问题描述 本文为您介绍联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵的解决办法。 ## 分类 主类别: 接口与外置设备 子类别: 鼠标 ## 关键词 联想, 无线键鼠, 失灵, 键盘, 鼠标 ## 元信息 创建时间:2024-12-15|版本:2.0 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2005-03-01/zV0VFAbLf3...
  - Windows 2000蓝屏死机故障分析与排除 | source=None | route=vector | distance=0.893308162689209 | rerank=0.5565161860070524 | mmr=0.270665765231021 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Windows 2000蓝屏死机故障分析与排除 ## 解决方案 从理论上讲，纯32位的Windows 2000是不会出现[死机](/detail/kd_17517.html)的，但是这仅仅是理论上。病毒或[硬件](/detail/kd_17962.html)和硬件[驱动](/detail/kd_17488.html)程序不匹配等原因将造成Windows 2000的崩溃，当Windows 2000出现死机时，显示器屏幕将变为蓝色，然后出现STOP故障提示信息。下面我们分别介绍通用的STOP故障处理方法和特殊的STOP故障排除。 一、通用STOP故障处理 1、首先使用新版杀毒[软件](/...

### case_007
- Original: 连不上网，怎么检查网络是否通畅
- Normalized: 无法连接网络，怎么检查网络是否通畅
- Dual retrieval: True
- Candidates: vector=30, title=20, dedup=39
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统 | source=None | route=vector | distance=0.7264096736907959 | rerank=0.6405305309924323 | mmr=0.6405305309924323 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统 ## 解决方案 **故障现象:** 开机后电源键亮屏幕卡在黑色背景屏幕，有白字报错信息。 **解决方案:** 1、首先查看屏幕报错信息,如报错S.M.A.R.T（如下图），请尽量备份自己的数据，此报错多为硬盘损坏或者异常，建议您去[联想售后服务中心](https://newsupport.lenovo.com.cn/serverNet.html)检测硬盘。 ![](https://webdoc.lenovo.com.cn/lenovowsi/20130819/1376889731271_932.jpg) 2、如果不是方案...
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.7293828725814819 | rerank=0.6327176931411613 | mmr=0.31403406853515625 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)

### case_008
- Original: 只使用电池有时找不到网络设备怎么办
- Normalized: 只使用电池有时找不到网络设备怎么办
- Dual retrieval: False
- Candidates: vector=14, title=10, dedup=24
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - Windows 2000蓝屏死机故障分析与排除 | source=None | route=vector | distance=0.7850018739700317 | rerank=0.6063672042602983 | mmr=0.6063672042602983 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Windows 2000蓝屏死机故障分析与排除 ## 解决方案 从理论上讲，纯32位的Windows 2000是不会出现[死机](/detail/kd_17517.html)的，但是这仅仅是理论上。病毒或[硬件](/detail/kd_17962.html)和硬件[驱动](/detail/kd_17488.html)程序不匹配等原因将造成Windows 2000的崩溃，当Windows 2000出现死机时，显示器屏幕将变为蓝色，然后出现STOP故障提示信息。下面我们分别介绍通用的STOP故障处理方法和特殊的STOP故障排除。 一、通用STOP故障处理 1、首先使用新版杀毒[软件](/...
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.8291946649551392 | rerank=0.5763639233320303 | mmr=0.29922708329374825 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)

### case_009
- Original: 搜不到蓝牙设备怎么办
- Normalized: 蓝牙设备无法被发现设备怎么办
- Dual retrieval: True
- Candidates: vector=30, title=24, dedup=35
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统 | source=None | route=vector | distance=0.9405757188796997 | rerank=0.5340094637825328 | mmr=0.5340094637825328 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统 ## 解决方案 **故障现象:** 开机后电源键亮屏幕卡在黑色背景屏幕，有白字报错信息。 **解决方案:** 1、首先查看屏幕报错信息,如报错S.M.A.R.T（如下图），请尽量备份自己的数据，此报错多为硬盘损坏或者异常，建议您去[联想售后服务中心](https://newsupport.lenovo.com.cn/serverNet.html)检测硬盘。 ![](https://webdoc.lenovo.com.cn/lenovowsi/20130819/1376889731271_932.jpg) 2、如果不是方案...
  - 关于NOKIA手机通过红外线连接旭日150拨号上网的解决方案 | source=None | route=vector | distance=1.002386450767517 | rerank=0.5017647305071067 | mmr=0.22896535889563055 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:关于NOKIA手机通过红外线连接旭日150拨号上网的解决方案 ## 解决方案 **问题描述：** 用户称使用NOKIA\_6210手机连接旭日150红外[端口](http://iknow.lenovo.com/knowledgeDetail.html?knowledgeId=17415)无法识别到该设备。要求核实该笔记本能否通过红外连接NOKIA手机拨号上网。用户称已经从NOKIA官方网站下载相关通讯[软件](http://iknow.lenovo.com/knowledgeDetail.html?knowledgeId=17963)。

### case_010
- Original: 连不上蓝牙设备怎么添加
- Normalized: 蓝牙连接失败设备怎么添加
- Dual retrieval: True
- Candidates: vector=30, title=26, dedup=39
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': True, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 如何添加启用蓝牙的设备 | source=None | route=vector | distance=1.0338187217712402 | rerank=0.48604375236963765 | mmr=0.48604375236963765 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:如何添加启用蓝牙的设备 # 知识库 356 ## 标题 如何添加启用蓝牙的设备 ## 问题描述 您可以将多种不同类型的蓝牙设备添加到电脑，如移动电话、无线耳机以及无线鼠标设备和键盘，该如何操作呢？一起来看下本文，里面介绍了win11、win10、win8、win7、xp系统的添加方法。 ## 分类 主类别: 内置设备 子类别: 蓝牙 ## 关键词 启用, 蓝牙, 添加, 蓝牙设备, 无线, win10添加蓝牙, win11添加蓝牙, 通过蓝牙连接手机, 添加蓝牙耳机, 添加蓝牙键盘, 添加蓝牙鼠标 ## 元信息 创建时间:2025-08-26|版本:3.0
  - 蓝牙设备在Win XP SP2操作系统下的设置与使用 | source=None | route=vector | distance=1.0866001844406128 | rerank=0.47269936697732373 | mmr=0.21081354591745982 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:蓝牙设备在Win XP SP2操作系统下的设置与使用 # 知识库 994 ## 标题 蓝牙设备在Win XP SP2操作系统下的设置与使用 ## 问题描述 蓝牙设备在Win XP SP2操作系统下的设置与使用。 ## 分类 主类别: 内置设备 子类别: 蓝牙 ## 关键词 xp, sp2, 系统, 蓝牙, 无线 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 [蓝牙](/detail/kd_17350.html)技术是目前非常常见的无线传输技术，借助Windows XP系统，我们可以轻松的实现计算机与其它蓝牙设备的数据交换。本文着重介绍如何使用蓝牙技术实现...

### case_011
- Original: 电脑没声音，音量怎么调
- Normalized: 电脑无声音，音量怎么调
- Dual retrieval: True
- Candidates: vector=30, title=20, dedup=26
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 如何通过联想电源管理软件调整电源模式 | source=None | route=vector | distance=1.074805498123169 | rerank=0.45907528208783965 | mmr=0.45907528208783965 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:如何通过联想电源管理软件调整电源模式 # 知识库 269 ## 标题 如何通过联想电源管理软件调整电源模式 ## 问题描述 本文介绍通过联想电源管理软件的不同版本调整电源模式的详细操作步骤。 ## 分类 主类别: 预装软件 子类别: 电源管理 ## 关键词 联想电源管理软件, 电源模式, 联想电源管理, thinkpad 电源管理, lenovo电源管理 ## 元信息 创建时间:2024-12-15|版本:3.0
  - 电脑会自动开机启动，是什么问题？ | source=0408-电脑会自动开机启动，是什么问题？.md | route=title | distance=None | rerank=0.4180238078123845 | mmr=0.1815339042062196 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电脑会自动开机启动，是什么问题？ # 知识库 408 ## 标题 电脑会自动开机启动，是什么问题？ ## 问题描述 有时我们会发现一个奇怪的故障，明明没有 按电源按钮，电脑却无缘无故的自动启动了，这究竟是什么故障？或者是什么功能？应该如何处理呢？ ## 分类 主类别: 内置设备 子类别: 内存 ## 关键词 自动开机, 网络唤醒, 来电唤醒, 电脑自动开机, 电脑自动开机启动问题, 电脑非正常关机, BIOS网络唤醒功能, BIOS来电唤醒功能, BIOS设置自动开机, 网络唤醒功能关闭方法, BIOS电源管理设置, 电脑正常关机操作, 来电唤醒功能禁用, 电脑开机启动问题解决, 电...

### case_012
- Original: 系统卡死没有响应怎么办
- Normalized: 系统系统无响应没有响应怎么办
- Dual retrieval: True
- Candidates: vector=28, title=20, dedup=27
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': True, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.918038010597229 | rerank=0.536024394563095 | mmr=0.536024394563095 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)
  - Windows 2000蓝屏死机故障分析与排除 | source=None | route=vector | distance=0.9608509540557861 | rerank=0.5211531183079989 | mmr=0.25797155435931485 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Windows 2000蓝屏死机故障分析与排除 ## 解决方案 从理论上讲，纯32位的Windows 2000是不会出现[死机](/detail/kd_17517.html)的，但是这仅仅是理论上。病毒或[硬件](/detail/kd_17962.html)和硬件[驱动](/detail/kd_17488.html)程序不匹配等原因将造成Windows 2000的崩溃，当Windows 2000出现死机时，显示器屏幕将变为蓝色，然后出现STOP故障提示信息。下面我们分别介绍通用的STOP故障处理方法和特殊的STOP故障排除。 一、通用STOP故障处理 1、首先使用新版杀毒[软件](/...

### case_013
- Original: 电脑运行游戏卡怎么办
- Normalized: 电脑运行游戏卡怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': True, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 联想新圆梦F系列机型运行游戏卡或无法运行的解决方案 | source=0077-联想新圆梦F系列机型运行游戏卡或无法运行的解决方案.md | route=title | distance=None | rerank=0.6087651298454675 | mmr=0.6087651298454675 | anchor=FULL_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:联想新圆梦F系列机型运行游戏卡或无法运行的解决方案 # 知识库 77 ## 标题 联想新圆梦F系列机型运行游戏卡或无法运行的解决方案 ## 问题描述 联想新圆梦F系列机型运行游戏卡或无法运行的解决方案。 ## 分类 主类别: 游戏专区 子类别: 游戏卡顿 ## 关键词 新圆梦, 游戏卡, 运行慢, 不流畅 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 **故障现象:** 新圆梦F系列运行游戏卡、不流畅。 **解决方案:** 1、核实您的新圆梦F机器硬件配置是否符合游戏官网推荐的硬件配置： （1）如果您的新圆梦F的硬件配置（比如CPU、内存、显卡等）满足游...
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.8327584862709045 | rerank=0.5818775327665604 | mmr=0.27858660775032323 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)

### case_014
- Original: Excel 文件菜单和相关功能灰色不可用怎么办
- Normalized: Excel 文件菜单和相关功能灰色不可用怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': True, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - Excel文件菜单及相关功能灰色不可用怎么办？ | source=0025-Excel文件菜单及相关功能灰色不可用怎么办？.md | route=title | distance=None | rerank=0.6273604496653787 | mmr=0.6273604496653787 | anchor=PARTIAL_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:Excel文件菜单及相关功能灰色不可用怎么办？ # 知识库 25 ## 标题 Excel文件菜单及相关功能灰色不可用怎么办？ ## 问题描述 删除自动记忆文件来解决使用 Excel 的时候，发现“文件”菜单下的“新建”“打开”“保存”“打印文件”等功能都显示为灰色，无法正常使用的问题。 ## 分类 主类别: 预装软件 子类别: Office软件 ## 关键词 Excel, 菜单, 灰色, 不可用 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 · [打开excel文件速度慢](http://support1.lenovo.com.cn/lenovo/wsi...
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.848768413066864 | rerank=0.5726849380340572 | mmr=0.2765703681336005 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)

### case_015
- Original: Word 插入的图片都变成空白框了怎么办
- Normalized: Word 插入的图片都变成空白框了怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.8092654943466187 | rerank=0.5906815114033921 | mmr=0.5906815114033921 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)
  - 单向可Ping通的原因与原理- | source=None | route=vector | distance=0.8759582042694092 | rerank=0.5653367745350291 | mmr=0.2890248841161206 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:单向可Ping通的原因与原理- ## 解决方案 当网络出现问题时，我们最常用的测试工具就是“Ping”命令了。但有时候我们会碰到单方向Ping通的现象，例如通过HUB或一根交叉线连接的在同一个局域网内的电脑A、 B，在检查它们之间的网络连通性时，发现从主机A Ping 主机B正常而从主机B Ping 主机A时，出现“超时无应答”错误。为什么呢? 要知道这其中的奥秘，我们有必要来看看Ping命令的工作过程到底是怎么样的。 假定主机A的IP地址是192.168.1.1，主机B的IP地址是192.168.1.2，都在同一子网内，则当你在主机A上运行“Ping 192.168.1.2”后，都...

### case_016
- Original: Outlook 为什么没有已发送邮件的记录
- Normalized: Outlook 为什么没有已发送邮件的记录
- Dual retrieval: False
- Candidates: vector=13, title=10, dedup=23
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': True, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 如何给某分区、光驱、U盘分配盘符 | source=None | route=vector | distance=0.9624115824699402 | rerank=0.5209935109437982 | mmr=0.5209935109437982 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:如何给某分区、光驱、U盘分配盘符 # 知识库 231 ## 标题 如何给某分区、光驱、U盘分配盘符 ## 问题描述 下面为您介绍为分区、光驱、U盘分配盘符。 ## 分类 主类别: 操作系统故障 子类别: 磁盘分区 ## 关键词 XP, 查看, IP地址, 设置, 管理, Windows, 分区, 光盘, U盘, 盘符 ## 元信息 创建时间:2024-12-15|版本:2.0
  - Outlook为何没有已发送邮件的记录- | source=0011-Outlook为何没有已发送邮件的记录-.md | route=title | distance=None | rerank=0.4905734908004148 | mmr=0.23177436912924276 | anchor=PARTIAL_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:Outlook为何没有已发送邮件的记录- # 知识库 11 ## 标题 Outlook为何没有已发送邮件的记录? ## 问题描述 Outlook没有已发送邮件的记录调整方法。 ## 分类 主类别: 预装软件 子类别: Office软件 ## 关键词 Outlook, 已发送, 邮件, 记录 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 **故障现象：**使用Outlook将邮件发送出去后，为什么在“已发送邮件”文件夹中却找不到记录？ **解决方案：**以Outlook2010为例： 请打开“**文件**”选项卡，单击“**选项**”； ![](https...

### case_017
- Original: IE 只能打开首页，其他链接打不开怎么办
- Normalized: IE 只能打开首页，其他链接打不开怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？ | source=0785-联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？.md | route=title | distance=None | rerank=0.5613529304366445 | mmr=0.5613529304366445 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？ # 知识库 785 ## 标题 联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？ ## 问题描述 本文为您介绍联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵的解决办法。 ## 分类 主类别: 接口与外置设备 子类别: 鼠标 ## 关键词 联想, 无线键鼠, 失灵, 键盘, 鼠标 ## 元信息 创建时间:2024-12-15|版本:2.0 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2005-03-01/zV0VFAbLf3...
  - Lenovo G485无线网络连接不上的解决方案 | source=None | route=vector | distance=0.9231616258621216 | rerank=0.5456580595277465 | mmr=0.26035606326587457 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Lenovo G485无线网络连接不上的解决方案 ## 解决方案 [联想远程软件服务](https://activity.lenovo.com.cn/ecare365/index.html?&pmf_group=dj&pmf_medium=dj&pmf_source=Z00007165T000)，可远程帮您电脑加速、游戏加速、磁盘分区、重装系统、网络与浏览器修复、软件和驱动的激活、安装调试及配置优化、一对一应用指导等，让您足不出户，轻松解决电脑问题！ -------------------------------------------------------------------...

### case_018
- Original: 如何使用U盘安装Windows 7操作系统
- Normalized: 如何使用U盘安装Windows 7操作系统
- Dual retrieval: False
- Candidates: vector=13, title=10, dedup=23
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 联想摄像头随机软件能否保存视频捕捉属性以及视频捕捉参数？ | source=None | route=vector | distance=0.9318643808364868 | rerank=0.48535261705404553 | mmr=0.48535261705404553 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:联想摄像头随机软件能否保存视频捕捉属性以及视频捕捉参数？ # 知识库 934 ## 标题 联想摄像头随机软件能否保存视频捕捉属性以及视频捕捉参数？ ## 问题描述 联想摄像头随机软件能否保存视频捕捉属性以及视频捕捉参数 ## 分类 主类别: 内置设备 子类别: 摄像头 ## 关键词 摄像头, 视频捕捉, 参数, 随机软件 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 在联想摄像头应用程序中进入系统设置---设备设置---[视频](http://iknow.lenovo.com/knowledgeDetail.html?knowledgeId=17880)...
  - 使用联想系统恢复光盘安装WIN98操作系统（CHM格式） | source=None | route=vector | distance=0.9319272041320801 | rerank=0.4620508214945171 | mmr=0.2172861020826978 | anchor=PARTIAL_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:使用联想系统恢复光盘安装WIN98操作系统（CHM格式） # 知识库 937 ## 标题 使用联想系统恢复光盘安装WIN98操作系统（CHM格式） ## 问题描述 使用联想系统恢复光盘安装WIN98操作系统 ## 分类 主类别: 操作系统故障 子类别: 系统安装与升级 ## 关键词 系统恢复, 光盘, 操作系统, win98 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 使用联想系统恢复光盘安装WIN98操作系统（CHM格式）。 附件：[安装画面详解.chm](https://webdoc.lenovo.com.cn/lenovowsi/cskb/dat...

### case_019
- Original: 手机或平板电脑无法访问百度相关网站怎么办
- Normalized: 手机或平板电脑无法访问百度相关网站怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': True, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.7373387217521667 | rerank=0.6320887180081294 | mmr=0.6320887180081294 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)
  - 手机或平板电脑无法访问百度相关网站的解决办法 | source=0100-手机或平板电脑无法访问百度相关网站的解决办法.md | route=title | distance=None | rerank=0.6133401381925689 | mmr=0.3217299827271589 | anchor=FULL_ANCHOR_EVIDENCE | expected_title_hit=True
    Summary: 文档来源:手机或平板电脑无法访问百度相关网站的解决办法 # 知识库 100 ## 标题 手机或平板电脑无法访问百度相关网站的解决办法 ## 问题描述 当您使用手机或者平板电脑内置的网页浏览器上网时，如果出现这样的情况：无法访问百度相关网站（比如m.baidu.com）并一直提示“网络连接错误”，但访问其他网站时一切正常。下文将针对这种情况给出解决方案。 ## 分类 主类别: 网络问题 子类别: 网页相关 ## 关键词 手机, 平板, 上网, 百度 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 当您使用手机或者平板电脑内置的网页浏览器上网时，如果出现这样的情况：无法...

### case_020
- Original: 屏幕保护怎么关闭或取消
- Normalized: 屏幕保护怎么关闭或取消
- Dual retrieval: False
- Candidates: vector=14, title=12, dedup=26
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 改善手机或平板机身发热的办法 | source=None | route=vector | distance=0.8375248908996582 | rerank=0.5836920080380665 | mmr=0.5836920080380665 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:改善手机或平板机身发热的办法 # 知识库 108 ## 标题 改善手机或平板机身发热的办法 ## 问题描述 手机或者平板发热一直是一大难题，下面将指导如何通过更改手机设置来达到减少发热的情况。 ## 分类 主类别: 内置设备 子类别: 主板 ## 关键词 手机, 平板, 发热, 烫 ## 元信息 创建时间:2024-12-15|版本:1.0
  - 如何在任务栏显示或隐藏电池图标 | source=0336-如何在任务栏显示或隐藏电池图标.md | route=title | distance=None | rerank=0.5403396611664463 | mmr=0.2477760468097372 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:如何在任务栏显示或隐藏电池图标 # 知识库 336 ## 标题 如何在任务栏显示或隐藏电池图标 ## 问题描述 Windows 7、Windows 8、XP系统下载任务栏显示或隐藏电池图标的操作步骤。 ## 分类 主类别: 内置设备 子类别: 电池 ## 关键词 任务栏, 显示, 隐藏, 电池图标 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 **[Windows 7](/detail/kd_17984.html)、[Windows 8](/detail/kd_17985.html) [Windows XP](#XP)** **一、Windows 7、W...

### case_021
- Original: 风扇声音大但电脑能正常开机怎么办
- Normalized: 风扇声音大但电脑能正常开机怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': True, 'chunk_quality_problem': False, 'likely_false_positive': False, 'requires_manual_review': True}
- Final TopK before threshold:
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.8459506630897522 | rerank=0.5756115607864998 | mmr=0.5756115607864998 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)
  - 智能电视开不了机并且指示灯都不亮怎么办？ | source=0192-智能电视开不了机并且指示灯都不亮怎么办？.md | route=title | distance=None | rerank=0.5673856539664912 | mmr=0.27468938420329136 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:智能电视开不了机并且指示灯都不亮怎么办？ # 知识库 192 ## 标题 智能电视开不了机并且指示灯都不亮怎么办？ ## 问题描述 智能电视开不了机并且指示灯都不亮怎么办，下面给您介绍遇到此现象怎么处理。 ## 分类 主类别: 显示相关 子类别: 黑屏 ## 关键词 联想, 智能电视, 开关, 电源, 开机 ## 元信息 创建时间:2024-12-15|版本:1.0 ## 解决方案 1、请首先确保电视机已经正确连接了电源线，并且电源插座或插孔中有电； 2、如果排除连接原因，请分别按遥控器上的电源按钮和机器右侧的电源按钮测试； 3、如仍无法开机，请联系联想客服人员上门检查。

### case_022
- Original: 火星基地打印机怎么连接量子网络
- Normalized: 火星基地打印机怎么连接量子网络
- Dual retrieval: False
- Candidates: vector=14, title=14, dedup=28
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
- Final TopK before threshold:
  - 联想一键恢复的使用方法 | source=None | route=vector | distance=0.84909987449646 | rerank=0.5825273307138562 | mmr=0.5825273307138562 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:联想一键恢复的使用方法 也可以选择从用户备份恢复。 备份文件是在备份系统时选择的位置，默认是保存在D盘。 如下图： ![](https://webdoc.lenovo.com.cn/lenovowsi/new_cskb/uploadfile/20131230113531008.png) 若修改过路径，可以选择您选择的路径： ![](https://webdoc.lenovo.com.cn/lenovowsi/new_cskb/uploadfile/20131230113532009.png) 从用户备份： ![](https://webdoc.lenovo.com.cn/lenovo...
  - 电子词典LN4000操作汇总 | source=None | route=vector | distance=0.8500452637672424 | rerank=0.5798263117690505 | mmr=0.28304166507857725 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:电子词典LN4000操作汇总 ## 解决方案 ![](https://webdoc.lenovo.com.cn/lenovowsi/uploadimages/2004-09-22/0Cj36N3Q6UrErzf4.jpg)

### case_023
- Original: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Normalized: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Dual retrieval: False
- Candidates: vector=15, title=10, dedup=25
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
- Final TopK before threshold:
  - Windows自带电源管理（包括休眠、待机和睡眠）的设置方法 | source=None | route=vector | distance=0.9639943242073059 | rerank=0.5208196896740005 | mmr=0.5208196896740005 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Windows自带电源管理（包括休眠、待机和睡眠）的设置方法 ### Windows XP操作系统中，自带电源管理（包括休眠、待机和睡眠）的设置方法： Windows XP操作系统中，点击“**开始**”---“**控制面板**”---“**性能和维护**”---“**电源选项**”，即可打开系统自带的电源管理窗口。分别的选项有：“**电源使用方案**”、“**报警**”、“**电表**”、“**高级**”、“**休眠**”。如果希望选择不同的电源方案，可以选择“**电源使用方案**”的下拉菜单选择需要的方案。下面有各自的具体设置，可以修改成需要的设置，也可以另存为自己定制的电源方案...
  - Windows 2000蓝屏死机故障分析与排除 | source=None | route=vector | distance=0.983170747756958 | rerank=0.5133315102171117 | mmr=0.22450722765638426 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:Windows 2000蓝屏死机故障分析与排除 ## 解决方案 从理论上讲，纯32位的Windows 2000是不会出现[死机](/detail/kd_17517.html)的，但是这仅仅是理论上。病毒或[硬件](/detail/kd_17962.html)和硬件[驱动](/detail/kd_17488.html)程序不匹配等原因将造成Windows 2000的崩溃，当Windows 2000出现死机时，显示器屏幕将变为蓝色，然后出现STOP故障提示信息。下面我们分别介绍通用的STOP故障处理方法和特殊的STOP故障排除。 一、通用STOP故障处理 1、首先使用新版杀毒[软件](/...

### case_024
- Original: 手机屏幕进水后如何更换折叠屏铰链
- Normalized: 手机屏幕进水后如何更换折叠屏铰链
- Dual retrieval: False
- Candidates: vector=14, title=10, dedup=24
- Classification: {'likely_no_knowledge': False, 'candidate_recall_problem': False, 'rerank_problem': False, 'chunk_quality_problem': False, 'likely_false_positive': True, 'requires_manual_review': True}
- Final TopK before threshold:
  - 在Windows XP下如何配置无线网络 | source=None | route=vector | distance=0.7194023132324219 | rerank=0.6762497545568469 | mmr=0.6762497545568469 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:在Windows XP下如何配置无线网络 ![](http://robotrs.lenovo.com.cn/ZmptY2NtYW5hZ2Vy/p4data/Rdata/Rfiles/307.files/image028.jpg) 9、AccessConnections开始连接无线网络； ![](http://robotrs.lenovo.com.cn/ZmptY2NtYW5hZ2Vy/p4data/Rdata/Rfiles/307.files/image030.jpg) ![](http://robotrs.lenovo.com.cn/ZmptY2NtYW5hZ2Vy/p4data/...
  - 如何恢复Windows XP任务栏输入法图标 | source=None | route=vector | distance=0.7144526839256287 | rerank=0.6689153231690946 | mmr=0.28016637135670847 | anchor=NO_ANCHOR_EVIDENCE | expected_title_hit=False
    Summary: 文档来源:如何恢复Windows XP任务栏输入法图标 ![](https://chinakb.lenovo.com.cn/chinakb/prod-api/file/downloadFile?key=uniko/IMAGE/7e344dde95170e83d5a345c4df418ee0-1714295845202.png&name=mceclip7.png) ![](https://chinakb.lenovo.com.cn/chinakb/prod-api/file/downloadFile?key=uniko/IMAGE/f50e462b4236d80aea69c15b6a435673...

## Recommended Next Steps

1. Add anchor-based rejection or down-ranking for expected no-answer style queries.
2. Manually inspect candidate recall failures before changing thresholds.
3. Improve chunk boundaries for cases where title is correct but anchor evidence is partial.
4. Consider increasing candidate pools only if correct documents are absent from candidates.
5. Consider a stronger Cross-Encoder reranker if correct candidates enter the pool but lose final TopK.