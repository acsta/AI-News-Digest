"""
sources.py — RSS 新闻源定义
每个源包含名称、RSS URL 和类别。
"""

from dataclasses import dataclass, field
from datetime import datetime


# ── 数据结构 ──────────────────────────────────────────────

@dataclass
class RSSSource:
    """RSS 源定义"""
    name: str
    url: str
    category: str  # "ai" | "politics"


@dataclass
class Article:
    """统一的文章数据结构，供所有采集模块输出"""
    title: str
    url: str
    summary: str
    source: str
    category: str
    published: datetime | None = None
    extra: dict = field(default_factory=dict)


# ── AI 类 RSS 源 ─────────────────────────────────────────

AI_SOURCES: list[RSSSource] = [
    RSSSource(
        name="TechCrunch AI",
        url="https://techcrunch.com/category/artificial-intelligence/feed/",
        category="ai",
    ),
    RSSSource(
        name="The Verge AI",
        url="https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        category="ai",
    ),
    RSSSource(
        name="MIT Technology Review",
        url="https://www.technologyreview.com/feed/",
        category="ai",
    ),
    RSSSource(
        name="Ars Technica AI",
        url="https://feeds.arstechnica.com/arstechnica/technology-lab",
        category="ai",
    ),
    RSSSource(
        name="Hacker News AI",
        url="https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT",
        category="ai",
    ),
    RSSSource(
        name="OpenAI Blog",
        url="https://openai.com/blog/rss.xml",
        category="ai",
    ),
]

# ── 政治类 RSS 源 ────────────────────────────────────────

POLITICS_SOURCES: list[RSSSource] = [
    RSSSource(
        name="BBC World News",
        url="http://feeds.bbci.co.uk/news/world/rss.xml",
        category="politics",
    ),
    RSSSource(
        name="NPR Politics",
        url="https://feeds.npr.org/1014/rss.xml",
        category="politics",
    ),
    RSSSource(
        name="Reuters World",
        url="https://www.rss.reuters.com/news/worldNews",
        category="politics",
    ),
    RSSSource(
        name="AP News",
        url="https://rsshub.app/apnews/topics/apf-topnews",
        category="politics",
    ),
]

# ── 全部源 ────────────────────────────────────────────────

ALL_SOURCES: list[RSSSource] = AI_SOURCES + POLITICS_SOURCES
