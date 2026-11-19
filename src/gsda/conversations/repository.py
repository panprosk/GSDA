from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    project_id TEXT NOT NULL,
    mode_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user','assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, id);
"""


@dataclass(frozen=True)
class Conversation:
    id: str
    title: str
    project_id: str
    mode_id: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class Message:
    id: int
    conversation_id: str
    role: str
    content: str
    created_at: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class ConversationRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as c:
            c.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_conversation(self, project_id: str, mode_id: str, title: str = "Νέα συνομιλία") -> Conversation:
        cid, now = uuid.uuid4().hex, _now()
        conn = self._connect()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO conversations VALUES (?,?,?,?,?,?)",
                    (cid, title, project_id, mode_id, now, now),
                )
        finally:
            conn.close()
        return Conversation(cid, title, project_id, mode_id, now, now)

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM conversations WHERE id=?", (conversation_id,)).fetchone()
        finally:
            conn.close()
        return Conversation(**dict(row)) if row else None

    def list_conversations(self, project_id: Optional[str] = None) -> List[Conversation]:
        sql, args = "SELECT * FROM conversations", ()
        if project_id:
            sql, args = sql + " WHERE project_id=?", (project_id,)
        sql += " ORDER BY updated_at DESC, rowid DESC"
        conn = self._connect()
        try:
            rows = conn.execute(sql, args).fetchall()
        finally:
            conn.close()
        return [Conversation(**dict(r)) for r in rows]

    def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        now = _now()
        conn = self._connect()
        try:
            with conn:
                cur = conn.execute(
                    "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?,?,?,?)",
                    (conversation_id, role, content, now),
                )
                conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conversation_id))
            mid = cur.lastrowid
        finally:
            conn.close()
        return Message(mid, conversation_id, role, content, now)

    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Message]:
        """Χρονολογική σειρά· με limit επιστρέφει τα τελευταία N."""
        conn = self._connect()
        try:
            if limit is None:
                rows = conn.execute(
                    "SELECT * FROM messages WHERE conversation_id=? ORDER BY id", (conversation_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM (SELECT * FROM messages WHERE conversation_id=? ORDER BY id DESC LIMIT ?) "
                    "ORDER BY id",
                    (conversation_id, max(limit, 0)),
                ).fetchall()
        finally:
            conn.close()
        return [Message(**dict(r)) for r in rows]

    def delete_conversation(self, conversation_id: str) -> bool:
        """Διαγράφει τη συνομιλία και (μέσω ON DELETE CASCADE) όλα τα μηνύματά της."""
        conn = self._connect()
        try:
            with conn:
                cur = conn.execute("DELETE FROM conversations WHERE id=?", (conversation_id,))
        finally:
            conn.close()
        return cur.rowcount > 0

    def set_title(self, conversation_id: str, title: str) -> None:
        conn = self._connect()
        try:
            with conn:
                conn.execute("UPDATE conversations SET title=? WHERE id=?", (title, conversation_id))
        finally:
            conn.close()
