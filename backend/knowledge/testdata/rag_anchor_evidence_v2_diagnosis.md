# Anchor Evidence v2 Diagnosis

- Status: `success`
- Generated at: `2026-07-05T20:29:19`
- Records: 17

## Reason Counts

- ALIAS_OR_LANGUAGE_GAP: 1
- CANDIDATE_RECALL_MISSING: 1
- HARD_ANCHOR_TOO_BROAD: 3
- OTHER: 4
- SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK: 8

## Records

### case_022
- Question: 火星基地打印机怎么连接量子网络
- Group: B_anchor_unanswerable / unanswerable
- Hard: ['量子网络']
- Soft: []
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: HARD_ANCHOR_TOO_BROAD
- Expected source in window: []
- Final Top2: []

### case_023
- Question: 冰箱冷冻室结霜导致电脑不能上网怎么办
- Group: B_anchor_unanswerable / unanswerable
- Hard: ['冰箱冷冻室']
- Soft: []
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: HARD_ANCHOR_TOO_BROAD
- Expected source in window: []
- Final Top2: []

### case_024
- Question: 手机屏幕进水后如何更换折叠屏铰链
- Group: B_anchor_unanswerable / unanswerable
- Hard: ['折叠屏铰链']
- Soft: []
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: HARD_ANCHOR_TOO_BROAD
- Expected source in window: []
- Final Top2: []

### case_025
- Question: PowerPoint 2007 cannot input Chinese
- Group: A_anchor_answerable / answerable
- Hard: []
- Soft: []
- Negative: []
- Rejection: None
- Diagnosis: CANDIDATE_RECALL_MISSING
- Expected source in window: []
- Final Top2: []

### case_026
- Question: How to modify Microsoft Word default style
- Group: A_anchor_answerable / answerable
- Hard: []
- Soft: ['Word']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_027
- Question: Outlook paragraph marks should be hidden
- Group: A_anchor_answerable / answerable
- Hard: []
- Soft: ['Outlook']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_030
- Question: Excel shows #VALUE! error
- Group: A_anchor_answerable / answerable
- Hard: []
- Soft: ['Excel']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_039
- Question: How to turn on Bluetooth module
- Group: A_anchor_answerable / answerable
- Hard: []
- Soft: ['Bluetooth', '蓝牙设备']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_040
- Question: How to add Bluetooth device
- Group: A_anchor_answerable / answerable
- Hard: []
- Soft: ['Bluetooth', '蓝牙设备']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_044
- Question: Blue screen error 0xDEADBEEF
- Group: B_anchor_unanswerable / unanswerable
- Hard: ['0xDEADBEEF']
- Soft: ['blue screen']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: OTHER
- Expected source in window: []
- Final Top2: []

### case_045
- Question: System error E9999 repair
- Group: B_anchor_unanswerable / unanswerable
- Hard: ['E9999']
- Soft: []
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: OTHER
- Expected source in window: []
- Final Top2: []

### case_049
- Question: Boot error 0xBADF00D cannot enter system
- Group: B_anchor_unanswerable / unanswerable
- Hard: ['0xBADF00D']
- Soft: ['startup']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: OTHER
- Expected source in window: []
- Final Top2: []

### case_050
- Question: Startup protocol error E654321
- Group: B_anchor_unanswerable / unanswerable
- Hard: ['E654321']
- Soft: ['startup']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: OTHER
- Expected source in window: []
- Final Top2: []

### case_071
- Question: Word inserted pictures become blank boxes, not black screen
- Group: E_confusing / answerable
- Hard: []
- Soft: ['Word']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_072
- Question: Screen brightness is too low, not Word blank picture
- Group: E_confusing / answerable
- Hard: []
- Soft: ['display brightness']
- Negative: ['Word']
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_074
- Question: Bluetooth device cannot be found, not infrared or Wi-Fi
- Group: E_confusing / answerable
- Hard: []
- Soft: ['Bluetooth', '蓝牙设备', 'Wi-Fi']
- Negative: []
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK
- Expected source in window: []
- Final Top2: []

### case_080
- Question: Taskbar input method icon disappeared, not Word input issue
- Group: E_confusing / answerable
- Hard: ['任务栏输入法图标']
- Soft: []
- Negative: ['Word']
- Rejection: ANCHOR_EVIDENCE_MISSING
- Diagnosis: ALIAS_OR_LANGUAGE_GAP
- Expected source in window: []
- Final Top2: []
