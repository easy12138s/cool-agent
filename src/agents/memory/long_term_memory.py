"""
长期记忆模块
"""

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MemoryItem:
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


class LongTermMemory:
    def __init__(self, *, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
              id TEXT PRIMARY KEY,
              content TEXT NOT NULL,
              metadata TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def add(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryItem:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content 不能为空")
        if metadata is None:
            metadata = {}
        item = MemoryItem(
            id=str(uuid4()),
            content=content,
            metadata=metadata,
            created_at=utc_now_iso(),
        )
        cur = self._conn.cursor()
        insert_sql = (
            "INSERT INTO memories (id, content, metadata, created_at) "
            "VALUES (?, ?, ?, ?)"
        )
        cur.execute(
            insert_sql,
            (
                item.id,
                item.content,
                json.dumps(item.metadata, ensure_ascii=False),
                item.created_at,
            ),
        )
        self._conn.commit()
        return item

    def get(self, memory_id: str) -> Optional[MemoryItem]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return MemoryItem(
            id=str(row["id"]),
            content=str(row["content"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=str(row["created_at"]),
        )

    def delete(self, memory_id: str) -> bool:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        changed = cur.rowcount or 0
        self._conn.commit()
        return changed > 0

    def list_recent(self, limit: int = 20) -> List[MemoryItem]:
        if limit <= 0:
            raise ValueError("limit 必须为正整数")
        cur = self._conn.cursor()
        cur.execute(
            "SELECT * FROM memories ORDER BY created_at DESC, rowid DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        items: List[MemoryItem] = []
        for row in rows:
            items.append(
                MemoryItem(
                    id=str(row["id"]),
                    content=str(row["content"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    created_at=str(row["created_at"]),
                )
            )
        return items

    @staticmethod
    def _score(query: str, content: str) -> float:
        q = {w for w in re.split(r"\W+", query.lower()) if w}
        if not q:
            return 0.0
        c = {w for w in re.split(r"\W+", content.lower()) if w}
        if not c:
            return 0.0
        return len(q & c) / len(q)

    def search(self, query: str, *, limit: int = 10) -> List[Dict[str, Any]]:
        if limit <= 0:
            raise ValueError("limit 必须为正整数")
        if not isinstance(query, str):
            raise ValueError("query 必须是字符串")

        q = query.strip()
        cur = self._conn.cursor()
        if not q:
            recent_items = self.list_recent(limit)
            return [
                {
                    "id": r.id,
                    "content": r.content,
                    "metadata": r.metadata,
                    "created_at": r.created_at,
                    "score": 0.0,
                }
                for r in recent_items
            ]

        select_sql = (
            "SELECT * FROM memories WHERE content LIKE ? "
            "ORDER BY created_at DESC, rowid DESC LIMIT ?"
        )
        cur.execute(
            select_sql,
            (f"%{q}%", max(limit * 5, limit)),
        )
        fetched_rows = cur.fetchall()
        ranked: List[Dict[str, Any]] = []
        for row in fetched_rows:
            content = str(row["content"])
            ranked.append(
                {
                    "id": str(row["id"]),
                    "content": content,
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "created_at": str(row["created_at"]),
                    "score": self._score(q, content),
                }
            )
        ranked.sort(
            key=lambda x: (x["score"], x["created_at"], x["id"]),
            reverse=True,
        )
        return ranked[:limit]
