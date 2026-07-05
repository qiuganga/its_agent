# RAG Anchor Evidence A/B Comparison

- Generated at: `2026-07-05T19:46:50`
- Baseline: `backend\knowledge\testdata\rag_eval_report_v2_anchor_baseline.json`
- Experiment: `backend\knowledge\testdata\rag_eval_report_v2_anchor_evidence.json`

## Metrics

| Group | Total | Strong Anchor | No Strong Anchor | Top1 Hit | Top2 Hit | No-answer Anchor Rejected | No-answer Passed | False Rejected | ANCHOR_EVIDENCE_MISSING | Missing source_id |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 82 | 0 | 82 | 7 | 9 | 0 | 23 | 1 | 0 | 0 |
| experiment | 82 | 39 | 43 | 13 | 17 | 7 | 16 | 10 | 16 | 0 |

## Top2 Changes

- unchanged: 56
- changed: 26

## Analysis

- anchor_gate_rejects_anchor_unanswerable: 7
- anchor_gate_false_rejected_answerable: ['case_071', 'case_072', 'case_074', 'case_080', 'case_025', 'case_026', 'case_027', 'case_030', 'case_039', 'case_040']
- no_strong_anchor_answerable_false_rejected: []
- remaining_unanswerable_accepted: ['case_041', 'case_042', 'case_043', 'case_046', 'case_047', 'case_048', 'case_051', 'case_052', 'case_061', 'case_062', 'case_063', 'case_064', 'case_065', 'case_066', 'case_067', 'case_068']
- anchor_missing_cases: ['case_022', 'case_023', 'case_024', 'case_026', 'case_027', 'case_030', 'case_039', 'case_040', 'case_044', 'case_045', 'case_049', 'case_050', 'case_071', 'case_072', 'case_074', 'case_080']
- top2_changed_cases: ['case_006', 'case_009', 'case_010', 'case_014', 'case_015', 'case_016', 'case_018', 'case_026', 'case_028', 'case_031', 'case_032', 'case_033', 'case_034', 'case_035', 'case_036', 'case_037', 'case_038', 'case_048', 'case_051', 'case_052', 'case_069', 'case_070', 'case_073', 'case_076', 'case_078', 'case_082']
- likely_anchor_help_cases: ['case_006', 'case_009', 'case_010', 'case_014', 'case_015', 'case_016', 'case_018', 'case_028', 'case_031', 'case_032', 'case_033', 'case_034', 'case_035', 'case_036', 'case_037', 'case_038', 'case_069', 'case_070', 'case_073', 'case_076', 'case_078', 'case_082']
- requires_reranker_groups: ['C_generic_answerable', 'E_confusing', 'A_anchor_answerable', 'D_generic_unanswerable']
- boost_penalty_side_effect_note: Review top2_changed_cases and likely_anchor_help_cases; the script does not tune boost or penalty.

## Group Metrics

### baseline
- C_generic_answerable: total=20, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=15, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- A_anchor_answerable: total=24, top2=5, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- B_anchor_unanswerable: total=15, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=15, anchor_missing=0
- D_generic_unanswerable: total=8, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0
### experiment
- C_generic_answerable: total=20, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=15, top2=4, false_rejected=4, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=4
- A_anchor_answerable: total=24, top2=11, false_rejected=6, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=5
- B_anchor_unanswerable: total=15, top2=0, false_rejected=0, no_answer_rejected=7, no_answer_accepted=8, anchor_missing=7
- D_generic_unanswerable: total=8, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0

## Focus Cases

### case_002
- Question: 开机没反应怎么办
- Anchors: []
- Baseline Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.5418942996633378 adjust=0.0 adjusted=0.5418942996633378 status=NO_STRONG_ANCHOR matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5251268358461182 adjust=0.0 adjusted=0.5251268358461182 status=NO_STRONG_ANCHOR matched=[]

### case_005
- Question: 电脑蓝屏报错0x0000007B怎么办
- Anchors: ['0x0000007B']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6129120461236077 adjust=0.08 adjusted=0.6929120461236077 status=FULL_ANCHOR_EVIDENCE matched=['0x0000007B']
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.5931223198490008 adjust=-0.12 adjusted=0.47312231984900077 status=NO_ANCHOR_EVIDENCE matched=[]

### case_006
- Question: 无线网络连不上怎么办
- Anchors: ['无线网络']
- Baseline Top2: ['联想无线键鼠套装安装注意事项，无线键盘或鼠标突然失灵怎么办？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['在Windows 7下如何配置无线网络', '联想手机A789如何连接无线网络上网']
- Rejected: False reason=None
  - 在Windows 7下如何配置无线网络 | score=0.5540881137202314 adjust=0.08 adjusted=0.6340881137202313 status=FULL_ANCHOR_EVIDENCE matched=['无线网络']
  - 联想手机A789如何连接无线网络上网 | score=0.5488117689455635 adjust=0.08 adjusted=0.6288117689455635 status=FULL_ANCHOR_EVIDENCE matched=['无线网络']

### case_009
- Question: 搜不到蓝牙设备怎么办
- Anchors: ['蓝牙', '蓝牙设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Experiment Top2: ['如何添加启用蓝牙的设备', '如何开启蓝牙模块功能']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5798051182339028 adjust=0.08 adjusted=0.6598051182339028 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']
  - 如何开启蓝牙模块功能 | score=0.5150872151480291 adjust=0.08 adjusted=0.5950872151480291 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']

### case_010
- Question: 连不上蓝牙设备怎么添加
- Anchors: ['蓝牙', '蓝牙设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何备份幸福之家4.X中的日记']
- Experiment Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5298705776660186 adjust=0.08 adjusted=0.6098705776660186 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']
  - 蓝牙设备在Win XP SP2操作系统下的设置与使用 | score=0.47269936697732373 adjust=0.08 adjusted=0.5526993669773237 status=FULL_ANCHOR_EVIDENCE matched=['蓝牙', '蓝牙设备']

### case_014
- Question: Excel 文件菜单和相关功能灰色不可用怎么办
- Anchors: ['Excel']
- Baseline Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Experiment Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', 'Excel表导入 Access 2010 后时间显示错误怎么办-']
- Rejected: False reason=None
  - Excel文件菜单及相关功能灰色不可用怎么办？ | score=0.6279600568445349 adjust=0.08 adjusted=0.7079600568445349 status=FULL_ANCHOR_EVIDENCE matched=['Excel']
  - Excel表导入 Access 2010 后时间显示错误怎么办- | score=0.5864185129933905 adjust=0.08 adjusted=0.6664185129933905 status=FULL_ANCHOR_EVIDENCE matched=['Excel']

### case_015
- Question: Word 插入的图片都变成空白框了怎么办
- Anchors: ['Word']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['为什么 Word 2010-2007 中插入的图片都变成空白框了？', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 为什么 Word 2010-2007 中插入的图片都变成空白框了？ | score=0.5785555440687418 adjust=0.08 adjusted=0.6585555440687417 status=FULL_ANCHOR_EVIDENCE matched=['Word']
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5988207047308607 adjust=-0.12 adjusted=0.4788207047308607 status=NO_ANCHOR_EVIDENCE matched=[]

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Anchors: ['量子网络']
- Baseline Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Experiment Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 在Windows 8系统下如何查看网络IP地址 | score=0.6248707379315541 adjust=-0.12 adjusted=0.5048707379315541 status=NO_ANCHOR_EVIDENCE matched=[]
  - 暴风影音在播放高清视频时占用的CPU高怎么办- | score=0.5866134912426009 adjust=-0.12 adjusted=0.4666134912426009 status=NO_ANCHOR_EVIDENCE matched=[]

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Anchors: ['冰箱冷冻室']
- Baseline Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 更新Windows 8.1过程中，提示“无法更新到Windows 8.1” | score=0.5231294566538982 adjust=-0.12 adjusted=0.4031294566538982 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5050323858514126 adjust=-0.12 adjusted=0.38503238585141264 status=NO_ANCHOR_EVIDENCE matched=[]

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Anchors: ['折叠屏铰链']
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Experiment Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 同禧有内置音箱的机型如何屏蔽内置音箱 | score=0.7031034160075843 adjust=-0.12 adjusted=0.5831034160075843 status=NO_ANCHOR_EVIDENCE matched=[]
  - 31018765A 扬天T系列用户手册 V1.0 | score=0.647268346263858 adjust=-0.12 adjusted=0.527268346263858 status=NO_ANCHOR_EVIDENCE matched=[]
