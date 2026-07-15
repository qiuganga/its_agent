from enum import Enum
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field


class ContentKind(str, Enum):
    THINKING = "THINKING"
    PROCESS = "PROCESS"
    ANSWER = "ANSWER"
    CLARIFICATION = "CLARIFICATION"
    TOOL_STARTED = "TOOL_STARTED"
    TOOL_RESULT = "TOOL_RESULT"


class StreamStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class StopReason(str, Enum):
    NORMAL = "NORMAL"
    MAX_TOKENS = "MAX_TOKENS"
    ERROR = "ERROR"


class MessageBody(BaseModel):
    contentType: str


class TextMessageBody(MessageBody):
    contentType: Literal["sagegpt/text"] = "sagegpt/text"
    text: str = Field(default="", description="Text content")
    kind: ContentKind = Field(..., description="THINKING/PROCESS/ANSWER")


class ToolEventMessageBody(MessageBody):
    contentType: Literal["sagegpt/tool_event"] = "sagegpt/tool_event"
    kind: ContentKind = Field(..., description="TOOL_STARTED/TOOL_RESULT")
    text: str = Field(default="", description="Safe display text")
    event: dict[str, Any] = Field(default_factory=dict, description="Safe tool event payload")


class ClarificationMessageBody(MessageBody):
    contentType: Literal["sagegpt/clarification"] = "sagegpt/clarification"
    kind: ContentKind = ContentKind.CLARIFICATION
    text: str
    clarification: dict[str, Any] = Field(default_factory=dict)


class FinishMessageBody(MessageBody):
    contentType: Literal["sagegpt/finish"] = "sagegpt/finish"


class PacketMeta(BaseModel):
    createTime: str
    finishReason: Optional[StopReason] = None
    errorMessage: Optional[str] = None


class StreamPacket(BaseModel):
    id: str
    content: Union[TextMessageBody, ToolEventMessageBody, ClarificationMessageBody, FinishMessageBody]
    status: StreamStatus
    metadata: PacketMeta
