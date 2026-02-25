"""
scraper.py — RSS 新闻采集模块
使用 feedparser + httpx 并发采集所有 RSS 源。
"""

import asyncio
import logging
from datetime import datetime, timezone

import feedparser
import httpx

from sources import ALL_SOURCES, Article, RSSSource
from config import FETCH_HOURS

logger = logging.getLogger(__name__)

# httpx 并发限制，避免被限流
_SEMAPHORE = asyncio.Semaphore(5)
_TIMEOUT = httpx.Timeout(20.0, connect=10.0)


async def _fetch_one(
    client: httpx.AsyncClient,
    source: RSSSource,
) -> list[Article]:
    """采集单个 RSS 源，返回 Article 列表。"""
    async with _SEMAPHORE:
        try:
            resp = await client.get(source.url)
            resp.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            logger.warning("RSS 采集失败 [%s]: %s", source.name, exc)
            return []

    feed = feedparser.parse(resp.text)
    if feed.bozo and not feed.entries:
        logger.warning("RSS 解析异常 [%s]: %s", source.name, feed.bozo_exception)
        return []

    articles: list[Article] = []
    now = datetime.now(timezone.utc)

    for entry in feed.entries:
        # 解析发布时间
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass

        # 过滤时间窗口
        if published and (now - published).total_seconds() > FETCH_HOURS * 3600:
            continue

        title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()
        summary = getattr(entry, "summary", "").strip()

        if not title or not link:
            continue

        # 截断过长摘要
        if len(summary) > 500:
            summary = summary[:497] + "..."

        articles.append(
            Article(
                title=title,
                url=link,
                summary=summary,
                source=source.name,
                category=source.category,
                published=published,
            )
        )

    logger.info("RSS [%s]: 获取 %d 篇文章", source.name, len(articles))
    return articles


async def fetch_all_rss(sources: list[RSSSource] | None = None) -> list[Article]:
    """
    并发采集所有 RSS 源。

    Args:
        sources: 可选源列表，默认 ALL_SOURCES。

    Returns:
        所有采集到的 Article 列表。
    """
    if sources is None:
        sources = ALL_SOURCES

    async with httpx.AsyncClient(
        timeout=_TIMEOUT,
        headers={"User-Agent": "AI-News-Digest/1.0"},
        follow_redirects=True,
    ) as client:
        tasks = [_fetch_one(client, src) for src in sources]
        results = await asyncio.gather(*tasks)

    all_articles = [a for batch in results for a in batch]
    logger.info("RSS 采集完成: 共 %d 篇文章 (来自 %d 个源)", len(all_articles), len(sources))
    return all_articles
