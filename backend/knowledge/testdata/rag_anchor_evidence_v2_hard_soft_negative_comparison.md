# RAG Anchor Evidence A/B Comparison

- Generated at: `2026-07-05T23:40:42`
- Baseline: `backend\knowledge\testdata\rag_eval_report_v2_anchor_hsn_baseline.json`
- Experiment: `backend\knowledge\testdata\rag_eval_report_v2_anchor_hard_soft_negative.json`

## Metrics

| Group | Total | Hard | Soft | Negative | No Anchor | Top1 Hit | Top2 Hit | No-answer Anchor Rejected | No-answer Passed | False Rejected | ANCHOR_EVIDENCE_MISSING | Hard Outside TopK | Negative Penalties | Missing source_id |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 82 | 18 | 39 | 5 | 33 | 7 | 9 | 0 | 23 | 1 | 0 | 0 | 0 | 0 |
| experiment | 82 | 18 | 39 | 5 | 33 | 10 | 15 | 9 | 13 | 4 | 12 | 0 | 0 | 0 |
| legacy | 82 | 18 | 39 | 5 | 33 | 13 | 19 | 7 | 14 | 13 | 19 | 0 | 0 | 0 |

## Top2 Changes

- unchanged: 60
- changed: 22

## Analysis

- anchor_gate_rejects_anchor_unanswerable: 10
- anchor_gate_false_rejected_answerable: ['case_025', 'case_069', 'case_070', 'case_080']
- no_strong_anchor_answerable_false_rejected: []
- remaining_unanswerable_accepted: ['case_042', 'case_043', 'case_047', 'case_048', 'case_052', 'case_061', 'case_062', 'case_063', 'case_064', 'case_065', 'case_066', 'case_067', 'case_068']
- anchor_missing_cases: ['case_022', 'case_023', 'case_024', 'case_041', 'case_045', 'case_046', 'case_049', 'case_050', 'case_051', 'case_069', 'case_070', 'case_080']
- top2_changed_cases: ['case_004', 'case_006', 'case_010', 'case_018', 'case_021', 'case_022', 'case_032', 'case_033', 'case_035', 'case_036', 'case_039', 'case_044', 'case_048', 'case_049', 'case_051', 'case_056', 'case_062', 'case_065', 'case_068', 'case_075', 'case_076', 'case_078']
- likely_anchor_help_cases: ['case_004', 'case_006', 'case_010', 'case_018', 'case_021', 'case_032', 'case_033', 'case_035', 'case_036', 'case_075', 'case_076', 'case_078']
- requires_reranker_groups: ['C_generic_answerable', 'A_anchor_answerable', 'E_confusing', 'D_generic_unanswerable']
- boost_penalty_side_effect_note: Review top2_changed_cases and likely_anchor_help_cases; the script does not tune boost or penalty.

## Three-way Analysis

- legacy_false_rejected: 13
- new_false_rejected: 4
- legacy_anchor_rejected_no_answer: 7
- new_anchor_rejected_no_answer: 9
- new_hard_evidence_outside_topk: 0
- new_negative_anchor_penalties: 0

## Group Metrics

### baseline
- C_generic_answerable: total=18, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- A_anchor_answerable: total=26, top2=6, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=15, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- B_anchor_unanswerable: total=15, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=15, anchor_missing=0
- D_generic_unanswerable: total=8, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0
### experiment
- C_generic_answerable: total=18, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- A_anchor_answerable: total=26, top2=10, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=15, top2=4, false_rejected=3, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=3
- B_anchor_unanswerable: total=15, top2=0, false_rejected=0, no_answer_rejected=10, no_answer_accepted=5, anchor_missing=9
- D_generic_unanswerable: total=8, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0
### legacy
- C_generic_answerable: total=18, top2=1, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=1
- A_anchor_answerable: total=26, top2=13, false_rejected=6, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=5
- E_confusing: total=15, top2=5, false_rejected=6, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=6
- B_anchor_unanswerable: total=15, top2=0, false_rejected=0, no_answer_rejected=9, no_answer_accepted=6, anchor_missing=7
- D_generic_unanswerable: total=8, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0

## Focus Cases

### case_002
- Question: 开机没反应怎么办
- Anchors: ['startup', '开机']
- Baseline Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.5394869763044614 adjust=0.03 adjusted=0.5694869763044614 status=FULL_ANCHOR_EVIDENCE matched=['startup']
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5238238584081376 adjust=0.0 adjusted=0.5238238584081376 status=NO_ANCHOR_EVIDENCE matched=[]

### case_005
- Question: 电脑蓝屏报错0x0000007B怎么办
- Anchors: ['0x0000007B', 'blue screen', '电脑']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6129120461236077 adjust=0.11 adjusted=0.7229120461236077 status=FULL_ANCHOR_EVIDENCE matched=['0x0000007B', 'blue screen']
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.5931223198490008 adjust=-0.1 adjusted=0.4931223198490008 status=NO_ANCHOR_EVIDENCE matched=[]

### case_006
- Question: 无线网络连不上怎么办
- Anchors: ['Wi-Fi', '网络']
- Baseline Top2: ['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- Rejected: False reason=None
  - 在Windows 7下如何配置无线网络 | score=0.5537360675001923 adjust=0.03 adjusted=0.5837360675001924 status=FULL_ANCHOR_EVIDENCE matched=['Wi-Fi']
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.5710641717703838 adjust=0.0 adjusted=0.5710641717703838 status=NO_ANCHOR_EVIDENCE matched=[]

### case_009
- Question: 搜不到蓝牙设备怎么办
- Anchors: ['Bluetooth', '蓝牙设备', '设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Experiment Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5756142981738701 adjust=0.03 adjusted=0.6056142981738701 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']
  - 如何确认触控板的品牌（厂商） | score=0.5462264950720579 adjust=0.0 adjusted=0.5462264950720579 status=NO_ANCHOR_EVIDENCE matched=[]

### case_010
- Question: 连不上蓝牙设备怎么添加
- Anchors: ['Bluetooth', '蓝牙设备', '设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何备份幸福之家4.X中的日记']
- Experiment Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5297932824077565 adjust=0.03 adjusted=0.5597932824077565 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']
  - 蓝牙设备在Win XP SP2操作系统下的设置与使用 | score=0.4722967109206015 adjust=0.03 adjusted=0.5022967109206015 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']

### case_014
- Question: Excel 文件菜单和相关功能灰色不可用怎么办
- Anchors: ['Excel', '文件']
- Baseline Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Experiment Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Rejected: False reason=None
  - Excel文件菜单及相关功能灰色不可用怎么办？ | score=0.6276468722254123 adjust=0.03 adjusted=0.6576468722254123 status=FULL_ANCHOR_EVIDENCE matched=['Excel']
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6122342669176513 adjust=0.0 adjusted=0.6122342669176513 status=NO_ANCHOR_EVIDENCE matched=[]

### case_015
- Question: Word 插入的图片都变成空白框了怎么办
- Anchors: ['Word', '图片']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6223229357658677 adjust=0.0 adjusted=0.6223229357658677 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5979668815248114 adjust=0.0 adjusted=0.5979668815248114 status=NO_ANCHOR_EVIDENCE matched=[]

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Anchors: ['量子网络', '网络']
- Baseline Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Experiment Top2: ['在Windows 8系统下如何查看网络IP地址', 'WinXP从待机状态唤醒后网络连接断开']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 在Windows 8系统下如何查看网络IP地址 | score=0.6247332738634324 adjust=-0.1 adjusted=0.5247332738634324 status=NO_ANCHOR_EVIDENCE matched=[]
  - WinXP从待机状态唤醒后网络连接断开 | score=0.5818151772838617 adjust=-0.1 adjusted=0.4818151772838617 status=NO_ANCHOR_EVIDENCE matched=[]

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Anchors: ['冰箱冷冻室', '电脑']
- Baseline Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 更新Windows 8.1过程中，提示“无法更新到Windows 8.1” | score=0.5233667564190059 adjust=-0.1 adjusted=0.4233667564190059 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.506594995122661 adjust=-0.1 adjusted=0.40659499512266106 status=NO_ANCHOR_EVIDENCE matched=[]

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Anchors: ['折叠屏铰链']
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Experiment Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 同禧有内置音箱的机型如何屏蔽内置音箱 | score=0.7031153753864848 adjust=-0.1 adjusted=0.6031153753864849 status=NO_ANCHOR_EVIDENCE matched=[]
  - 31018765A 扬天T系列用户手册 V1.0 | score=0.6478328547285436 adjust=-0.1 adjusted=0.5478328547285436 status=NO_ANCHOR_EVIDENCE matched=[]
