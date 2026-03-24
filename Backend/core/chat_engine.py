import os
import random
import time

from groq import Groq

from config.settings import settings
from core.query_engine import search_atlas_direct


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY") or settings.groq_api_key
)


SYSTEM_PROMPT = """
You are LawGenie, a professional virtual legal assistant for India.

Rules:
1. Provide accurate legal guidance based on Indian law.
2. Do not claim to be a licensed lawyer.
3. If uncertain, clearly say so.
4. Include practical next steps.
5. Add references/sources at the end when possible.

Output format: Markdown.
"""


def _format_context_with_metadata(top_results, fallback_docs):
    if top_results:
        blocks = []
        for i, item in enumerate(top_results, start=1):
            text = (item.get("text") or "").strip()
            score = item.get("score", 0.0)
            metadata = item.get("metadata") or {}

            meta_lines = []
            for key in [
                "source",
                "source_name",
                "chunk_index",
                "pdf_name",
                "pdf_link",
                "category",
                "jurisdiction",
                "subcategory",
                "fingerprint",
            ]:
                value = metadata.get(key)
                if value not in [None, ""]:
                    meta_lines.append(f"- {key}: {value}")

            block = (
                f"[Chunk {i}]\n"
                f"Score: {score:.4f}\n"
                f"Metadata:\n{chr(10).join(meta_lines) if meta_lines else '- (none)'}\n"
                f"Text:\n{text}"
            )
            blocks.append(block)

        return "\n\n".join(blocks)

    return "\n\n".join(fallback_docs)


def _generate_with_retry_groq(messages, max_retries=4):
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=settings.groq_model,
                temperature=0.3,
                max_completion_tokens=settings.groq_max_completion_tokens,
                top_p=1,
                reasoning_effort=settings.groq_reasoning_effort,
                stream=False,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            err = str(e).lower()
            if "503" in err or "unavailable" in err or "overloaded" in err or "timeout" in err:
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
                continue
            raise e

    raise Exception("Groq API overloaded. Try again later.")


def legal_chat_light(query: str, history=None) -> dict:
    """
    Lightweight RAG-only chat flow.
    - Always performs direct Atlas retrieval.
    - No router/tool decision step.
    """
    history_text = ""
    if history:
        trimmed_history = history[-settings.chat_max_history_turns :]
        for turn in trimmed_history:
            role = turn.get("role", "").lower()
            message = turn.get("message", "")
            if role in ["user", "user query"]:
                history_text += f"User: {message}\n"
            elif role in ["assistant", "ai response"]:
                history_text += f"Assistant: {message}\n"

    retrieved_docs = search_atlas_direct(query=query, top_k=settings.chat_top_k, mode="auto")
    context_list = retrieved_docs.get("top_docs", [])
    top_results = retrieved_docs.get("top_results", [])
    scores = retrieved_docs.get("scores", [])
    top_score = max(scores) if scores else 0.0
    context_relevance = "high" if top_score >= 0.72 else "low"

    context_text = _format_context_with_metadata(top_results, context_list)

    user_prompt = f"""
Conversation History (for reference only):
{history_text}

Legal Reference Context:
{context_text}

User Question:
{query}

Context Relevance Signal:
- Relevance level: {context_relevance}

Instructions:
- Use the retrieved legal context as the primary source when relevant.
- If context is partially related, combine it with reliable Indian legal knowledge.
- If context is weak, clearly mention uncertainty.
- Provide practical next steps and relevant sections where possible.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response_text = _generate_with_retry_groq(messages)
    except Exception as e:
        return {
            "query": query,
            "answer": "The legal assistant is currently unavailable. Please try again later.",
            "error": str(e),
            "context_count": len(context_list),
            "retrieval_mode": retrieved_docs.get("mode", "auto"),
        }

    return {
        "query": query,
        "answer": response_text.strip(),
        "context_count": len(context_list),
        "retrieval_mode": retrieved_docs.get("mode", "auto"),
    }