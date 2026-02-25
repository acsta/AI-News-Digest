"""
sources.py — RSS 新闻源定义
每个源包含名称、RSS URL 和类别。
分为四大板块：AI 开发实用、游戏开发 AI (Unity)、时事政治、财经新闻。
"""

from dataclasses import dataclass, field
from datetime import datetime


# ── 数据结构 ──────────────────────────────────────────────

@dataclass
class RSSSource:
    """RSS 源定义"""
    name: str
    url: str
    category: str  # "ai_dev" | "gamedev_ai" | "politics" | "finance"


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
# 新模型发布、开源项目、AI 工具、开发者教程

AI_DEV_SOURCES: list[RSSSource] = [
    # --- 综合 AI 新闻 ---
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
    # --- 模型 & 研究 ---
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
    # --- 开源 & 工具 ---
    RSSSource(
        name="GitHub Trending (AI)",
        url="https://rsshub.app/github/trending/daily/python?since=daily",
        category="ai_dev",
    ),
    RSSSource(
        name="Papers With Code",
        url="https://rsshub.app/paperswithcode/latest",
        category="ai_dev",
    ),
    RSSSource(
        name="Towards Data Science",
        url="https://rsshub.app/medium/feed/towards-data-science",
        category="ai_dev",
    ),
]

# ── X/Twitter 动态 (通过 RSSHub 转 RSS，无需 API Key) ────

X_SOURCES: list[RSSSource] = [
    RSSSource(name="X/@karpathy", url="https://rsshub.app/twitter/user/karpathy", category="x_timeline"),
    RSSSource(name="X/@_akhaliq", url="https://rsshub.app/twitter/user/_akhaliq", category="x_timeline"),
    RSSSource(name="X/@huggingface", url="https://rsshub.app/twitter/user/huggingface", category="x_timeline"),
    RSSSource(name="X/@LangChainAI", url="https://rsshub.app/twitter/user/LangChainAI", category="x_timeline"),
    RSSSource(name="X/@claudeai", url="https://rsshub.app/twitter/user/claudeai", category="x_timeline"),
    RSSSource(name="X/@GoogleAI", url="https://rsshub.app/twitter/user/GoogleAI", category="x_timeline"),
    RSSSource(name="X/@OpenAI", url="https://rsshub.app/twitter/user/OpenAI", category="x_timeline"),
    RSSSource(name="X/@cursor_ai", url="https://rsshub.app/twitter/user/cursor_ai", category="x_timeline"),
    RSSSource(name="X/@unity", url="https://rsshub.app/twitter/user/unity", category="x_timeline"),
    RSSSource(name="X/@sama", url="https://rsshub.app/twitter/user/sama", category="x_timeline"),
    RSSSource(name="X/@AndrewYNg", url="https://rsshub.app/twitter/user/AndrewYNg", category="x_timeline"),
    RSSSource(name="X/@OfficialLoganK", url="https://rsshub.app/twitter/user/OfficialLoganK", category="x_timeline"),
    RSSSource(name="X/@lxfater", url="https://rsshub.app/twitter/user/lxfater", category="x_timeline"),
    RSSSource(name="X/@yangyi", url="https://rsshub.app/twitter/user/yangyi", category="x_timeline"),
    RSSSource(name="X/@xiaohu", url="https://rsshub.app/twitter/user/xiaohu", category="x_timeline"),
    RSSSource(name="X/@vista8", url="https://rsshub.app/twitter/user/vista8", category="x_timeline"),
    RSSSource(name="X/@op7418", url="https://rsshub.app/twitter/user/op7418", category="x_timeline"),
    RSSSource(name="X/@dotey", url="https://rsshub.app/twitter/user/dotey", category="x_timeline"),
]

# ── 游戏开发 AI (Unity) ─────────────────────────────────

GAMEDEV_AI_SOURCES: list[RSSSource] = [
    RSSSource(
        name="Unity Blog",
        url="https://blog.unity.com/feed",
        category="gamedev_ai",
    ),
    RSSSource(
        name="Unity AI/ML",
        url="https://rsshub.app/unity/blog/ai",
        category="gamedev_ai",
    ),
    RSSSource(
        name="Gamasutra (Game Developer)",
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
        name="AP News",
        url="https://rsshub.app/apnews/topics/apf-topnews",
        category="politics",
    ),
    RSSSource(
        name="South China Morning Post",
        url="https://www.scmp.com/rss/91/feed",
        category="politics",
    ),
    RSSSource(
        name="FT World",
        url="https://rsshub.app/ft/news/world",
        category="politics",
    ),
]

# ── 财经新闻 ─────────────────────────────────────────────

FINANCE_SOURCES: list[RSSSource] = [
    RSSSource(
        name="Bloomberg Markets",
        url="https://rsshub.app/bloomberg/markets",
        category="finance",
    ),
    RSSSource(
        name="Wall Street Journal",
        url="https://rsshub.app/wsj/en-us",
        category="finance",
    ),
    RSSSource(
        name="CNBC Business",
        url="https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147",
        category="finance",
    ),
    RSSSource(
        name="36氪",
        url="https://rsshub.app/36kr/newsflashes",
        category="finance",
    ),
    RSSSource(
        name="华尔街见闻",
        url="https://rsshub.app/wallstreetcn/news/global",
        category="finance",
    ),
]

# ── 全部源 ────────────────────────────────────────────────

ALL_SOURCES: list[RSSSource] = (
    AI_DEV_SOURCES + X_SOURCES + GAMEDEV_AI_SOURCES + POLITICS_SOURCES + FINANCE_SOURCES
)
