import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from app.repositories.session_repository import SessionRepository
from app.scripts.migrate_json_sessions_to_mysql import migrate
from app.services.session_service import SessionService


class FakeDatabase:
    def __init__(self):
        self.next_session_id = 1
        self.sessions = {}
        self.messages = {}


class FakePool:
    def __init__(self):
        self.db = FakeDatabase()

    def connection(self):
        return FakeConnection(self.db)


class FakeConnection:
    def __init__(self, db):
        self.db = db
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        return FakeCursor(self.db)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


class FakeCursor:
    def __init__(self, db):
        self.db = db
        self._results = []
        self.closed = False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.lower().split())
        if normalized.startswith("insert into agent_chat_sessions"):
            user_id, session_id, created_at, updated_at, overwrite_created_at = params
            key = (user_id, session_id)
            if key not in self.db.sessions:
                self.db.sessions[key] = {
                    "id": self.db.next_session_id,
                    "user_id": user_id,
                    "session_id": session_id,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
                self.db.messages[self.db.next_session_id] = []
                self.db.next_session_id += 1
            else:
                if overwrite_created_at:
                    self.db.sessions[key]["created_at"] = created_at
                self.db.sessions[key]["updated_at"] = updated_at
            self._results = []
        elif normalized.startswith("select id from agent_chat_sessions"):
            user_id, session_id = params
            row = self.db.sessions.get((user_id, session_id))
            self._results = [(row["id"],)] if row else []
        elif normalized.startswith("delete from agent_chat_messages"):
            chat_session_id = params[0]
            self.db.messages[chat_session_id] = []
            self._results = []
        elif normalized.startswith("update agent_chat_sessions set updated_at"):
            updated_at, chat_session_id = params
            for row in self.db.sessions.values():
                if row["id"] == chat_session_id:
                    row["updated_at"] = updated_at
                    break
            self._results = []
        elif normalized.startswith("select role, content from agent_chat_messages"):
            chat_session_id = params[0]
            rows = sorted(self.db.messages.get(chat_session_id, []), key=lambda item: item["message_order"])
            self._results = [(row["role"], row["content"]) for row in rows]
        elif normalized.startswith("select id, session_id, updated_at from agent_chat_sessions"):
            user_id = params[0]
            rows = [row for row in self.db.sessions.values() if row["user_id"] == user_id]
            rows.sort(key=lambda row: row["updated_at"], reverse=True)
            self._results = [(row["id"], row["session_id"], row["updated_at"]) for row in rows]
        elif normalized.startswith("select chat_session_id, role, content, message_order"):
            chat_session_ids = set(params)
            rows = []
            for chat_session_id in chat_session_ids:
                rows.extend(self.db.messages.get(chat_session_id, []))
            rows.sort(key=lambda row: (row["chat_session_id"], row["message_order"]))
            self._results = [
                (row["chat_session_id"], row["role"], row["content"], row["message_order"])
                for row in rows
            ]
        else:
            raise AssertionError(f"unexpected SQL: {sql}")

    def executemany(self, sql, rows):
        normalized = " ".join(sql.lower().split())
        if not normalized.startswith("insert into agent_chat_messages"):
            raise AssertionError(f"unexpected executemany SQL: {sql}")
        for chat_session_id, message_order, role, content, created_at in rows:
            self.db.messages.setdefault(chat_session_id, []).append({
                "chat_session_id": chat_session_id,
                "message_order": message_order,
                "role": role,
                "content": content,
                "created_at": created_at,
            })

    def fetchone(self):
        return self._results[0] if self._results else None

    def fetchall(self):
        return list(self._results)

    def close(self):
        self.closed = True


class MysqlSessionRepositoryTests(unittest.TestCase):
    def make_repo(self):
        return SessionRepository(FakePool())

    def test_empty_session_load_returns_none(self):
        repo = self.make_repo()
        self.assertIsNone(repo.load_session("u1", "s1"))

    def test_save_and_load_preserves_message_order(self):
        repo = self.make_repo()
        messages = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]
        repo.save_session("u1", "s1", messages)
        self.assertEqual(repo.load_session("u1", "s1"), messages)

    def test_unicode_emoji_newline_and_long_text_survive_roundtrip(self):
        repo = self.make_repo()
        long_text = "中文🙂\n" + ("long text " * 1000)
        messages = [{"role": "user", "content": long_text}]
        repo.save_session("u1", "s1", messages)
        self.assertEqual(repo.load_session("u1", "s1"), messages)

    def test_second_save_replaces_old_messages_without_duplicates(self):
        repo = self.make_repo()
        repo.save_session("u1", "s1", [{"role": "user", "content": "old"}])
        repo.save_session("u1", "s1", [{"role": "assistant", "content": "new"}])
        self.assertEqual(repo.load_session("u1", "s1"), [{"role": "assistant", "content": "new"}])

    def test_same_session_id_is_isolated_between_users(self):
        repo = self.make_repo()
        repo.save_session("u1", "same", [{"role": "user", "content": "u1"}])
        repo.save_session("u2", "same", [{"role": "user", "content": "u2"}])
        self.assertEqual(repo.load_session("u1", "same")[0]["content"], "u1")
        self.assertEqual(repo.load_session("u2", "same")[0]["content"], "u2")

    def test_metadata_is_returned_by_updated_at_desc(self):
        repo = self.make_repo()
        older = datetime(2026, 1, 1, 10, 0, 0)
        newer = older + timedelta(hours=1)
        repo.save_session("u1", "old", [{"role": "user", "content": "old"}], created_at=older, updated_at=older)
        repo.save_session("u1", "new", [{"role": "user", "content": "new"}], created_at=newer, updated_at=newer)
        metadata = repo.get_all_sessions_metadata("u1")
        self.assertEqual([item[0] for item in metadata], ["new", "old"])
        self.assertEqual(metadata[0][2], [{"role": "user", "content": "new"}])


class SessionServiceHistoryTests(unittest.TestCase):
    def test_prompt_history_is_truncated_but_full_history_is_not(self):
        service = SessionService()
        full_history = [{"role": "system", "content": "sys"}]
        for i in range(5):
            full_history.append({"role": "user", "content": f"u{i}"})
            full_history.append({"role": "assistant", "content": f"a{i}"})

        prompt_history = service.build_prompt_history(full_history, max_turn=3)

        self.assertEqual(len(full_history), 11)
        self.assertEqual(len(prompt_history), 7)
        self.assertEqual(prompt_history[0], {"role": "system", "content": "sys"})
        self.assertEqual([msg["content"] for msg in prompt_history[1:]], ["u2", "a2", "u3", "a3", "u4", "a4"])


class JsonMigrationTests(unittest.TestCase):
    def write_json_session(self, root: Path, user_id: str, session_id: str, messages):
        user_dir = root / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / f"{session_id}.json"
        file_path.write_text(json.dumps(messages, ensure_ascii=False), encoding="utf-8")
        return file_path

    def test_dry_run_does_not_write_database(self):
        repo = self.make_repo()
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_session(Path(tmpdir), "u1", "s1", [{"role": "user", "content": "hello"}])
            stats = migrate(repo=repo, source_root=Path(tmpdir), apply=False)

        self.assertEqual(stats.valid, 1)
        self.assertEqual(stats.imported, 0)
        self.assertIsNone(repo.load_session("u1", "s1"))

    def test_apply_imports_json_session(self):
        repo = self.make_repo()
        messages = [{"role": "user", "content": "hello"}]
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_session(Path(tmpdir), "u1", "s1", messages)
            stats = migrate(repo=repo, source_root=Path(tmpdir), apply=True)

        self.assertEqual(stats.imported, 1)
        self.assertEqual(repo.load_session("u1", "s1"), messages)

    def test_repeated_apply_skips_existing_without_duplicates(self):
        repo = self.make_repo()
        messages = [{"role": "user", "content": "hello"}]
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_session(Path(tmpdir), "u1", "s1", messages)
            first = migrate(repo=repo, source_root=Path(tmpdir), apply=True)
            second = migrate(repo=repo, source_root=Path(tmpdir), apply=True)

        self.assertEqual(first.imported, 1)
        self.assertEqual(second.skipped_existing, 1)
        self.assertEqual(repo.load_session("u1", "s1"), messages)

    def test_existing_mysql_session_is_not_overwritten_by_default(self):
        repo = self.make_repo()
        repo.save_session("u1", "s1", [{"role": "user", "content": "mysql"}])
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_json_session(Path(tmpdir), "u1", "s1", [{"role": "user", "content": "json"}])
            stats = migrate(repo=repo, source_root=Path(tmpdir), apply=True)

        self.assertEqual(stats.skipped_existing, 1)
        self.assertEqual(repo.load_session("u1", "s1"), [{"role": "user", "content": "mysql"}])

    def make_repo(self):
        return SessionRepository(FakePool())


if __name__ == "__main__":
    unittest.main()
