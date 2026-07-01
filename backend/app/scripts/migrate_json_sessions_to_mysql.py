import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.infrastructure.logging.logger import logger
from app.repositories.session_repository import SessionRepository, session_repository


APP_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = APP_DIR / "user_memories"


@dataclass
class MigrationStats:
    scanned: int = 0
    valid: int = 0
    imported: int = 0
    skipped_existing: int = 0
    skipped_invalid: int = 0
    failed: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate legacy JSON chat sessions to MySQL.")
    parser.add_argument("--apply", action="store_true", help="Write valid sessions into MySQL.")
    parser.add_argument("--dry-run", action="store_true", help="Scan only. This is the default.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing MySQL sessions.")
    parser.add_argument("--user-id", help="Only migrate one user_id directory.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT), help="Legacy user_memories root.")
    return parser.parse_args()


def iter_session_files(source_root: Path, user_id: str | None = None) -> Iterable[tuple[str, str, Path]]:
    if user_id:
        user_dir = source_root / user_id
        user_dirs = [user_dir] if user_dir.exists() and user_dir.is_dir() else []
    else:
        user_dirs = [path for path in source_root.iterdir() if path.is_dir()] if source_root.exists() else []

    for user_dir in sorted(user_dirs):
        for file_path in sorted(user_dir.glob("*.json")):
            yield user_dir.name, file_path.stem, file_path


def load_json_messages(file_path: Path) -> list[dict[str, str]]:
    with file_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise ValueError("session JSON root must be a list")

    messages: list[dict[str, str]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict) or "role" not in item or "content" not in item:
            raise ValueError(f"message {index} must contain role and content")
        messages.append({
            "role": str(item["role"]),
            "content": str(item["content"]),
        })
    return messages


def file_created_at(file_path: Path) -> datetime:
    try:
        return datetime.fromtimestamp(file_path.stat().st_ctime)
    except OSError as exc:
        logger.warning("cannot read JSON file create time name=%s: %s", file_path.name, exc.__class__.__name__)
        return datetime.now()


def migrate(
    *,
    repo: SessionRepository = session_repository,
    source_root: Path = DEFAULT_SOURCE_ROOT,
    apply: bool = False,
    overwrite: bool = False,
    user_id: str | None = None,
) -> MigrationStats:
    stats = MigrationStats()
    for current_user_id, session_id, file_path in iter_session_files(source_root, user_id=user_id):
        stats.scanned += 1
        try:
            messages = load_json_messages(file_path)
            stats.valid += 1
        except Exception as exc:
            stats.skipped_invalid += 1
            logger.error("skip invalid JSON session file=%s: %s", file_path.name, exc.__class__.__name__)
            continue

        try:
            exists = repo.load_session(current_user_id, session_id) is not None
            if exists and not overwrite:
                stats.skipped_existing += 1
                continue

            if apply:
                created_at = file_created_at(file_path)
                repo.save_session(
                    current_user_id,
                    session_id,
                    messages,
                    created_at=created_at,
                    updated_at=created_at,
                    overwrite_created_at=overwrite,
                )
                stats.imported += 1
        except Exception as exc:
            stats.failed += 1
            logger.error(
                "failed to migrate JSON session user_id=%s session_id=%s: %s",
                current_user_id,
                session_id,
                exc.__class__.__name__,
            )
            continue

    return stats


def main() -> None:
    args = parse_args()
    apply = bool(args.apply)
    stats = migrate(
        source_root=Path(args.source_root),
        apply=apply,
        overwrite=bool(args.overwrite),
        user_id=args.user_id,
    )
    mode = "apply" if apply else "dry-run"
    print(
        "mode={mode} scanned={scanned} valid={valid} imported={imported} "
        "skipped_existing={skipped_existing} skipped_invalid={skipped_invalid} failed={failed}".format(
            mode=mode,
            scanned=stats.scanned,
            valid=stats.valid,
            imported=stats.imported,
            skipped_existing=stats.skipped_existing,
            skipped_invalid=stats.skipped_invalid,
            failed=stats.failed,
        )
    )


if __name__ == "__main__":
    main()
