"""
twitter_fetcher.py — X/Twitter 推文采集模块
使用 httpx 直接调用 X API v2 获取关注账号推文。
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx

from sources import Article
from config import TWITTER_BEARER_TOKEN, TWITTER_USERNAMES, FETCH_HOURS

logger = logging.getLogger(__name__)

_BASE = "https://api.twitter.com/2"
_TIMEOUT = httpx.Timeout(15.0, connect=10.0)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "User-Agent": "AI-News-Digest/1.0",
    }


async def _get_user_id(client: httpx.AsyncClient, username: str) -> str | None:
    """通过用户名查询 Twitter 用户 ID。"""
    try:
        resp = await client.get(
            f"{_BASE}/users/by/username/{username}",
            headers=_headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("id")
    except Exception as exc:
        logger.warning("Twitter 用户查询失败 [@%s]: %s", username, exc)
        return None


async def _get_user_tweets(
    client: httpx.AsyncClient,
    user_id: str,
    username: str,
    since: datetime,
) -> list[Article]:
    """获取用户最近的推文。"""
    params = {
        "max_results": 20,
        "start_time": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tweet.fields": "created_at,text,entities",
        "expansions": "author_id",
    }
    try:
        resp = await client.get(
            f"{_BASE}/users/{user_id}/tweets",
            headers=_headers(),
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Twitter 推文获取失败 [@%s]: %s", username, exc)
        return []

    tweets = data.get("data", [])
    articles: list[Article] = []

    for tweet in tweets:
        text = tweet.get("text", "").strip()
        tweet_id = tweet.get("id", "")
        created_at_str = tweet.get("created_at", "")

        published = None
        if created_at_str:
            try:
                published = datetime.fromisoformat(
                    created_at_str.replace("Z", "+00:00")
                )
            except Exception:
                pass

        # 提取推文中的 URL
        urls = []
        entities = tweet.get("entities", {})
        for url_obj in entities.get("urls", []):
            expanded = url_obj.get("expanded_url", "")
            if expanded and "twitter.com" not in expanded:
                urls.append(expanded)

        tweet_url = f"https://x.com/{username}/status/{tweet_id}"

        articles.append(
            Article(
                title=f"@{username}: {text[:100]}{'...' if len(text) > 100 else ''}",
                url=tweet_url,
                summary=text[:500],
                source=f"X/@{username}",
                category="ai",  # 由 AI 后续判定
                published=published,
                extra={"shared_urls": urls},
            )
        )

    logger.info("Twitter [@%s]: 获取 %d 条推文", username, len(articles))
    return articles


async def fetch_tweets() -> list[Article]:
    """
    获取所有配置的 Twitter 账号的最近推文。
    如果未配置 Bearer Token 则返回空列表。
    """
    if not TWITTER_BEARER_TOKEN:
        logger.info("Twitter: 未配置 Bearer Token，跳过 Twitter 采集")
        return []

    if not TWITTER_USERNAMES:
        logger.info("Twitter: 未配置用户名列表，跳过")
        return []

    since = datetime.now(timezone.utc) - timedelta(hours=FETCH_HOURS)

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        # 1. 查询所有用户 ID
        id_tasks = [_get_user_id(client, u) for u in TWITTER_USERNAMES]
        user_ids = await asyncio.gather(*id_tasks)

        # 2. 获取推文
        tweet_tasks = []
        for username, uid in zip(TWITTER_USERNAMES, user_ids):
            if uid:
                tweet_tasks.append(
                    _get_user_tweets(client, uid, username, since)
                )

        if not tweet_tasks:
            logger.warning("Twitter: 没有找到任何有效用户")
            return []

        results = await asyncio.gather(*tweet_tasks)

    all_tweets = [a for batch in results for a in batch]
    logger.info("Twitter 采集完成: 共 %d 条推文", len(all_tweets))
    return all_tweets
