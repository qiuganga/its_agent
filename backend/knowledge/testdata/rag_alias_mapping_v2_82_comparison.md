# Alias Mapping v2 A/B Comparison

- Baseline: `D:\sgg-agent\code\its_multi_agent\backend\knowledge\testdata\rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker.json`
- Alias v2: `D:\sgg-agent\code\its_multi_agent\backend\knowledge\testdata\rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker_alias_v2.json`

## Metrics

| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Top1 weak hit | 37 | 37 | 0 |
| Top2 weak hit | 38 | 38 | 0 |
| False rejected answerable | 15 | 14 | -1 |
| Accepted count | - | - | 1 |
| Rejected count | - | - | -1 |
| Top1 changed cases | - | - | 8 |
| Top2 changed cases | - | - | 14 |
| Alias applied cases | - | - | 7 |
| New alias hit cases | - | - | 6 |
| Source id missing before rerank | - | - | 0 |

## Classification Counts

- ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW: 13
- ALIAS_IMPROVED: 1
- ALIAS_NO_EFFECT: 68

## Improved Cases

- case_082 | ALIAS_IMPROVED | aliases=打印机 | top2_changed=True | before=How to install printer hardware driver on Windows | after=How to install 打印机 hardware driver on Windows

## Regression Cases

- None

## Changed But Needs Manual Review

- case_038 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=Windows 7 | top2_changed=True | before=Configure wireless network on Windows 7 | after=Configure wireless network on Windows 7
- case_039 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=How to turn on Bluetooth module | after=How to turn on 蓝牙 module
- case_040 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=How to add Bluetooth device | after=How to add 蓝牙 device
- case_041 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=打印机 | top2_changed=True | before=Moon base printer connect to quantum network | after=Moon base 打印机 connect to quantum network
- case_042 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Foldable screen hinge replacement for tablet | after=Foldable screen hinge replacement for tablet
- case_046 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Quantum network router configuration | after=Quantum network router configuration
- case_048 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Freezer compartment fan stopped spinning | after=Freezer compartment fan stopped spinning
- case_051 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Mars projector access quantum network | after=Mars projector access quantum network
- case_057 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Adjust screen brightness | after=Adjust screen brightness
- case_062 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Washing machine shakes during spin cycle | after=Washing machine shakes during spin cycle
- case_064 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Gas stove turns off immediately after ignition | after=Gas stove turns off immediately after ignition
- case_074 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Bluetooth device cannot be found,not infrared or Wi-Fi | after=蓝牙 device cannot be found,not infrared or Wi-Fi
- case_077 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=- | top2_changed=True | before=Generic blue screen cannot enter system but no error code | after=Generic blue screen cannot enter system but no error code

## New Alias Focus Cases

- case_022 | ALIAS_NO_EFFECT | aliases=打印机 | top2_changed=False | before=火星基地打印机怎么连接量子网络 | after=火星基地打印机怎么连接量子网络
- case_031 | ALIAS_NO_EFFECT | aliases=Windows 7 | top2_changed=False | before=Windows 7 group policy client service failed login | after=Windows 7 group policy client service failed login
- case_037 | ALIAS_NO_EFFECT | aliases=Windows XP | top2_changed=False | before=Windows XP safe mode startup | after=Windows XP safe mode startup
- case_038 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=Windows 7 | top2_changed=True | before=Configure wireless network on Windows 7 | after=Configure wireless network on Windows 7
- case_041 | ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW | aliases=打印机 | top2_changed=True | before=Moon base printer connect to quantum network | after=Moon base 打印机 connect to quantum network
- case_082 | ALIAS_IMPROVED | aliases=打印机 | top2_changed=True | before=How to install printer hardware driver on Windows | after=How to install 打印机 hardware driver on Windows

> This report does not change production retrieval logic.
