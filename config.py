"""
config.py — 统一配置管理
从 .env 文件或系统环境变量加载所有配置。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env
load_dotenv(Path(__file__).parent / ".env")


def _get(key: str, default: str = "") -> str:
    val = os.getenv(key, "").strip()
    return val if val else default


# ── AI Provider ──────────────────────────────────────────
AI_PROVIDER: str = _get("AI_PROVIDER", "gemini")  # gemini | openai | deepseek

GEMINI_API_KEY: str = _get("GEMINI_API_KEY")
GEMINI_MODEL: str = _get("GEMINI_MODEL", "gemini-2.0-flash")

OPENAI_API_KEY: str = _get("OPENAI_API_KEY")
OPENAI_MODEL: str = _get("OPENAI_MODEL", "gpt-4o-mini")

DEEPSEEK_API_KEY: str = _get("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL: str = _get("DEEPSEEK_MODEL", "deepseek-reasoner")
DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

# ── X / Twitter ──────────────────────────────────────────
TWITTER_BEARER_TOKEN: str = _get("TWITTER_BEARER_TOKEN")
TWITTER_USERNAMES: list[str] = [
    u.strip() for u in _get("TWITTER_USERNAMES").split(",") if u.strip()
]

# ── 微信推送 (Server酱) ──────────────────────────────────
SERVERCHAN_KEY: str = _get("SERVERCHAN_KEY")

# ── Telegram ─────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str = _get("TELEGRAM_CHAT_ID")

# ── Email / SMTP ─────────────────────────────────────────
SMTP_HOST: str = _get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(_get("SMTP_PORT", "587"))
SMTP_USER: str = _get("SMTP_USER")
SMTP_PASSWORD: str = _get("SMTP_PASSWORD")
EMAIL_TO: str = _get("EMAIL_TO")

# ── 通知渠道（支持多渠道，逗号分隔） ───────────────────────
NOTIFY_VIA: list[str] = [
    ch.strip().lower()
    for ch in _get("NOTIFY_VIA", "wechat").split(",")
    if ch.strip()
]

# ── 通用参数 ─────────────────────────────────────────────
FETCH_HOURS: int = int(_get("FETCH_HOURS", "24"))
MAX_NEWS_ITEMS: int = int(_get("MAX_NEWS_ITEMS", "20"))

# ── 路径 ─────────────────────────────────────────────────
PROJECT_DIR: Path = Path(__file__).parent
DATA_DIR: Path = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH: Path = DATA_DIR / "history.db"
