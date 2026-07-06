# Alias Candidate Suggestions

This report was generated from existing offline RAG evaluation reports only.

## Summary

- Total candidates: 15
- New suggestions: 5
- Existing aliases detected: 10
- High confidence: 11
- Medium confidence: 3
- Low confidence: 1

## Top New Suggestions

| Rank | Canonical | New Aliases | Score | Risk | Evidence Cases |
| --- | --- | --- | ---: | --- | --- |
| 1 | Windows 7 | Windows 7, win7, Win7 | 1.0000 | low | case_007, case_018, case_022, case_031, case_038, case_042, case_045, case_082 |
| 2 | Windows XP | windows xp, Windows XP, xp, XP | 1.0000 | low | case_003, case_004, case_011, case_022, case_037, case_047, case_048, case_050 |
| 3 | 打印机 | Printer, printer, 打印机 | 1.0000 | low | case_022, case_041, case_058, case_082 |
| 4 | PowerPoint | powerpoint, PowerPoint, PPT, ppt | 0.6800 | medium | case_025 |
| 5 | 任务栏输入法图标 | 任务栏输入法图标, 输入法图标 | 0.5600 | medium | case_080 |

## Risky Candidates Not Recommended Directly

- None

## Existing Aliases Detected

- Lenovo: Lenovo, lenovo, LENOVO, 联想电脑, 联想
- Wi-Fi: wireless, Wireless, Wi-Fi, WiFi, WIFI, wifi, wlan, WLAN, 无线网络, 无线连接, 无线网
- Windows: Windows10, windows10, windows11, Windows11, windows, Windows, win10, Win10, Win11, win11
- BIOS: BIOS, bios, UEFI, uefi
- Word: Microsoft Word, docx, word, WORD, Word, doc
- 蓝牙: Bluetooth, bluetooth, 蓝牙设备, BT, bt, 蓝牙
- Excel: excel, EXCEL, Excel, xlsx, xls
- Outlook: OUTLOOK, outlook, Outlook
- Microsoft Office: Microsoft Office, Microsoft 365, microsoft365, Office365, office365, Office, office, O365, o365
- ThinkPad: Think Pad, think pad, ThinkPad, tp, TP

## Notes

- This script does not modify `query_aliases.yaml`.
- This script does not call network, Embedding, Reranker, Chroma, LLM, or MCP services.
- Candidates require manual review before a formal alias config update.
