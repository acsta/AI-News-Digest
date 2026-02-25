"""
ai_processor.py — AI 筛选 + 摘要模块
支持 Gemini（默认）/ OpenAI / Deepseek 三种 Provider。
将采集到的文章发送给 LLM，返回中文摘要和重要性排序。
"""

import json
import logging

from sources import Article
from config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    DEEPSEEK_BASE_URL,
    MAX_NEWS_ITEMS,
)

logger = logging.getLogger(__name__)

# ── 系统提示词 ──────────────────────────────────────────────

SYSTEM_PROMPT = f"""你是一个面向**开发者**的专业新闻编辑。你的读者是一名 Unity 游戏开发者，同时关注 AI 工具链和国际时事。
请从输入文章中筛选最有价值的内容，生成中文摘要，并按以下四个板块分类输出。

## 版块定义

1. **ai_dev** — AI 开发实用
   - 最新发布的大模型（GPT、Claude、Gemini、Llama、开源模型等）
   - 新的 AI 开源项目和代码库
   - 开发者工具和 SDK 更新（LangChain、HuggingFace、vLLM 等）
   - AI 编程助手和 Agent 框架动态
   - 重要 AI 论文和基准测试结果
   - **不要选**：纯商业融资、CEO 八卦、泛泛的 AI 观点文

2. **gamedev_ai** — 游戏开发 AI（Unity 重点）
   - Unity 引擎更新和新功能
   - 游戏中的 AI 应用（NPC AI、程序化生成、AI 美术等）
   - Unity ML-Agents、Sentis 等工具
   - 游戏行业 AI 工具和工作流
   - Unreal 或通用游戏 AI 重大突破也可纳入

3. **politics** — 中外时事政治
   - 国际重大事件（战争、外交、选举、政策变化）
   - 中国相关重大国际新闻
   - AI 监管政策和法规
   - 地缘政治对科技行业的影响

4. **finance** — 重要财经
   - 全球市场重大波动
   - 科技公司财报和重大并购
   - 中美经贸动态
   - 加密货币和金融科技重大事件

## 输出要求

1. 总共选出最多 {MAX_NEWS_ITEMS} 条新闻，每个板块至少覆盖（若有内容）
2. 去除广告、软文、重复、低价值内容
3. 每条新闻输出以下字段：
   - `section`: 板块标识 (ai_dev / gamedev_ai / politics / finance)
   - `title_cn`: 中文标题（简洁有力）
   - `summary_cn`: 中文摘要（3~5 句话，突出对开发者有什么用或有什么影响）
   - `importance`: 重要程度 1~10
   - `original_url`: 原文链接
4. 先按 section 分组，每组内按 importance 降序排列
5. 严格输出 JSON 数组，不要包含任何其他文字

## 输出格式

```json
[
  {{
    "section": "ai_dev",
    "title_cn": "Meta 开源 Llama 4 Scout 模型",
    "summary_cn": "Meta 发布 Llama 4 Scout...",
    "importance": 9,
    "original_url": "https://..."
  }},
  {{
    "section": "gamedev_ai",
    "title_cn": "Unity 6.2 新增 AI Navigation 系统",
    "summary_cn": "Unity 最新版本...",
    "importance": 8,
    "original_url": "https://..."
  }}
]
```"""


def _build_user_prompt(articles: list[Article]) -> str:
    """将文章列表序列化为 LLM 可读的格式。"""
    items = []
    for i, a in enumerate(articles, 1):
        items.append(
            f"[{i}] 标题: {a.title}\n"
            f"    来源: {a.source} | 类别: {a.category}\n"
            f"    摘要: {a.summary[:300]}\n"
            f"    链接: {a.url}"
        )
    return (
        f"以下是今天采集到的 {len(articles)} 篇新闻文章，"
        f"请筛选最重要的（最多 {MAX_NEWS_ITEMS} 条）并生成中文摘要：\n\n"
        + "\n\n".join(items)
    )


def _parse_response(text: str) -> list[dict]:
    """从 LLM 响应中提取 JSON 数组。"""
    # 尝试找到 JSON 数组
    text = text.strip()

    # 移除可能的 markdown 代码块标记
    if text.startswith("```"):
        lines = text.split("\n")
        # 去掉首尾的 ``` 行
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    # 找到第一个 [ 和最后一个 ]
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.error("AI 响应中未找到 JSON 数组")
        return []

    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        logger.error("AI 响应 JSON 解析失败: %s", exc)
        return []


# ── Gemini Provider ──────────────────────────────────────

async def _summarize_gemini(articles: list[Article]) -> list[dict]:
    """使用 Google Gemini 生成摘要。"""
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)

    user_prompt = _build_user_prompt(articles)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + user_prompt}]}
        ],
    )

    return _parse_response(response.text)


# ── OpenAI Provider ──────────────────────────────────────

async def _summarize_openai(articles: list[Article]) -> list[dict]:
    """使用 OpenAI 生成摘要。"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    user_prompt = _build_user_prompt(articles)

    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return _parse_response(response.choices[0].message.content or "")


# ── Deepseek Provider ───────────────────────────────────

async def _summarize_deepseek(articles: list[Article]) -> list[dict]:
    """使用 Deepseek 生成摘要（兼容 OpenAI SDK）。"""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    user_prompt = _build_user_prompt(articles)

    response = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return _parse_response(response.choices[0].message.content or "")


# ── 统一入口 ─────────────────────────────────────────────

_PROVIDERS = {
    "gemini": _summarize_gemini,
    "openai": _summarize_openai,
    "deepseek": _summarize_deepseek,
}


async def summarize(
    articles: list[Article],
    provider: str | None = None,
) -> list[dict]:
    """
    使用指定的 AI Provider 筛选和摘要文章。

    Args:
        articles: 待处理的文章列表。
        provider: AI Provider 名称，默认读取 config.AI_PROVIDER。

    Returns:
        筛选后的摘要列表 (list of dict)。
    """
    if not articles:
        logger.info("AI: 无文章需要处理")
        return []

    provider = (provider or AI_PROVIDER).lower()
    fn = _PROVIDERS.get(provider)

    if fn is None:
        logger.error("AI: 不支持的 Provider '%s'，可选: %s", provider, list(_PROVIDERS))
        return []

    logger.info(
        "AI: 使用 %s 处理 %d 篇文章 (最多输出 %d 条)",
        provider,
        len(articles),
        MAX_NEWS_ITEMS,
    )

    try:
        digest = await fn(articles)
        logger.info("AI: 摘要生成完成，共 %d 条", len(digest))
        return digest
    except Exception as exc:
        logger.error("AI: 摘要生成失败 [%s]: %s", provider, exc, exc_info=True)
        return []
