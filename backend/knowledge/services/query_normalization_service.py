import re


NORMALIZATION_RULES = [
    ("屏幕不亮但风扇会转，电脑黑屏", "黑屏但风扇会转"),
    ("屏幕不亮但风扇会转,电脑黑屏", "黑屏但风扇会转"),
    ("屏幕没显示但风扇会转，电脑黑屏", "黑屏但风扇会转"),
    ("屏幕没显示但风扇会转,电脑黑屏", "黑屏但风扇会转"),
    ("屏幕不亮但风扇会转", "黑屏但风扇会转"),
    ("屏幕没显示但风扇会转", "黑屏但风扇会转"),
    ("系统卡死没有响应", "系统无响应"),
    ("电脑卡死没有响应", "系统无响应"),
    ("卡死没有响应", "系统无响应"),
    ("搜不到蓝牙设备", "蓝牙设备无法被发现"),
    ("搜不到蓝牙", "蓝牙设备无法被发现"),
    ("连不上蓝牙设备", "蓝牙连接失败"),
    ("连不上蓝牙", "蓝牙连接失败"),
    ("开机没反应", "无法开机"),
    ("开不了机", "无法开机"),
    ("开不开", "无法开机"),
    ("屏幕没显示", "黑屏"),
    ("屏幕不亮", "黑屏"),
    ("显示器不亮", "黑屏"),
    ("死机", "系统无响应"),
    ("卡住", "系统无响应"),
    ("卡死", "系统无响应"),
    ("没声音", "无声音"),
    ("连不上网", "无法连接网络"),
]

ORDERED_NORMALIZATION_RULES = sorted(NORMALIZATION_RULES, key=lambda item: len(item[0]), reverse=True)

NORMALIZATION_CLEANUPS = [
    ("蓝牙设备无法被发现设备", "蓝牙设备无法被发现"),
    ("蓝牙连接失败设备", "蓝牙连接失败"),
    ("系统系统无响应", "系统无响应"),
    ("系统无响应没有响应", "系统无响应"),
    ("无响应没有响应", "无响应"),
    ("黑屏，电脑黑屏", "黑屏"),
    ("黑屏,电脑黑屏", "黑屏"),
    ("黑屏但风扇会转，电脑黑屏", "黑屏但风扇会转"),
    ("黑屏但风扇会转,电脑黑屏", "黑屏但风扇会转"),
]


class QueryNormalizationService:
    """Rule-based Chinese query normalization for RAG retrieval."""

    def normalize(self, original_question: str) -> str:
        normalized = self._normalize_text(original_question)
        for source, target in ORDERED_NORMALIZATION_RULES:
            normalized = normalized.replace(source, target)
        normalized = self._cleanup_duplicates(normalized)
        return self._normalize_text(normalized)

    @staticmethod
    def _normalize_text(text: str | None) -> str:
        normalized = re.sub(r"\s+", " ", (text or "").strip())
        normalized = re.sub(r"\s*([,，])\s*", r"\1", normalized)
        normalized = re.sub(r"[,，]{2,}", "，", normalized)
        return normalized.strip(" ,，")

    def _cleanup_duplicates(self, text: str) -> str:
        cleaned = text
        changed = True
        while changed:
            changed = False
            for source, target in NORMALIZATION_CLEANUPS:
                if source in cleaned:
                    cleaned = cleaned.replace(source, target)
                    changed = True
        return cleaned


query_normalization_service = QueryNormalizationService()
