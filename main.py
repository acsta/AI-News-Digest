"""
main.py — AI News Digest 主入口
串联采集 → 去重 → AI 摘要 → 推送 全流程。
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime, timezone

from scraper import fetch_all_rss
from dedup import is_seen, mark_seen, cleanup, filter_new
from ai_processor import summarize
from notifier import send, _format_markdown

# ── 日志配置 ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI News Digest — 每日新闻聚合推送")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只采集和去重，不调用 AI API 和推送",
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "openai", "deepseek"],
        default=None,
        help="覆盖 AI Provider（默认读取 .env 中的 AI_PROVIDER）",
    )
    parser.add_argument(
        "--notify",
        choices=["wechat", "telegram", "email"],
        default=None,
        help="覆盖推送渠道（默认读取 .env 中的 NOTIFY_VIA）",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    start = datetime.now(timezone.utc)
    logger.info("=" * 60)
    logger.info("AI News Digest 开始运行")
    logger.info("=" * 60)

    # ── 1. 采集 (RSS + X/Twitter via Nitter, 全部走 RSS 管道) ──
    logger.info("▶ 第 1 步: 采集新闻源 (RSS + X/Nitter)...")

    all_articles = await fetch_all_rss()

    logger.info("采集完成: 共 %d 篇", len(all_articles))

    if not all_articles:
        logger.warning("未采集到任何文章，流程结束")
        return

    # ── 2. 去重 ──────────────────────────────────────────
    logger.info("▶ 第 2 步: URL 去重...")
    cleanup()  # 清理过期记录

    new_urls = filter_new([a.url for a in all_articles])
    new_articles = [a for a in all_articles if a.url in set(new_urls)]

    logger.info(
        "去重结果: %d / %d 为新文章",
        len(new_articles),
        len(all_articles),
    )

    if not new_articles:
        logger.info("所有文章均已处理过，无需继续")
        return

    # ── Dry-run 模式 ─────────────────────────────────────
    if args.dry_run:
        logger.info("=" * 60)
        logger.info("[DRY-RUN] 采集到的新文章 (%d 篇):", len(new_articles))
        logger.info("=" * 60)
        for i, a in enumerate(new_articles, 1):
            logger.info(
                "  [%d] [%s] %s\n       %s\n       %s",
                i,
                a.category.upper(),
                a.title,
                a.source,
                a.url,
            )
        logger.info("=" * 60)
        logger.info("[DRY-RUN] 流程结束（未调用 AI 和推送）")
        # 在 dry-run 模式下也标记已处理，避免重复
        mark_seen([a.url for a in new_articles])
        return

    # ── 3. AI 筛选摘要 ──────────────────────────────────
    logger.info("▶ 第 3 步: AI 筛选 + 摘要生成...")
    digest = await summarize(new_articles, provider=args.provider)

    if not digest:
        logger.warning("AI 未返回任何摘要结果")
        return

    logger.info("AI 摘要: 共 %d 条重要新闻", len(digest))

    # ── 4. 推送 ──────────────────────────────────────────
    logger.info("▶ 第 4 步: 推送新闻摘要...")
    success = await send(digest, channels=args.notify)

    if success:
        # 推送成功后标记已处理
        mark_seen([a.url for a in new_articles])
        logger.info("推送成功，已标记 %d 篇文章为已处理", len(new_articles))
    else:
        logger.error("推送失败！文章未标记，下次运行将重试")

    # ── 完成 ─────────────────────────────────────────────
    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    logger.info("=" * 60)
    logger.info("AI News Digest 运行完毕 (耗时 %.1f 秒)", elapsed)
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
