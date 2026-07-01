from typing import Any, Dict, List

from app.infrastructure.logging.logger import logger
from app.repositories.session_repository import session_repository


Message = Dict[str, Any]


class SessionService:
    """Chat history service.

    Runtime storage is MySQL. JSON files under user_memories are only a legacy
    migration source and are not read or written by this service.
    """

    DEFAULT_SESSION_ID = "default_session"

    def __init__(self):
        self._repo = session_repository

    def prepare_history(
        self,
        user_id: str,
        session_id: str,
        user_input: str,
        max_turn: int = 3,
    ) -> List[Message]:
        full_history = self.prepare_full_history(user_id, session_id, user_input)
        return self.build_prompt_history(full_history, max_turn=max_turn)

    def prepare_full_history(self, user_id: str, session_id: str, user_input: str) -> List[Message]:
        full_history = self.load_history(user_id, session_id)
        full_history.append({"role": "user", "content": user_input})
        return full_history

    def build_prompt_history(self, full_history: List[Message], max_turn: int = 3) -> List[Message]:
        return self._truncate_history(full_history, max_turn=max_turn)

    def load_history(self, user_id: str, session_id: str) -> List[Message]:
        target_session_id = session_id if session_id else self.DEFAULT_SESSION_ID
        try:
            session_history = self._repo.load_session(user_id, target_session_id)
        except Exception as exc:
            logger.error(
                "failed to load chat history user_id=%s session_id=%s: %s",
                user_id,
                target_session_id,
                exc.__class__.__name__,
            )
            return [{"role": "system", "content": "failed to load chat history"}]

        if session_history is None:
            return self._init_system_msg_instruct(target_session_id)
        return session_history

    def save_history(self, user_id: str, session_id: str, chat_history: List[Message]) -> None:
        if chat_history is None:
            return
        target_session_id = session_id if session_id else self.DEFAULT_SESSION_ID
        try:
            self._repo.save_session(user_id, target_session_id, chat_history)
        except Exception as exc:
            logger.error(
                "failed to save chat history user_id=%s session_id=%s: %s",
                user_id,
                target_session_id,
                exc.__class__.__name__,
            )
            return

    def get_all_sessions_memory(self, user_id: str) -> List[Dict[str, Any]]:
        raw_sessions = self._repo.get_all_sessions_metadata(user_id)
        formatted_sessions = []

        for session_id, create_time, data_or_error in raw_sessions:
            session_item: Dict[str, Any] = {
                "session_id": session_id,
                "create_time": create_time,
            }

            if isinstance(data_or_error, Exception):
                logger.error("failed to read chat session %s: %s", session_id, str(data_or_error))
                session_item.update({
                    "memory": [],
                    "total_messages": 0,
                    "error": "unable to read chat session",
                })
            else:
                user_visible_memory = [
                    msg for msg in data_or_error if msg.get("role") != "system"
                ]
                session_item.update({
                    "memory": user_visible_memory,
                    "total_messages": len(user_visible_memory),
                })

            formatted_sessions.append(session_item)

        formatted_sessions.sort(
            key=lambda item: item.get("create_time") or "",
            reverse=True,
        )
        return formatted_sessions

    def _init_system_msg_instruct(self, session_id: str) -> List[Message]:
        return [{
            "role": "system",
            "content": (
                "You are a memory-aware assistant. Answer the user based on the "
                f"conversation context when useful. Session ID: {session_id}"
            ),
        }]

    def _truncate_history(self, chat_history: List[Message], max_turn: int = 3) -> List[Message]:
        system_messages = [msg for msg in chat_history if msg.get("role") == "system"]
        non_system_messages = [msg for msg in chat_history if msg.get("role") != "system"]
        return system_messages + non_system_messages[-max_turn * 2:]


session_service = SessionService()
