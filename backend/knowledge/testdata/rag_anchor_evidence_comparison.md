# RAG Anchor Evidence A/B Comparison

- Generated at: `2026-07-05T15:58:08`
- Baseline: `D:\sgg-agent\code\its_multi_agent\backend\knowledge\testdata\rag_eval_report_clean_v1_anchor_baseline.json`
- Experiment: `D:\sgg-agent\code\its_multi_agent\backend\knowledge\testdata\rag_eval_report_clean_v1_anchor_evidence.json`

## Metrics

| Group | Total | Strong Anchor | No Strong Anchor | Top1 Hit | Top2 Hit | No-answer Anchor Rejected | No-answer Passed | False Rejected | ANCHOR_EVIDENCE_MISSING | Missing source_id |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 24 | 0 | 24 | 7 | 10 | 0 | 3 | 0 | 0 | 0 |
| experiment | 24 | 11 | 13 | 9 | 11 | 3 | 0 | 0 | 3 | 0 |

## Top2 Changes

- unchanged: 15
- changed: 9

## Focus Cases

### case_002
- Question: 开机没反应怎么办
- Anchors: []
- Baseline Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.5391750934721173 adjust=0.0 adjusted=0.5391750934721173 status=NO_STRONG_ANCHOR matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5256470093238185 adjust=0.0 adjusted=0.5256470093238185 status=NO_STRONG_ANCHOR matched=[]

### case_005
- Question: 电脑蓝屏报错0x0000007B怎么办
- Anchors: ['0x0000007B']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6133300324409076 adjust=0.08 adjusted=0.6933300324409075 status=FULL_ANCHOR_EVIDENCE matched=['0x0000007B']
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.59400648065522 adjust=-0.12 adjusted=0.47400648065522 status=NO_ANCHOR_EVIDENCE matched=[]

### case_006
- Question: 无线网络连不上怎么办
- Anchors: ['无线网络']
- Baseline Top2: ['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['在Windows 7下如何配置无线网络', '联想手机A789如何连接无线网络上网']
- Rejected: False reason=None
  - 在Windows 7下如何配置无线网络 | score=0.5537360675001923 adjust=0.08 adjusted=0.6337360675001923 status=FULL_ANCHOR_EVIDENCE matched=['无线网络']
  - 联想手机A789如何连接无线网络上网 | score=0.5476949964964137 adjust=0.08 adjusted=0.6276949964964137 status=FULL_ANCHOR_EVIDENCE matched=['无线网络']

### case_009
- Question: 搜不到蓝牙设备怎么办
- Anchors: ['蓝牙', '蓝牙设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Experiment Top2: ['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.577574535638185 adjust=0.08 adjusted=0.6575745356381849 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']
  - 如何开启蓝牙模块功能 | score=0.5137353125423981 adjust=0.08 adjusted=0.5937353125423981 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']

### case_010
- Question: 连不上蓝牙设备怎么添加
- Anchors: ['蓝牙', '蓝牙设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何备份幸福之家4.X中的日记']
- Experiment Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5307616001953248 adjust=0.08 adjusted=0.6107616001953248 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']
  - 蓝牙设备在Win XP SP2操作系统下的设置与使用 | score=0.4723723810886072 adjust=0.08 adjusted=0.5523723810886072 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']

### case_014
- Question: Excel 文件菜单和相关功能灰色不可用怎么办
- Anchors: ['Excel']
- Baseline Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Experiment Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', 'Excel表导入 Access 2010 后时间显示错误怎么办-']
- Rejected: False reason=None
  - Excel文件菜单及相关功能灰色不可用怎么办？ | score=0.6265706662738548 adjust=0.08 adjusted=0.7065706662738548 status=FULL_ANCHOR_EVIDENCE matched=['Excel']
  - Excel表导入 Access 2010 后时间显示错误怎么办- | score=0.5867700439627834 adjust=0.08 adjusted=0.6667700439627834 status=FULL_ANCHOR_EVIDENCE matched=['Excel']

### case_015
- Question: Word 插入的图片都变成空白框了怎么办
- Anchors: ['Word']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 为什么 Word 2010-2007 中插入的图片都变成空白框了？ | score=0.576646938491748 adjust=0.08 adjusted=0.6566469384917479 status=FULL_ANCHOR_EVIDENCE matched=['Word']
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5998925110912356 adjust=-0.12 adjusted=0.47989251109123565 status=NO_ANCHOR_EVIDENCE matched=[]

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Anchors: ['量子网络']
- Baseline Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Experiment Top2: ['在Windows 8系统下如何查看网络IP地址', 'WinXP从待机状态唤醒后网络连接断开']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 在Windows 8系统下如何查看网络IP地址 | score=0.6248707379315541 adjust=-0.12 adjusted=0.5048707379315541 status=NO_ANCHOR_EVIDENCE matched=[]
  - WinXP从待机状态唤醒后网络连接断开 | score=0.5828852912390075 adjust=-0.12 adjusted=0.46288529123900746 status=NO_ANCHOR_EVIDENCE matched=[]

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Anchors: ['冰箱冷冻室']
- Baseline Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 更新Windows 8.1过程中，提示“无法更新到Windows 8.1” | score=0.5216628282865722 adjust=-0.12 adjusted=0.4016628282865722 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5049519045749329 adjust=-0.12 adjusted=0.3849519045749329 status=NO_ANCHOR_EVIDENCE matched=[]

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Anchors: ['折叠屏铰链']
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Experiment Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 同禧有内置音箱的机型如何屏蔽内置音箱 | score=0.7042312876087977 adjust=-0.12 adjusted=0.5842312876087977 status=NO_ANCHOR_EVIDENCE matched=[]
  - 31018765A 扬天T系列用户手册 V1.0 | score=0.6478328547285436 adjust=-0.12 adjusted=0.5278328547285436 status=NO_ANCHOR_EVIDENCE matched=[]
