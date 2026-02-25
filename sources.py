"""
sources.py — RSS 新闻源定义
每个源包含名称、RSS URL 和类别。
分为五大板块：AI 开发实用、X/Twitter 动态、游戏开发 AI (Unity)、时事政治、财经新闻。

X/Twitter 动态板块当前为空 —— Twitter/X 已封锁所有免费读取路径
（API 免费层不支持读推文、RSSHub/Nitter 公共实例全部失效）。
如果未来有可用方案，取消注释 X_SOURCES 并填入实例地址即可。
"""

from dataclasses import dataclass, field
from datetime import datetime


# ── 数据结构 ──────────────────────────────────────────────

@dataclass
class RSSSource:
    """RSS 源定义"""
    name: str
    url: str
    category: str  # "ai_dev" | "x_timeline" | "gamedev_ai" | "politics" | "finance"


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


# ── AI 开发实用 ──────────────────────────────────────────

AI_DEV_SOURCES: list[RSSSource] = [
    RSSSource(
        name="Hacker News AI",
        url="https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT+OR+Claude+OR+Gemini",
        category="ai_dev",
    ),
    RSSSource(
        name="TechCrunch AI",
        url="https://techcrunch.com/category/artificial-intelligence/feed/",
        category="ai_dev",
    ),
    RSSSource(
        name="The Verge AI",
        url="https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        category="ai_dev",
    ),
    RSSSource(
        name="Ars Technica AI",
        url="https://feeds.arstechnica.com/arstechnica/technology-lab",
        category="ai_dev",
    ),
    RSSSource(
        name="MIT Technology Review",
        url="https://www.technologyreview.com/feed/",
        category="ai_dev",
    ),
    RSSSource(
        name="Hugging Face Blog",
        url="https://huggingface.co/blog/feed.xml",
        category="ai_dev",
    ),
    RSSSource(
        name="OpenAI Blog",
        url="https://openai.com/blog/rss.xml",
        category="ai_dev",
    ),
    RSSSource(
        name="Google AI Blog",
        url="https://blog.google/technology/ai/rss/",
        category="ai_dev",
    ),
    RSSSource(
        name="Hacker News Show (AI/ML)",
        url="https://hnrss.org/show?q=AI+OR+machine+learning+OR+open+source",
        category="ai_dev",
    ),
]

# ── X/Twitter 动态 ───────────────────────────────────────
# ⚠️ 当前无可用免费方案。如果你有可用的 Nitter 实例或自建 RSSHub，
# 取消下面的注释并替换 NITTER_INSTANCE 地址即可。
#
# NITTER_INSTANCE = "https://your-nitter-instance.com"
# def _x(u): return RSSSource(f"X/@{u}", f"{NITTER_INSTANCE}/{u}/rss", "x_timeline")
# X_SOURCES = [_x("karpathy"), _x("_akhaliq"), _x("sama"), ...]

X_SOURCES: list[RSSSource] = []  # 暂时为空

# ── 游戏开发 AI (Unity) ─────────────────────────────────

GAMEDEV_AI_SOURCES: list[RSSSource] = [
    RSSSource(
        name="Unity Blog",
        url="https://blog.unity.com/feed",
        category="gamedev_ai",
    ),
    RSSSource(
        name="Game Developer (Gamasutra)",
        url="https://www.gamedeveloper.com/rss.xml",
        category="gamedev_ai",
    ),
    RSSSource(
        name="HN Game AI",
        url="https://hnrss.org/newest?q=game+AI+OR+unity+AI+OR+procedural+generation",
        category="gamedev_ai",
    ),
    RSSSource(
        name="80 Level",
        url="https://80.lv/feed/",
        category="gamedev_ai",
    ),
]

# ── 时事政治 ─────────────────────────────────────────────

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
        name="South China Morning Post",
        url="https://www.scmp.com/rss/91/feed",
        category="politics",
    ),
    RSSSource(
        name="Al Jazeera",
        url="https://www.aljazeera.com/xml/rss/all.xml",
        category="politics",
    ),
    RSSSource(
        name="The Guardian World",
        url="https://www.theguardian.com/world/rss",
        category="politics",
    ),
]

# ── 财经新闻 ─────────────────────────────────────────────

FINANCE_SOURCES: list[RSSSource] = [
    RSSSource(
        name="CNBC Business",
        url="https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147",
        category="finance",
    ),
    RSSSource(
        name="Yahoo Finance",
        url="https://finance.yahoo.com/news/rssindex",
        category="finance",
    ),
    RSSSource(
        name="MarketWatch",
        url="https://feeds.marketwatch.com/marketwatch/topstories/",
        category="finance",
    ),
    RSSSource(
        name="Investing.com",
        url="https://www.investing.com/rss/news.rss",
        category="finance",
    ),
]

# ── 全部源 ────────────────────────────────────────────────

ALL_SOURCES: list[RSSSource] = (
    AI_DEV_SOURCES + X_SOURCES + GAMEDEV_AI_SOURCES + POLITICS_SOURCES + FINANCE_SOURCES
)
