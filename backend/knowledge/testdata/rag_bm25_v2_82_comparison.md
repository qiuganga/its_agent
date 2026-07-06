# RAG Anchor Evidence A/B Comparison

- Generated at: `2026-07-06T14:51:54`
- Baseline: `backend\knowledge\testdata\rag_eval_report_v2_82_hsn_bm25_baseline.json`
- Experiment: `backend\knowledge\testdata\rag_eval_report_v2_82_hsn_bm25_experimental.json`

## Metrics

| Group | Total | Hard | Soft | Negative | No Anchor | Top1 Hit | Top2 Hit | No-answer Anchor Rejected | No-answer Passed | False Rejected | ANCHOR_EVIDENCE_MISSING | Hard Outside TopK | Negative Penalties | Missing source_id |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 82 | 18 | 39 | 5 | 33 | 10 | 15 | 9 | 13 | 4 | 12 | 0 | 0 | 0 |
| experiment | 82 | 18 | 39 | 5 | 33 | 11 | 15 | 9 | 13 | 4 | 12 | 0 | 0 | 0 |

## Top2 Changes

- unchanged: 72
- changed: 10

## Analysis

- anchor_gate_rejects_anchor_unanswerable: 10
- anchor_gate_false_rejected_answerable: ['case_025', 'case_069', 'case_070', 'case_080']
- no_strong_anchor_answerable_false_rejected: []
- remaining_unanswerable_accepted: ['case_042', 'case_043', 'case_047', 'case_048', 'case_052', 'case_061', 'case_062', 'case_063', 'case_064', 'case_065', 'case_066', 'case_067', 'case_068']
- anchor_missing_cases: ['case_022', 'case_023', 'case_024', 'case_041', 'case_045', 'case_046', 'case_049', 'case_050', 'case_051', 'case_069', 'case_070', 'case_080']
- top2_changed_cases: ['case_005', 'case_027', 'case_035', 'case_040', 'case_046', 'case_048', 'case_052', 'case_063', 'case_068', 'case_078']
- likely_anchor_help_cases: ['case_005', 'case_035', 'case_078']
- requires_reranker_groups: ['C_generic_answerable', 'A_anchor_answerable', 'E_confusing', 'D_generic_unanswerable']
- boost_penalty_side_effect_note: Review top2_changed_cases and likely_anchor_help_cases; the script does not tune boost or penalty.

## BM25 Analysis

- baseline_bm25_mode: off
- experiment_bm25_mode: experimental
- bm25_candidate_delta: 889
- bm25_unique_added_delta: 687
- top2_changed_cases: ['case_005', 'case_027', 'case_035', 'case_040', 'case_046', 'case_048', 'case_052', 'case_063', 'case_068', 'case_078']
- top2_weak_hit_improved_cases: []
- top2_weak_hit_regressed_cases: []

## Group Metrics

### baseline
- C_generic_answerable: total=18, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- A_anchor_answerable: total=26, top2=10, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=15, top2=4, false_rejected=3, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=3
- B_anchor_unanswerable: total=15, top2=0, false_rejected=0, no_answer_rejected=10, no_answer_accepted=5, anchor_missing=9
- D_generic_unanswerable: total=8, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0
### experiment
- C_generic_answerable: total=18, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- A_anchor_answerable: total=26, top2=10, false_rejected=1, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=15, top2=4, false_rejected=3, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=3
- B_anchor_unanswerable: total=15, top2=0, false_rejected=0, no_answer_rejected=10, no_answer_accepted=5, anchor_missing=9
- D_generic_unanswerable: total=8, top2=0, false_rejected=0, no_answer_rejected=0, no_answer_accepted=8, anchor_missing=0

## Focus Cases

### case_002
- Question: 开机没反应怎么办
- Anchors: ['startup', '开机']
- Baseline Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.5405179173684178 adjust=0.03 adjusted=0.5705179173684178 status=FULL_ANCHOR_EVIDENCE matched=['startup']
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5273132290295546 adjust=0.0 adjusted=0.5273132290295546 status=NO_ANCHOR_EVIDENCE matched=[]

### case_005
- Question: 电脑蓝屏报错0x0000007B怎么办
- Anchors: ['0x0000007B', 'blue screen', '电脑']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', 'Windows 2000蓝屏死机故障分析与排除']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6147667868352691 adjust=0.11 adjusted=0.7247667868352691 status=FULL_ANCHOR_EVIDENCE matched=['0x0000007B', 'blue screen']
  - Windows 2000蓝屏死机故障分析与排除 | score=0.47632429459995257 adjust=0.11 adjusted=0.5863242945999526 status=FULL_ANCHOR_EVIDENCE matched=['0x0000007B', 'blue screen']

### case_006
- Question: 无线网络连不上怎么办
- Anchors: ['Wi-Fi', '网络']
- Baseline Top2: ['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- Experiment Top2: ['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- Rejected: False reason=None
  - 在Windows 7下如何配置无线网络 | score=0.5540881137202314 adjust=0.03 adjusted=0.5840881137202314 status=FULL_ANCHOR_EVIDENCE matched=['Wi-Fi']
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.5718608173769821 adjust=0.0 adjusted=0.5718608173769821 status=NO_ANCHOR_EVIDENCE matched=[]

### case_009
- Question: 搜不到蓝牙设备怎么办
- Anchors: ['Bluetooth', '蓝牙设备', '设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Experiment Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5768177504998382 adjust=0.03 adjusted=0.6068177504998382 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']
  - 如何确认触控板的品牌（厂商） | score=0.547108736173243 adjust=0.0 adjusted=0.547108736173243 status=NO_ANCHOR_EVIDENCE matched=[]

### case_010
- Question: 连不上蓝牙设备怎么添加
- Anchors: ['Bluetooth', '蓝牙设备', '设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Experiment Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5320595853126088 adjust=0.03 adjusted=0.5620595853126088 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']
  - 蓝牙设备在Win XP SP2操作系统下的设置与使用 | score=0.4723036311132099 adjust=0.03 adjusted=0.5023036311132099 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']

### case_014
- Question: Excel 文件菜单和相关功能灰色不可用怎么办
- Anchors: ['Excel', '文件']
- Baseline Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Experiment Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Rejected: False reason=None
  - Excel文件菜单及相关功能灰色不可用怎么办？ | score=0.6272369918142773 adjust=0.03 adjusted=0.6572369918142773 status=FULL_ANCHOR_EVIDENCE matched=['Excel']
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6114836548508573 adjust=0.0 adjusted=0.6114836548508573 status=NO_ANCHOR_EVIDENCE matched=[]

### case_015
- Question: Word 插入的图片都变成空白框了怎么办
- Anchors: ['Word', '图片']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6227000585535514 adjust=0.0 adjusted=0.6227000585535514 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5984999285816919 adjust=0.0 adjusted=0.5984999285816919 status=NO_ANCHOR_EVIDENCE matched=[]

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Anchors: ['量子网络', '网络']
- Baseline Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Experiment Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 在Windows 8系统下如何查看网络IP地址 | score=0.6251690254848732 adjust=-0.1 adjusted=0.5251690254848732 status=NO_ANCHOR_EVIDENCE matched=[]
  - 暴风影音在播放高清视频时占用的CPU高怎么办- | score=0.586062480401402 adjust=-0.1 adjusted=0.486062480401402 status=NO_ANCHOR_EVIDENCE matched=[]

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Anchors: ['冰箱冷冻室', '电脑']
- Baseline Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 更新Windows 8.1过程中，提示“无法更新到Windows 8.1” | score=0.5231294566538982 adjust=-0.1 adjusted=0.42312945665389823 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5050323858514126 adjust=-0.1 adjusted=0.40503238585141266 status=NO_ANCHOR_EVIDENCE matched=[]

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Anchors: ['折叠屏铰链']
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Experiment Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 同禧有内置音箱的机型如何屏蔽内置音箱 | score=0.7026640656366148 adjust=-0.1 adjusted=0.6026640656366148 status=NO_ANCHOR_EVIDENCE matched=[]
  - 31018765A 扬天T系列用户手册 V1.0 | score=0.6471785905126128 adjust=-0.1 adjusted=0.5471785905126129 status=NO_ANCHOR_EVIDENCE matched=[]
