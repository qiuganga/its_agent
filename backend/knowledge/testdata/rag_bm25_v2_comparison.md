# RAG Anchor Evidence A/B Comparison

- Generated at: `2026-07-06T13:07:24`
- Baseline: `backend\knowledge\testdata\rag_eval_report_v2_hsn_bm25_baseline.json`
- Experiment: `backend\knowledge\testdata\rag_eval_report_v2_hsn_bm25_experimental.json`

## Metrics

| Group | Total | Hard | Soft | Negative | No Anchor | Top1 Hit | Top2 Hit | No-answer Anchor Rejected | No-answer Passed | False Rejected | ANCHOR_EVIDENCE_MISSING | Hard Outside TopK | Negative Penalties | Missing source_id |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 24 | 4 | 11 | 0 | 10 | 8 | 10 | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| experiment | 24 | 4 | 11 | 0 | 10 | 8 | 10 | 3 | 0 | 0 | 3 | 0 | 0 | 0 |

## Top2 Changes

- unchanged: 22
- changed: 2

## Analysis

- anchor_gate_rejects_anchor_unanswerable: 3
- anchor_gate_false_rejected_answerable: []
- no_strong_anchor_answerable_false_rejected: []
- remaining_unanswerable_accepted: []
- anchor_missing_cases: ['case_022', 'case_023', 'case_024']
- top2_changed_cases: ['case_005', 'case_022']
- likely_anchor_help_cases: ['case_005']
- requires_reranker_groups: ['C_generic_answerable', 'A_anchor_answerable', 'E_confusing']
- boost_penalty_side_effect_note: Review top2_changed_cases and likely_anchor_help_cases; the script does not tune boost or penalty.

## BM25 Analysis

- baseline_bm25_mode: off
- experiment_bm25_mode: experimental
- bm25_candidate_delta: 320
- bm25_unique_added_delta: 243
- top2_changed_cases: ['case_005', 'case_022']
- top2_weak_hit_improved_cases: []
- top2_weak_hit_regressed_cases: []

## Group Metrics

### baseline
- C_generic_answerable: total=8, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- A_anchor_answerable: total=10, top2=7, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=3, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- B_anchor_unanswerable: total=3, top2=0, false_rejected=0, no_answer_rejected=3, no_answer_accepted=0, anchor_missing=3
### experiment
- C_generic_answerable: total=8, top2=1, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- A_anchor_answerable: total=10, top2=7, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- E_confusing: total=3, top2=2, false_rejected=0, no_answer_rejected=0, no_answer_accepted=0, anchor_missing=0
- B_anchor_unanswerable: total=3, top2=0, false_rejected=0, no_answer_rejected=3, no_answer_accepted=0, anchor_missing=3

## Focus Cases

### case_002
- Question: 开机没反应怎么办
- Anchors: ['startup', '开机']
- Baseline Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['开机时，需要按F1（或F2）键后才能继续启动', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 开机时，需要按F1（或F2）键后才能继续启动 | score=0.5418856671685435 adjust=0.03 adjusted=0.5718856671685435 status=FULL_ANCHOR_EVIDENCE matched=['startup']
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5251268358461182 adjust=0.0 adjusted=0.5251268358461182 status=NO_ANCHOR_EVIDENCE matched=[]

### case_005
- Question: 电脑蓝屏报错0x0000007B怎么办
- Anchors: ['0x0000007B', 'blue screen', '电脑']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '开机时，需要按F1（或F2）键后才能继续启动']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', 'Windows 2000蓝屏死机故障分析与排除']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6141365615763263 adjust=0.11 adjusted=0.7241365615763263 status=FULL_ANCHOR_EVIDENCE matched=['0x0000007B', 'blue screen']
  - Windows 2000蓝屏死机故障分析与排除 | score=0.47728784544981634 adjust=0.11 adjusted=0.5872878454498164 status=FULL_ANCHOR_EVIDENCE matched=['0x0000007B', 'blue screen']

### case_006
- Question: 无线网络连不上怎么办
- Anchors: ['Wi-Fi', '网络']
- Baseline Top2: ['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- Experiment Top2: ['在Windows 7下如何配置无线网络', '台式和一体机蓝屏报错代码：0x0000007B']
- Rejected: False reason=None
  - 在Windows 7下如何配置无线网络 | score=0.5529292883825603 adjust=0.03 adjusted=0.5829292883825603 status=FULL_ANCHOR_EVIDENCE matched=['Wi-Fi']
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.5708817034261632 adjust=0.0 adjusted=0.5708817034261632 status=NO_ANCHOR_EVIDENCE matched=[]

### case_009
- Question: 搜不到蓝牙设备怎么办
- Anchors: ['Bluetooth', '蓝牙设备', '设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Experiment Top2: ['如何添加启用蓝牙的设备', '如何确认触控板的品牌（厂商）']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5791816013604253 adjust=0.03 adjusted=0.6091816013604253 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']
  - 如何确认触控板的品牌（厂商） | score=0.547108736173243 adjust=0.0 adjusted=0.547108736173243 status=NO_ANCHOR_EVIDENCE matched=[]

### case_010
- Question: 连不上蓝牙设备怎么添加
- Anchors: ['Bluetooth', '蓝牙设备', '设备']
- Baseline Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Experiment Top2: ['如何添加启用蓝牙的设备', '蓝牙设备在Win XP SP2操作系统下的设置与使用']
- Rejected: False reason=None
  - 如何添加启用蓝牙的设备 | score=0.5307124324756816 adjust=0.03 adjusted=0.5607124324756816 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']
  - 蓝牙设备在Win XP SP2操作系统下的设置与使用 | score=0.47304838661688275 adjust=0.03 adjusted=0.5030483866168828 status=FULL_ANCHOR_EVIDENCE matched=['Bluetooth', '蓝牙设备']

### case_014
- Question: Excel 文件菜单和相关功能灰色不可用怎么办
- Anchors: ['Excel', '文件']
- Baseline Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Experiment Top2: ['Excel文件菜单及相关功能灰色不可用怎么办？', '台式和一体机蓝屏报错代码：0x0000007B']
- Rejected: False reason=None
  - Excel文件菜单及相关功能灰色不可用怎么办？ | score=0.6269816268504407 adjust=0.03 adjusted=0.6569816268504407 status=FULL_ANCHOR_EVIDENCE matched=['Excel']
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.6110083997103446 adjust=0.0 adjusted=0.6110083997103446 status=NO_ANCHOR_EVIDENCE matched=[]

### case_015
- Question: Word 插入的图片都变成空白框了怎么办
- Anchors: ['Word', '图片']
- Baseline Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['台式和一体机蓝屏报错代码：0x0000007B', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: False reason=None
  - 台式和一体机蓝屏报错代码：0x0000007B | score=0.622751950806534 adjust=0.0 adjusted=0.622751950806534 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.6004734276920214 adjust=0.0 adjusted=0.6004734276920214 status=NO_ANCHOR_EVIDENCE matched=[]

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Anchors: ['量子网络', '网络']
- Baseline Top2: ['在Windows 8系统下如何查看网络IP地址', 'WinXP从待机状态唤醒后网络连接断开']
- Experiment Top2: ['在Windows 8系统下如何查看网络IP地址', '暴风影音在播放高清视频时占用的CPU高怎么办-']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 在Windows 8系统下如何查看网络IP地址 | score=0.6248821369412623 adjust=-0.1 adjusted=0.5248821369412623 status=NO_ANCHOR_EVIDENCE matched=[]
  - 暴风影音在播放高清视频时占用的CPU高怎么办- | score=0.5874769337259496 adjust=-0.1 adjusted=0.4874769337259496 status=NO_ANCHOR_EVIDENCE matched=[]

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Anchors: ['冰箱冷冻室', '电脑']
- Baseline Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Experiment Top2: ['更新Windows 8.1过程中，提示“无法更新到Windows 8.1”', '如何设置显示屏幕的亮度（电脑屏幕亮度怎么调）']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 更新Windows 8.1过程中，提示“无法更新到Windows 8.1” | score=0.5226976597901252 adjust=-0.1 adjusted=0.4226976597901252 status=NO_ANCHOR_EVIDENCE matched=[]
  - 如何设置显示屏幕的亮度（电脑屏幕亮度怎么调） | score=0.5050323858514126 adjust=-0.1 adjusted=0.40503238585141266 status=NO_ANCHOR_EVIDENCE matched=[]

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Anchors: ['折叠屏铰链']
- Baseline Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Experiment Top2: ['同禧有内置音箱的机型如何屏蔽内置音箱', '31018765A 扬天T系列用户手册 V1.0']
- Rejected: True reason=ANCHOR_EVIDENCE_MISSING
  - 同禧有内置音箱的机型如何屏蔽内置音箱 | score=0.7023231102412939 adjust=-0.1 adjusted=0.6023231102412939 status=NO_ANCHOR_EVIDENCE matched=[]
  - 31018765A 扬天T系列用户手册 V1.0 | score=0.6448112804789083 adjust=-0.1 adjusted=0.5448112804789084 status=NO_ANCHOR_EVIDENCE matched=[]
