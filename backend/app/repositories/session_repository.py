from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from app.infrastructure.database.database_pool import pool
from app.infrastructure.logging.logger import logger


Message = Dict[str, Any]
SessionMetadata = Tuple[str, str, Union[List[Message], Exception]]


class SessionRepository:
    """MySQL-backed chat session repository."""

    def __init__(self, db_pool=None):
        self._pool = db_pool or pool

    def load_session(self, user_id: str, session_id: str) -> Optional[List[Message]]:
        connection = self._pool.connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id
                FROM agent_chat_sessions
                WHERE user_id = %s AND session_id = %s
                """,
                (user_id, session_id),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            chat_session_id = self._first_column(row)
            cursor.execute(
                """
                SELECT role, content
                FROM agent_chat_messages
                WHERE chat_session_id = %s
                ORDER BY message_order ASC
                """,
                (chat_session_id,),
            )
            return [
                {"role": self._column(row, 0, "role"), "content": self._column(row, 1, "content")}
                for row in cursor.fetchall()
            ]
        finally:
            self._close_cursor(cursor)
            connection.close()

    def save_session(
        self,
        user_id: str,
        session_id: str,
        data: List[Message],
        *,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        overwrite_created_at: bool = False,
    ) -> None:
        connection = self._pool.connection()
        cursor = None
        try:
            cursor = connection.cursor()
            now = updated_at or datetime.now()
            created_at_value = created_at or now
            cursor.execute(
                """
                INSERT INTO agent_chat_sessions (user_id, session_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    created_at = IF(%s, VALUES(created_at), created_at),
                    updated_at = VALUES(updated_at)
                """,
                (user_id, session_id, created_at_value, now, overwrite_created_at),
            )
            cursor.execute(
                """
                SELECT id
                FROM agent_chat_sessions
                WHERE user_id = %s AND session_id = %s
                """,
                (user_id, session_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("chat session was not created")

            chat_session_id = self._first_column(row)
            cursor.execute(
                "DELETE FROM agent_chat_messages WHERE chat_session_id = %s",
                (chat_session_id,),
            )
            rows = [
                (
                    chat_session_id,
                    index,
                    str(message.get("role", "")),
                    str(message.get("content", "")),
                    now,
                )
                for index, message in enumerate(data)
            ]
            if rows:
                cursor.executemany(
                    """
                    INSERT INTO agent_chat_messages
                        (chat_session_id, message_order, role, content, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    rows,
                )
            cursor.execute(
                "UPDATE agent_chat_sessions SET updated_at = %s WHERE id = %s",
                (now, chat_session_id),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            logger.exception(
                "failed to save chat session user_id=%s session_id=%s",
                user_id,
                session_id,
            )
            raise
        finally:
            self._close_cursor(cursor)
            connection.close()

    def get_all_sessions_metadata(self, user_id: str) -> List[SessionMetadata]:
        connection = self._pool.connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, session_id, updated_at
                FROM agent_chat_sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC
                """,
                (user_id,),
            )
            sessions = cursor.fetchall()
            if not sessions:
                return []

            session_ids = [self._column(row, 0, "id") for row in sessions]
            placeholders = ", ".join(["%s"] * len(session_ids))
            cursor.execute(
                f"""
                SELECT chat_session_id, role, content, message_order
                FROM agent_chat_messages
                WHERE chat_session_id IN ({placeholders})
                ORDER BY chat_session_id ASC, message_order ASC
                """,
                tuple(session_ids),
            )
            messages_by_session: dict[int, List[Message]] = {int(session_id): [] for session_id in session_ids}
            for row in cursor.fetchall():
                chat_session_id = int(self._column(row, 0, "chat_session_id"))
                messages_by_session.setdefault(chat_session_id, []).append({
                    "role": self._column(row, 1, "role"),
                    "content": self._column(row, 2, "content"),
                })

            results: List[SessionMetadata] = []
            for row in sessions:
                chat_session_id = int(self._column(row, 0, "id"))
                session_id = str(self._column(row, 1, "session_id"))
                updated_at = self._column(row, 2, "updated_at")
                results.append((
                    session_id,
                    self._format_datetime(updated_at),
                    messages_by_session.get(chat_session_id, []),
                ))
            return results
        except Exception as exc:
            logger.exception("failed to load session metadata user_id=%s", user_id)
            return []
        finally:
            self._close_cursor(cursor)
            connection.close()

    @staticmethod
    def _column(row: Any, index: int, name: str) -> Any:
        if isinstance(row, dict):
            return row[name]
        return row[index]

    @classmethod
    def _first_column(cls, row: Any) -> Any:
        if isinstance(row, dict):
            return next(iter(row.values()))
        return row[0]

    @staticmethod
    def _format_datetime(value: Any) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)

    @staticmethod
    def _close_cursor(cursor: Any) -> None:
        if cursor is not None and hasattr(cursor, "close"):
            cursor.close()


session_repository = SessionRepository()
