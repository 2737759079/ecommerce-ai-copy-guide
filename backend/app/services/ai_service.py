import json
import re
from typing import Optional
from openai import OpenAI
from app.config import get_settings

settings = get_settings()


def get_client() -> Optional[OpenAI]:
    if not settings.deepseek_api_key or settings.deepseek_api_key == "your_deepseek_api_key_here":
        return None
    return OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)


def _chat(messages: list, temperature: float = 0.7) -> str:
    client = get_client()
    if client is None:
        return "[未配置DeepSeek API Key，无法生成内容]"
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"[AI调用失败: {str(e)}]"


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            text = m.group(1)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        text = m.group(0)
    try:
        return json.loads(text)
    except Exception:
        return {}


def generate_product_copy(product: dict, style: str = "professional") -> dict:
    prompt = f"""你是一名资深电商文案策划。请根据以下商品信息，生成一套{style}风格的电商文案，并以JSON格式返回。
商品信息：
{json.dumps(product, ensure_ascii=False, indent=2)}

要求JSON字段：
- title: 商品标题（30字以内）
- selling_points: 核心卖点（数组，每项一句话）
- detail: 详情页文案（200字左右）
- slogan: 宣传广告语（20字以内）
仅返回JSON，不要其他说明。"""
    content = _chat([{"role": "user", "content": prompt}], temperature=0.8)
    if content.startswith("["):
        return {
            "title": "",
            "selling_points": content,
            "detail": "",
            "slogan": "",
        }
    data = _extract_json(content)
    selling_points = data.get("selling_points", [])
    if isinstance(selling_points, list):
        selling_points = "\n".join([f"• {s}" for s in selling_points])
    return {
        "title": data.get("title", ""),
        "selling_points": selling_points,
        "detail": data.get("detail", ""),
        "slogan": data.get("slogan", ""),
    }


def generate_live_script(product: dict, style: str = "professional", platform: str = "live") -> str:
    prompt = f"""你是一名电商直播/短视频策划。请根据以下商品信息，生成一份{style}风格的{"直播脚本" if platform == "live" else "短视频口播脚本"}，并使用 Markdown 格式输出。
商品信息：
{json.dumps(product, ensure_ascii=False, indent=2)}

要求包含：开场留人、痛点挖掘、产品讲解、互动问答、逼单话术{"、镜头切换建议" if platform != "live" else ""}。直接输出脚本内容，不要包含JSON格式。"""
    return _chat([{"role": "user", "content": prompt}], temperature=0.85)


def generate_review_summary(reviews: list) -> dict:
    if not reviews:
        return {
            "summary": "该商品暂无评论，无法生成总结。",
            "suggestions": [],
        }
    review_texts = "\n".join([
        f"- 评分：{r.get('rating', 5)}，情感：{r.get('sentiment', 'neutral')}，内容：{r.get('content', '')}"
        for r in reviews
    ])
    prompt = f"""你是一名电商运营专家。请根据以下商品评论，生成一份评论总结与商品改进建议，并以 JSON 格式返回。
评论列表：
{review_texts}

要求 JSON 字段：
- summary: 对评论整体情况的总结（200字以内）
- suggestions: 改进建议列表（数组，每条建议一句话）
仅返回 JSON，不要其他说明。"""
    content = _chat([{"role": "user", "content": prompt}], temperature=0.7)
    if content.startswith("["):
        return {
            "summary": content,
            "suggestions": [],
        }
    data = _extract_json(content)
    if not data:
        return {
            "summary": content or "总结生成失败，请重试。",
            "suggestions": [],
        }
    suggestions = data.get("suggestions", [])
    if isinstance(suggestions, str):
        suggestions = [suggestions]
    return {
        "summary": data.get("summary", ""),
        "suggestions": suggestions,
    }


def chat_with_context(messages: list, context: str = "") -> str:
    system = "你是一名专业电商导购助手，基于店铺商品知识库回答用户问题，简洁准确。"
    if context:
        system += f"\n\n参考信息：\n{context}"
    full_messages = [{"role": "system", "content": system}] + messages
    return _chat(full_messages, temperature=0.6)
