# RAG Retrieval Evaluation Report

- Status: `success`
- Generated at: `2026-07-06T21:43:53`

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
- RAG_BM25_MODE: experimental
- RAG_BM25_CANDIDATE_TOP_K: 10
- RAG_RERANKER_MODE: experimental
- RAG_RERANKER_PROVIDER: siliconflow
- RAG_RERANKER_MODEL: Qwen/Qwen3-Reranker-8B
- RAG_RERANKER_MAX_DOCUMENT_CHARS: 4000

## Summary

- Total cases: 82
- Normalization triggered: 24
- Normalization not triggered: 58
- Accepted with final docs: 45
- Low-confidence rejected: 35
- Top1 title weak hit: 37 (0.4512)
- Top2 title weak hit: 38 (0.4634)
- Expected no-answer correctly rejected: 21
- Expected no-answer anchor rejected: 2
- Expected no-answer not rejected: 0
- Expected-answer false rejected: 14
- Strong anchor cases: 55
- Hard anchor cases: 18
- Soft anchor cases: 39
- Negative anchor cases: 5
- No anchor cases: 33
- Hard evidence outside TopK: 0
- Negative anchor penalties: 2
- ANCHOR_EVIDENCE_MISSING: 2
- BM25 mode: experimental
- BM25 candidates: 939
- BM25 unique additions: 718
- BM25/vector overlap: 40 (0.0426)
- BM25/title overlap: 0 (0.0)
- Reranker mode: experimental
- Reranker provider: siliconflow
- Reranker model: Qwen/Qwen3-Reranker-8B
- Reranker success/failure: 82/0
- Reranker invalid results: 0
- Reranker latency avg/P95 ms: 3385.0365853658536/5928.0
- Missing source_id before rerank: 0

## Group Metrics

- C_generic_answerable: total=18, top1=7, top2=8, false_rejected=8, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=10
- A_anchor_answerable: total=26, top1=24, top2=24, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=2
- E_confusing: total=15, top1=6, top2=6, false_rejected=6, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0, manual_review=9
- B_anchor_unanswerable: total=15, top1=0, top2=0, false_rejected=0, no_answer_rejected=15, no_answer_accepted=0, anchor_missing=2, manual_review=0
- D_generic_unanswerable: total=8, top1=0, top2=0, false_rejected=0, no_answer_rejected=8, no_answer_accepted=0, anchor_missing=0, manual_review=0

## A/B Comparison

- Positive: 0
- Neutral: 0
- Changed: 0
- Negative: 0

## Score Buckets

- >=0.50: 47
- <0.25: 32
- 0.25-0.35: 3

## Threshold Recommendation

- Recommendation: `consider_lowering_to_0.30`
- Possible false rejections: ['case_003', 'case_012', 'case_021', 'case_053', 'case_055', 'case_056', 'case_057', 'case_058', 'case_059', 'case_060', 'case_069', 'case_070', 'case_079', 'case_080']
- Expected no-answer not rejected: []
- Passed but title weak miss: ['case_039', 'case_040', 'case_072', 'case_074', 'case_077', 'case_081', 'case_082']

## Suspicious Cases

- case_003: score=0.04669211432337761, rejected=True, reason=['expected_answer_rejected', 'top2_title_weak_miss'], top_titles=['关于扬天机型安装XP SP2黑屏问题', '暴风影音的DLNA功能怎么用']
- case_012: score=0.04483794793486595, rejected=True, reason=['expected_answer_rejected', 'top2_title_weak_miss'], top_titles=['开机之后无任何反应怎么办？', '联想手机K900常见问题汇总']
- case_021: score=0.2642159163951874, rejected=True, reason=['expected_answer_rejected', 'top2_title_weak_miss'], top_titles=['风扇除尘功能说明：联想电源管理V1.0、V7.0、V8.0及早期机型除尘说明', '联想ET960电脑手机每次复位或者冷启动后，关闭视频声音或者不播放视频？']
- case_039: score=0.9960352778434753, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何开启蓝牙模块功能', '如何添加启用蓝牙的设备']
- case_040: score=0.9972304701805115, rejected=False, reason=['top2_title_weak_miss'], top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']

## Case Details

- case_001 | dual=True | rejected=False | anchor_rejected=False | score=0.8104326725006104 | bm25=20 unique=15 | top_titles=['智能电视开不了机并且指示灯都不亮怎么办？', '开机之后无任何反应怎么办？']
- case_002 | dual=True | rejected=False | anchor_rejected=False | score=0.9965745210647583 | bm25=20 unique=13 | top_titles=['开机之后无任何反应怎么办？', '联想手机S680不能开机如何解决']
- case_003 | dual=True | rejected=True | anchor_rejected=False | score=0.04669211432337761 | bm25=20 unique=10 | top_titles=[]
- case_004 | dual=False | rejected=False | anchor_rejected=False | score=0.9992350339889526 | bm25=10 unique=10 | top_titles=['开机蓝屏或提示登录进程初始化失败问题的解决方案（Vista）', '开机蓝屏或提示登录进程初始化失败问题的解决方案（XP）']
- case_005 | dual=False | rejected=False | anchor_rejected=False | score=0.9973286390304565 | bm25=10 unique=9 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Windows 2000蓝屏死机故障分析与排除']
- case_006 | dual=True | rejected=False | anchor_rejected=False | score=0.8807100057601929 | bm25=20 unique=16 | top_titles=['手动添加无线网络方法', '在Windows 8下连接无线网络']
- case_007 | dual=True | rejected=False | anchor_rejected=False | score=0.9959467053413391 | bm25=20 unique=13 | top_titles=['在Windows 7下如何检查判断网络是否通畅', '在Windows 8系统下如何检查网络连接']
- case_008 | dual=False | rejected=False | anchor_rejected=False | score=0.9995811581611633 | bm25=10 unique=9 | top_titles=['昭阳K43 E43系列机型只使用电池有时找不到网络设备的解决方法', 'Visio 2010-2007 形状面板不见了怎么办？']
- case_009 | dual=True | rejected=False | anchor_rejected=False | score=0.7716514468193054 | bm25=20 unique=10 | top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- case_010 | dual=True | rejected=False | anchor_rejected=False | score=0.9873566627502441 | bm25=20 unique=11 | top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- case_011 | dual=True | rejected=False | anchor_rejected=False | score=0.7668894529342651 | bm25=20 unique=10 | top_titles=['Windows XP下如何调节音量大小', '如何调整合成器内应用程序音量控制']
- case_012 | dual=True | rejected=True | anchor_rejected=False | score=0.04483794793486595 | bm25=20 unique=12 | top_titles=[]
- case_013 | dual=False | rejected=False | anchor_rejected=False | score=0.9892235994338989 | bm25=10 unique=8 | top_titles=['新圆梦F系列电脑运行游戏卡', '联想新圆梦F系列机型运行游戏卡或无法运行的解决方案']
- case_014 | dual=False | rejected=False | anchor_rejected=False | score=0.9990077614784241 | bm25=10 unique=9 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', '暴风影音的DLNA功能怎么用']
- case_015 | dual=False | rejected=False | anchor_rejected=False | score=0.9981591105461121 | bm25=10 unique=9 | top_titles=['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '如何观看SD卡、U盘及移动硬盘中的文件']
- case_016 | dual=False | rejected=False | anchor_rejected=False | score=0.9990440011024475 | bm25=10 unique=9 | top_titles=['Outlook为何没有已发送邮件的记录-', 'Outlook下我如何查看我的对话历史记录？']
- case_017 | dual=False | rejected=False | anchor_rejected=False | score=0.9995367527008057 | bm25=10 unique=10 | top_titles=['如何解决IE浏览器只能打开首页无法打开其他链接故障', 'QQ可以登录但网页打不开或者很慢']
- case_018 | dual=False | rejected=False | anchor_rejected=False | score=0.9994049072265625 | bm25=10 unique=10 | top_titles=['如何使用U盘安装Windows 7操作系统', 'Windows操作系统安装、改装、升级的操作指导汇总']
- case_019 | dual=False | rejected=False | anchor_rejected=False | score=0.9987602233886719 | bm25=10 unique=8 | top_titles=['手机或平板电脑无法访问百度相关网站的解决办法', '12306网站打不开怎么办']
- case_020 | dual=False | rejected=False | anchor_rejected=False | score=0.9857035279273987 | bm25=10 unique=10 | top_titles=['屏幕保护功能介绍以及不同系统下如何设置或取消屏幕保护（屏保）功能', '如何设置或禁用Windows Media Player播放时允许运行屏幕保护程序']
- case_021 | dual=False | rejected=True | anchor_rejected=False | score=0.2642159163951874 | bm25=10 unique=9 | top_titles=[]
- case_022 | dual=False | rejected=True | anchor_rejected=False | score=0.029760189354419708 | bm25=10 unique=10 | top_titles=[]
- case_023 | dual=False | rejected=True | anchor_rejected=False | score=0.33016154170036316 | bm25=10 unique=10 | top_titles=[]
- case_024 | dual=False | rejected=True | anchor_rejected=False | score=1.3105967809678987e-05 | bm25=10 unique=10 | top_titles=[]
- case_025 | dual=False | rejected=False | anchor_rejected=False | score=0.9993745684623718 | bm25=10 unique=10 | top_titles=['在 PowerPoint 2007 中无法输入中文怎么办？', '在Lync中如何共享桌面、ppt等？']
- case_026 | dual=False | rejected=False | anchor_rejected=False | score=0.9993010759353638 | bm25=10 unique=10 | top_titles=['如何修改 Microsoft Word 的默认样式？', 'Intel SE7501HG2 服务器主板的故障代码。']
- case_027 | dual=False | rejected=False | anchor_rejected=False | score=0.999398946762085 | bm25=7 unique=7 | top_titles=['如何去掉Outlook中的段落标记等符号-', '联想支持Windows 10系统升级的机型列表']
- case_028 | dual=False | rejected=False | anchor_rejected=False | score=0.9995654225349426 | bm25=10 unique=9 | top_titles=['Outlook为何没有已发送邮件的记录-', 'Outlook下我如何查看我的对话历史记录？']
- case_029 | dual=False | rejected=False | anchor_rejected=False | score=0.9990803003311157 | bm25=10 unique=10 | top_titles=['Visio 2010-2007 形状面板不见了怎么办？', '如何将 Visio 2010-2007 时间表更改为垂直方向？']
- case_030 | dual=False | rejected=False | anchor_rejected=False | score=0.991992175579071 | bm25=10 unique=10 | top_titles=['如何解决 Excel 显示 #VALUE! 错误信息的问题-', 'Excel表导入 Access 2010 后时间显示错误怎么办-']
- case_031 | dual=False | rejected=False | anchor_rejected=False | score=0.9993595480918884 | bm25=10 unique=9 | top_titles=['Windows 7 开机提示group policy client 服务器未登录', '如何卸载Windows 7的无线网卡设备驱动程序']
- case_032 | dual=False | rejected=False | anchor_rejected=False | score=0.9982255101203918 | bm25=10 unique=6 | top_titles=['Lenovo G485无线网络连接不上的解决方案', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”']
- case_033 | dual=False | rejected=False | anchor_rejected=False | score=0.9989240765571594 | bm25=10 unique=10 | top_titles=['如何通过应用商店升级到Windows 8.1', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”']
- case_034 | dual=False | rejected=False | anchor_rejected=False | score=0.9992307424545288 | bm25=10 unique=10 | top_titles=['BIOS中如何关闭指纹识别并再次开启', '联想支持Windows 10系统升级的机型列表']
- case_035 | dual=False | rejected=False | anchor_rejected=False | score=0.9986005425453186 | bm25=10 unique=10 | top_titles=['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '联想G470笔记本亮度无法调节的解决方案']
- case_036 | dual=False | rejected=False | anchor_rejected=False | score=0.9997244477272034 | bm25=10 unique=10 | top_titles=['Lenovo G485 USB3.0驱动程序安装不上的解决方法', '驱动查找、下载、安装及相关问题操作指导汇总']
- case_037 | dual=False | rejected=False | anchor_rejected=False | score=0.999302864074707 | bm25=10 unique=10 | top_titles=['如何启动到Windows XP的安全模式', '如何安装和使用 Windows XP 的故障恢复控制台']
- case_038 | dual=False | rejected=False | anchor_rejected=False | score=0.991723358631134 | bm25=10 unique=10 | top_titles=['Windows 7下如何建立无线局域网', '如何卸载Windows 7的无线网卡设备驱动程序']
- case_039 | dual=True | rejected=False | anchor_rejected=False | score=0.9960352778434753 | bm25=20 unique=13 | top_titles=['如何开启蓝牙模块功能', '如何添加启用蓝牙的设备']
- case_040 | dual=True | rejected=False | anchor_rejected=False | score=0.9972304701805115 | bm25=20 unique=12 | top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- case_041 | dual=True | rejected=True | anchor_rejected=False | score=0.0004099231446161866 | bm25=20 unique=15 | top_titles=[]
- case_042 | dual=False | rejected=True | anchor_rejected=False | score=4.0432387322653085e-05 | bm25=10 unique=10 | top_titles=[]
- case_043 | dual=False | rejected=True | anchor_rejected=False | score=2.18819022848038e-05 | bm25=1 unique=1 | top_titles=[]
- case_044 | dual=False | rejected=False | anchor_rejected=True | score=0.8365944027900696 | bm25=8 unique=8 | top_titles=[]
- case_045 | dual=False | rejected=True | anchor_rejected=False | score=0.24541260302066803 | bm25=10 unique=9 | top_titles=[]
- case_046 | dual=False | rejected=True | anchor_rejected=False | score=9.0855683083646e-06 | bm25=10 unique=10 | top_titles=[]
- case_047 | dual=False | rejected=True | anchor_rejected=False | score=3.872830347972922e-05 | bm25=3 unique=3 | top_titles=[]
- case_048 | dual=False | rejected=True | anchor_rejected=False | score=2.4215731173171662e-05 | bm25=0 unique=0 | top_titles=[]
- case_049 | dual=False | rejected=False | anchor_rejected=True | score=0.5271429419517517 | bm25=10 unique=8 | top_titles=[]
- case_050 | dual=False | rejected=True | anchor_rejected=False | score=0.08413786441087723 | bm25=6 unique=6 | top_titles=[]
- case_051 | dual=False | rejected=True | anchor_rejected=False | score=8.975753735285252e-05 | bm25=10 unique=10 | top_titles=[]
- case_052 | dual=False | rejected=True | anchor_rejected=False | score=0.00012253942259121686 | bm25=3 unique=3 | top_titles=[]
- case_053 | dual=False | rejected=True | anchor_rejected=False | score=0.033715542405843735 | bm25=10 unique=9 | top_titles=[]
- case_054 | dual=False | rejected=False | anchor_rejected=False | score=0.9988880753517151 | bm25=10 unique=10 | top_titles=['设置正确的DNS解决上网慢下驱动慢的问题', '如何解决ASDL上网慢的故障']
- case_055 | dual=False | rejected=True | anchor_rejected=False | score=0.00017610892246011645 | bm25=1 unique=1 | top_titles=[]
- case_056 | dual=False | rejected=True | anchor_rejected=False | score=0.0008231346728280187 | bm25=9 unique=9 | top_titles=[]
- case_057 | dual=False | rejected=True | anchor_rejected=False | score=0.0006182831129990518 | bm25=3 unique=3 | top_titles=[]
- case_058 | dual=False | rejected=True | anchor_rejected=False | score=0.20863202214241028 | bm25=2 unique=2 | top_titles=[]
- case_059 | dual=False | rejected=True | anchor_rejected=False | score=0.00527142034843564 | bm25=9 unique=9 | top_titles=[]
- case_060 | dual=False | rejected=True | anchor_rejected=False | score=0.010156745091080666 | bm25=5 unique=5 | top_titles=[]
- case_061 | dual=False | rejected=True | anchor_rejected=False | score=8.56065089465119e-05 | bm25=10 unique=10 | top_titles=[]
- case_062 | dual=False | rejected=True | anchor_rejected=False | score=6.284398295974825e-06 | bm25=0 unique=0 | top_titles=[]
- case_063 | dual=False | rejected=True | anchor_rejected=False | score=1.415171027474571e-05 | bm25=7 unique=7 | top_titles=[]
- case_064 | dual=False | rejected=True | anchor_rejected=False | score=1.2608388715307228e-05 | bm25=2 unique=2 | top_titles=[]
- case_065 | dual=False | rejected=True | anchor_rejected=False | score=1.0691980605770368e-05 | bm25=1 unique=1 | top_titles=[]
- case_066 | dual=False | rejected=True | anchor_rejected=False | score=9.539927123114467e-05 | bm25=1 unique=1 | top_titles=[]
- case_067 | dual=False | rejected=True | anchor_rejected=False | score=0.0018840179545804858 | bm25=6 unique=6 | top_titles=[]
- case_068 | dual=False | rejected=True | anchor_rejected=False | score=8.467365842079744e-05 | bm25=9 unique=8 | top_titles=[]
- case_069 | dual=True | rejected=True | anchor_rejected=False | score=0.26697680354118347 | bm25=16 unique=8 | top_titles=[]
- case_070 | dual=True | rejected=True | anchor_rejected=False | score=2.0162298824288882e-05 | bm25=20 unique=10 | top_titles=[]
- case_071 | dual=True | rejected=False | anchor_rejected=False | score=0.9974823594093323 | bm25=20 unique=10 | top_titles=['为什么 Word 2010-2007 中插入的图片都变成空白框了？', 'DPSD 865PE主板的商用机型如何设置开机密码及BIOS密码？']
- case_072 | dual=True | rejected=False | anchor_rejected=False | score=0.9872877597808838 | bm25=20 unique=10 | top_titles=['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '在按下键盘上取消CapsLock,NumLock,ScrLock声音']
- case_073 | dual=True | rejected=False | anchor_rejected=False | score=0.9972729086875916 | bm25=20 unique=12 | top_titles=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Internet Explorer版本升级说明']
- case_074 | dual=True | rejected=False | anchor_rejected=False | score=0.5429884791374207 | bm25=20 unique=16 | top_titles=['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- case_075 | dual=True | rejected=False | anchor_rejected=False | score=0.9988823533058167 | bm25=20 unique=10 | top_titles=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置从光驱启动-']
- case_076 | dual=True | rejected=False | anchor_rejected=False | score=0.9912981986999512 | bm25=20 unique=9 | top_titles=['台式和一体机蓝屏报错代码：0x0000007B', 'Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统']
- case_077 | dual=False | rejected=False | anchor_rejected=False | score=0.5617197155952454 | bm25=10 unique=10 | top_titles=['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', 'Windows 2000蓝屏死机故障分析与排除（2）']
- case_078 | dual=True | rejected=False | anchor_rejected=False | score=0.9954458475112915 | bm25=20 unique=10 | top_titles=['安装最新的 Windows 8.1 Update', 'Windows 8.1 Update （KB2919355）常见问题']
- case_079 | dual=True | rejected=True | anchor_rejected=False | score=0.037404902279376984 | bm25=20 unique=10 | top_titles=[]
- case_080 | dual=True | rejected=True | anchor_rejected=False | score=8.855166925059166e-06 | bm25=20 unique=10 | top_titles=[]
- case_081 | dual=False | rejected=False | anchor_rejected=False | score=0.999464213848114 | bm25=10 unique=9 | top_titles=['如何更新网卡的IP地址', '联想支持Windows 10系统升级的机型列表']
- case_082 | dual=True | rejected=False | anchor_rejected=False | score=0.9994891881942749 | bm25=20 unique=12 | top_titles=['如何在 Windows 系统下安装打印机硬件驱动程序', '如何安装网络打印机（XP Win7 Win8）']

> Title weak hit is an automatic weak label, not final business accuracy.