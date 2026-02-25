"""
dedup.py — URL 去重模块
使用 SQLite 存储已处理 URL 的 SHA256 哈希，自动清理过期记录。
"""

import hashlib
import logging
import sqlite3
from datetime import datetime, timedelta, timezone

from config import DB_PATH

logger = logging.getLogger(__name__)


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_urls (
            url_hash TEXT PRIMARY KEY,
            first_seen TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def _hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def is_seen(url: str) -> bool:
    """检查 URL 是否已经处理过。"""
    conn = _get_conn()
    try:
        cursor = conn.execute(
            "SELECT 1 FROM seen_urls WHERE url_hash = ?", (_hash(url),)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


def mark_seen(urls: list[str]) -> None:
    """批量标记 URL 为已处理。"""
    if not urls:
        return
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO seen_urls (url_hash, first_seen) VALUES (?, ?)",
            [(_hash(u), now) for u in urls],
        )
        conn.commit()
        logger.info("去重: 标记 %d 个 URL", len(urls))
    finally:
        conn.close()


def cleanup(days: int = 30) -> int:
    """清理 N 天前的记录，返回删除数量。"""
    conn = _get_conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    try:
        cursor = conn.execute(
            "DELETE FROM seen_urls WHERE first_seen < ?", (cutoff,)
        )
        conn.commit()
        deleted = cursor.rowcount
        if deleted:
            logger.info("去重: 清理 %d 条过期记录 (> %d 天)", deleted, days)
        return deleted
    finally:
        conn.close()


def filter_new(urls: list[str]) -> list[str]:
    """过滤出未处理过的 URL 列表。"""
    conn = _get_conn()
    try:
        new_urls = []
        for url in urls:
            cursor = conn.execute(
                "SELECT 1 FROM seen_urls WHERE url_hash = ?", (_hash(url),)
            )
            if cursor.fetchone() is None:
                new_urls.append(url)
        return new_urls
    finally:
        conn.close()
