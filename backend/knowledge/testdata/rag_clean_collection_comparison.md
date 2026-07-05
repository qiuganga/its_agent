# RAG Clean Collection A/B/C Comparison

- Generated at: `2026-07-05T00:27:02`

## Metrics

| Group | Collection | Indexable Docs | Skipped Docs | Chunks | Avg Chunks/Doc | Metadata Rate | Top1 Hit | Top2 Hit | No-answer Passed | No-answer Rejected |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| old | its-knowledge | None | None | 1101 | None | 0.0 | 4 | 6 | 3 | 0 |
| clean | its-knowledge-clean-v1 | 733 | 0 | 834 | 1.1378 | 1.0 | 7 | 9 | 3 | 0 |
| clean_small_chunk | its-knowledge-clean-chunk1000-v1 | 733 | 0 | 974 | 1.3288 | 1.0 | 4 | 6 | 3 | 0 |

## Classification Counts

- requires_manual_review: 17
- positive: 5
- negative: 2

## Focus Cases

### case_001
- Question: 开不了机，屏幕不亮怎么办
- Classification: `requires_manual_review`
- old: top=['Visio 2010-2007 形状面板不见了怎么办？', 'Lenovo G485无线网络连接不上的解决方案'] scores=[0.5642337726750268, 0.5590641529790483] top2_hit=False candidates=36
- clean: top=['Windows XP 关机故障', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）'] scores=[0.603783819822407, 0.5468904943019967] top2_hit=False candidates=37
- clean_small_chunk: top=['Excel文件菜单及相关功能灰色不可用怎么办？', 'Windows XP 关机故障'] scores=[0.6563383328111727, 0.6014237292392017] top2_hit=False candidates=36

### case_002
- Question: 开机没反应怎么办
- Classification: `positive`
- old: top=['电子词典LN4000操作汇总', 'Internet Explorer版本升级说明'] scores=[0.5462223925728276, 0.5001764997299845] top2_hit=False candidates=31
- clean: top=['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）'] scores=[0.5414254472785203, 0.5251268358461182] top2_hit=True candidates=28
- clean_small_chunk: top=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想支持Windows 10系统升级的机型列表'] scores=[0.6053414805643793, 0.5325919266741965] top2_hit=False candidates=31

### case_003
- Question: 屏幕不亮但风扇会转，电脑黑屏怎么处理
- Classification: `positive`
- old: top=['如何设置显卡的电源管理', '智能电视开不了机并且指示灯都不亮怎么办？'] scores=[0.5287652817018051, 0.5228054571086586] top2_hit=False candidates=41
- clean: top=['宽带连接频繁掉线', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）'] scores=[0.5320364763181433, 0.5165509829034334] top2_hit=True candidates=41
- clean_small_chunk: top=['宽带连接频繁掉线', 'Excel文件菜单及相关功能灰色不可用怎么办？'] scores=[0.5351204301667424, 0.515683648398809] top2_hit=False candidates=41

### case_005
- Question: 电脑蓝屏报错0x0000007B怎么办
- Classification: `positive`
- old: top=['新圆梦F系列电脑运行游戏卡', '电子词典LN4000操作汇总'] scores=[0.5846510550471072, 0.5750452821644836] top2_hit=False candidates=25
- clean: top=['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动'] scores=[0.6121722092319496, 0.5925482081836805] top2_hit=True candidates=25
- clean_small_chunk: top=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B'] scores=[0.6371012340684956, 0.6147667868352691] top2_hit=True candidates=25

### case_006
- Question: 无线网络连不上怎么办
- Classification: `requires_manual_review`
- old: top=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', 'Windows 2000蓝屏死机故障分析与排除'] scores=[0.5809229743821851, 0.5546277844316582] top2_hit=False candidates=24
- clean: top=['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）'] scores=[0.5827017107573725, 0.5622062608219777] top2_hit=False candidates=25
- clean_small_chunk: top=['Excel文件菜单及相关功能灰色不可用怎么办？', '联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？'] scores=[0.6343395195709776, 0.5823665775481475] top2_hit=False candidates=25

### case_009
- Question: 搜不到蓝牙设备怎么办
- Classification: `positive`
- old: top=['Lenovo G470开机屏幕黑屏或蓝屏报错,无法正常进入系统', '关于NOKIA手机通过红外线连接旭日150拨号上网的解决方案'] scores=[0.5337793915237351, 0.5014754493385694] top2_hit=False candidates=44
- clean: top=['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）'] scores=[0.5781446021061756, 0.5456722600264399] top2_hit=True candidates=39
- clean_small_chunk: top=['如何添加启用蓝牙的设备', 'Excel文件菜单及相关功能灰色不可用怎么办？'] scores=[0.5756142981738701, 0.5673097217272591] top2_hit=True candidates=39

### case_011
- Question: 电脑没声音，音量怎么调
- Classification: `requires_manual_review`
- old: top=['如何通过联想电源管理软件调整电源模式', '电脑会自动开机启动，是什么问题？'] scores=[0.45977858929348675, 0.41606755051680955] top2_hit=False candidates=26
- clean: top=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？'] scores=[0.5937000844636269, 0.4697691822364749] top2_hit=False candidates=26
- clean_small_chunk: top=['如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）', '一键恢复功能键在什么位置？'] scores=[0.5950282509558078, 0.47062227451354477] top2_hit=False candidates=27

### case_012
- Question: 系统卡死没有响应怎么办
- Classification: `requires_manual_review`
- old: top=['电子词典LN4000操作汇总', 'Windows 2000蓝屏死机故障分析与排除'] scores=[0.5329886350256616, 0.5203025216761005] top2_hit=False candidates=30
- clean: top=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '开机时，需要按F1（或F2）键后才能继续启动'] scores=[0.5527975914307299, 0.5451647526708359] top2_hit=False candidates=29
- clean_small_chunk: top=['Excel文件菜单及相关功能灰色不可用怎么办？', '更新Windows 8.1过程中，提示“无法更新到Windows 8.1”'] scores=[0.5824659911185619, 0.5507230833687018] top2_hit=False candidates=30

### case_015
- Question: Word 插入的图片都变成空白框了怎么办
- Classification: `requires_manual_review`
- old: top=['电子词典LN4000操作汇总', '单向可Ping通的原因与原理-'] scores=[0.590867295810328, 0.5650950879342661] top2_hit=False candidates=25
- clean: top=['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）'] scores=[0.6224840537258507, 0.5984999285816919] top2_hit=False candidates=25
- clean_small_chunk: top=['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B'] scores=[0.6624465902741279, 0.6223052100195168] top2_hit=False candidates=25

### case_018
- Question: 如何使用U盘安装Windows 7操作系统
- Classification: `requires_manual_review`
- old: top=['联想摄像头随机软件能否保存视频捕捉属性以及视频捕捉参数？', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）'] scores=[0.48657090393008307, 0.4633210043813585] top2_hit=False candidates=23
- clean: top=['联想硬盘保护EDU7.X的安装方法', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）'] scores=[0.824089887496962, 0.5529502240967934] top2_hit=False candidates=25
- clean_small_chunk: top=['联想硬盘保护EDU7.X的安装方法', '使用联想系统恢复光盘安装WIN98操作系统（CHM格式）'] scores=[0.8268134132940277, 0.5559366774853229] top2_hit=False candidates=24

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Classification: `requires_manual_review`
- old: top=['联想一键恢复的使用方法', '电子词典LN4000操作汇总'] scores=[0.5808058663718789, 0.5794257451171771] top2_hit=False candidates=28
- clean: top=['在Windows 8系统下如何查看网络IP地址', 'WinXP从待机状态唤醒后网络连接断开'] scores=[0.6252994272586148, 0.5837147925788273] top2_hit=False candidates=29
- clean_small_chunk: top=['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-'] scores=[0.6241570894314977, 0.5861753718855995] top2_hit=False candidates=29

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Classification: `requires_manual_review`
- old: top=['Windows自带电源管理（包括休眠、待机和睡眠）的设置方法', 'Windows 2000蓝屏死机故障分析与排除'] scores=[0.521603131710743, 0.5134956036123652] top2_hit=False candidates=25
- clean: top=['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）'] scores=[0.524272029123074, 0.5065999746965979] top2_hit=False candidates=25
- clean_small_chunk: top=['Excel文件菜单及相关功能灰色不可用怎么办？', '改善手机或平板机身发热的办法'] scores=[0.5912533848365349, 0.5592796427870816] top2_hit=False candidates=25

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Classification: `requires_manual_review`
- old: top=['在Windows XP下如何配置无线网络', '如何恢复Windows XP任务栏输入法图标'] scores=[0.6778516386762434, 0.6700769863402853] top2_hit=False candidates=24
- clean: top=['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0'] scores=[0.7035405046010768, 0.6471785905126128] top2_hit=False candidates=25
- clean_small_chunk: top=['同禧有内置音箱的机型如何屏蔽内置音箱', 'SecureBoot未正确配置'] scores=[0.7042312876087977, 0.6877515934990753] top2_hit=False candidates=24
