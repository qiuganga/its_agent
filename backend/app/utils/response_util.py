import uuid
from datetime import datetime
from typing import Optional

# 引入新的模型名称
from app.schemas.response import (
    StreamPacket,
    TextMessageBody,
    ToolEventMessageBody,
    FinishMessageBody,
    StreamStatus,
    PacketMeta,
    ContentKind
)


class ResponseFactory:
    """
    SSE 响应构建工厂
    """

    @staticmethod
    def build_text(text: str, kind: ContentKind) -> StreamPacket:
        """
        构建文本/推理片段响应
        """
        body = TextMessageBody(
            text=text,
            kind=kind
        )

        return StreamPacket(
            id=str(uuid.uuid4()),
            content=body,
            status=StreamStatus.IN_PROGRESS,
            metadata=PacketMeta(createTime=str(datetime.now()))
        )

    @staticmethod
    def build_tool_event(event: dict) -> StreamPacket:
        """
        Build a safe tool event packet for SSE.
        """
        safe_event = {
            key: event.get(key)
            for key in (
                "kind",
                "run_id",
                "tool_call_id",
                "sequence",
                "tool_name",
                "status",
                "ok",
                "error_code",
                "result_item_count",
                "latency_ms",
                "schema_version",
                "provider",
                "retryable",
                "argument_fingerprint",
                "timestamp_ms",
            )
            if key in event
        }
        kind = safe_event.get("kind")
        content_kind = ContentKind.TOOL_RESULT if kind == "TOOL_RESULT" else ContentKind.TOOL_STARTED
        tool_name = safe_event.get("tool_name") or "unknown"
        if content_kind == ContentKind.TOOL_STARTED:
            text = f"正在调用 {tool_name} 工具..."
        else:
            ok = bool(safe_event.get("ok"))
            status = safe_event.get("status") or ("completed" if ok else "failed")
            latency_ms = safe_event.get("latency_ms")
            item_count = safe_event.get("result_item_count")
            error_code = safe_event.get("error_code")
            if ok:
                count_text = item_count if item_count is not None else 0
                latency_text = latency_ms if latency_ms is not None else 0
                text = f"{tool_name} 工具调用完成，返回 {count_text} 条，用时 {latency_text} ms"
            else:
                text = f"{tool_name} 工具调用{status}，错误码 {error_code or 'UNKNOWN'}"

        body = ToolEventMessageBody(
            kind=content_kind,
            text=text,
            event=safe_event,
        )

        return StreamPacket(
            id=str(uuid.uuid4()),
            content=body,
            status=StreamStatus.IN_PROGRESS,
            metadata=PacketMeta(createTime=str(datetime.now()))
        )

    @staticmethod
    def build_finish(message_id: Optional[str] = None) -> StreamPacket:
        """
        构建结束信号响应
        """
        if message_id is None:
            message_id = str(uuid.uuid4())

        return StreamPacket(
            id=message_id,
            content=FinishMessageBody(),
            status=StreamStatus.FINISHED,
            metadata=PacketMeta(createTime=str(datetime.now()))
        )
