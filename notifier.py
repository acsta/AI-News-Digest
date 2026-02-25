"""
notifier.py — 推送通知模块
支持三种渠道：Server酱（微信）、Telegram、邮件。
"""

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from config import (
    NOTIFY_VIA,
    SERVERCHAN_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    EMAIL_TO,
)

logger = logging.getLogger(__name__)


# ── 格式化 ───────────────────────────────────────────────

_SECTION_META = {
    "ai_dev":      ("🤖 AI 开发实用", 1),
    "x_timeline":  ("🐦 X/Twitter 动态", 2),
    "gamedev_ai":  ("🎮 游戏开发 AI", 3),
    "politics":    ("🏛️ 时事政治", 4),
    "finance":     ("💰 重要财经", 5),
}


def _group_by_section(digest: list[dict]) -> list[tuple[str, str, list[dict]]]:
    """按 section 分组并排序。"""
    groups: dict[str, list[dict]] = {}
    for item in digest:
        sec = item.get("section", "other")
        groups.setdefault(sec, []).append(item)
    result = []
    for sec_key in sorted(groups, key=lambda s: _SECTION_META.get(s, (s, 99))[1]):
        label, _ = _SECTION_META.get(sec_key, (f"📌 {sec_key}", 99))
        result.append((sec_key, label, groups[sec_key]))
    return result


def _format_markdown(digest: list[dict]) -> str:
    """将摘要格式化为 Markdown 文本，按板块分组。"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# 📰 AI News Digest — {today}\n"]

    for sec_key, label, items in _group_by_section(digest):
        lines.append(f"## {label}\n")
        for i, item in enumerate(items, 1):
            importance = item.get("importance", "?")
            title = item.get("title_cn", "无标题")
            summary = item.get("summary_cn", "")
            url = item.get("original_url", "")

            lines.append(f"### {i}. {title}")
            lines.append(f"⭐ {importance}/10\n")
            lines.append(f"{summary}\n")
            if url:
                lines.append(f"🔗 [阅读原文]({url})\n")
        lines.append("---\n")

    return "\n".join(lines)


def _format_html(digest: list[dict]) -> str:
    """将摘要格式化为 HTML（用于邮件），按板块分组。"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    parts = [
        "<html><body style='font-family:sans-serif;max-width:700px;margin:auto'>",
        f"<h1>📰 AI News Digest — {today}</h1>",
    ]

    for sec_key, label, items in _group_by_section(digest):
        parts.append(f"<h2>{label}</h2>")
        for i, item in enumerate(items, 1):
            importance = item.get("importance", "?")
            title = item.get("title_cn", "无标题")
            summary = item.get("summary_cn", "")
            url = item.get("original_url", "")

            parts.append(f"<h3>{i}. {title}</h3>")
            parts.append(f"<p><strong>⭐ {importance}/10</strong></p>")
            parts.append(f"<p>{summary}</p>")
            if url:
                parts.append(f'<p>🔗 <a href="{url}">阅读原文</a></p>')
        parts.append("<hr/>")

    parts.append("</body></html>")
    return "\n".join(parts)


# ── Server酱 (微信推送) ──────────────────────────────────

async def _send_wechat(digest: list[dict]) -> bool:
    """通过 Server酱 推送到微信。"""
    if not SERVERCHAN_KEY:
        logger.error("微信推送: 未配置 SERVERCHAN_KEY")
        return False

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = f"📰 AI News Digest — {today}"
    content = _format_markdown(digest)

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(
                url,
                data={"title": title, "desp": content},
            )
            result = resp.json()
            if result.get("code") == 0:
                logger.info("微信推送: 成功")
                return True
            else:
                logger.error("微信推送失败: %s", result)
                return False
        except Exception as exc:
            logger.error("微信推送异常: %s", exc)
            return False


# ── Telegram ─────────────────────────────────────────────

async def _send_telegram(digest: list[dict]) -> bool:
    """通过 Telegram Bot 推送。"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram 推送: 未配置 BOT_TOKEN 或 CHAT_ID")
        return False

    content = _format_markdown(digest)

    # Telegram 消息限制 4096 字符，超出时截断
    if len(content) > 4000:
        content = content[:3997] + "..."

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.post(
                url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": content,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
            )
            result = resp.json()
            if result.get("ok"):
                logger.info("Telegram 推送: 成功")
                return True
            else:
                logger.error("Telegram 推送失败: %s", result)
                return False
        except Exception as exc:
            logger.error("Telegram 推送异常: %s", exc)
            return False


# ── 邮件 ─────────────────────────────────────────────────

async def _send_email(digest: list[dict]) -> bool:
    """通过 SMTP 发送邮件。"""
    if not SMTP_USER or not SMTP_PASSWORD or not EMAIL_TO:
        logger.error("邮件推送: 未配置 SMTP 信息")
        return False

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"📰 AI News Digest — {today}"
    html = _format_html(digest)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
        logger.info("邮件推送: 成功 -> %s", EMAIL_TO)
        return True
    except Exception as exc:
        logger.error("邮件推送异常: %s", exc)
        return False


# ── 统一入口 ─────────────────────────────────────────────

_CHANNELS = {
    "wechat": _send_wechat,
    "telegram": _send_telegram,
    "email": _send_email,
}


async def send(
    digest: list[dict],
    channels: list[str] | str | None = None,
) -> bool:
    """
    通过一个或多个渠道推送新闻摘要。

    Args:
        digest: AI 处理后的摘要列表。
        channels: 推送渠道列表或逗号分隔字符串，默认读 config.NOTIFY_VIA。

    Returns:
        所有渠道是否都推送成功。
    """
    if not digest:
        logger.info("推送: 无内容需要推送")
        return True

    # 解析渠道列表
    if channels is None:
        channel_list = NOTIFY_VIA  # 已经是 list[str]
    elif isinstance(channels, str):
        channel_list = [ch.strip().lower() for ch in channels.split(",") if ch.strip()]
    else:
        channel_list = channels

    if not channel_list:
        logger.error("推送: 未指定任何渠道")
        return False

    logger.info("推送: 使用 %s 渠道发送 %d 条新闻", channel_list, len(digest))

    # 并发推送到所有渠道
    import asyncio

    async def _push_one(ch: str) -> tuple[str, bool]:
        fn = _CHANNELS.get(ch)
        if fn is None:
            logger.error("推送: 不支持的渠道 '%s'，可选: %s", ch, list(_CHANNELS))
            return ch, False
        return ch, await fn(digest)

    results = await asyncio.gather(*[_push_one(ch) for ch in channel_list])

    all_ok = True
    for ch, ok in results:
        if not ok:
            logger.error("推送: 渠道 '%s' 失败", ch)
            all_ok = False

    return all_ok

