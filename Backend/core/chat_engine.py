import time
import random
import json
import re

from groq import Groq

from core.query_engine import search_atlas_direct
from config.settings import settings


# ================== GROQ CLIENT ==================

client = Groq(
    api_key=settings.groq_api_key
)


def _debug_log(label: str, payload: dict) -> None:
    try:
        print(f"[DEBUG] {label}: {json.dumps(payload, ensure_ascii=True)}")
    except Exception:
        print(f"[DEBUG] {label}: {payload}")


# ================== SYSTEM PROMPT ==================

SYSTEM_PROMPT = """
You are LawGenie, a professional virtual legal assistant for India.

Your Identity:
- Your name is LawGenie.
- You are an AI-powered legal guidance assistant.

Your Responsibilities:
- Provide accurate legal information based on Indian laws.
- Cover IPC, CrPC, RTI, Consumer Law, Labor Law, Family Law, IT Act, etc.
- Explain legal concepts in simple and easy language.

Conversation Awareness:
- Always analyze previous conversation history.
- If the current query is related to earlier questions, connect it with past context.
- Maintain continuity in multi-turn conversations.
- Avoid repeating information unnecessarily.

Rules:
1. Never give false or misleading legal advice.
2. If unsure, clearly say you are not fully certain.
3. Do not pretend to be a licensed lawyer.
4. Never encourage illegal activity.
5. Ask follow-up questions if important details are missing.
6. Respect user privacy and confidentiality.

Response Guidelines:
- Give structured answers when possible.
- Keep answers precise and concise. Avoid unnecessary detail.
- Mention relevant laws/sections when applicable.
- Provide step-by-step guidance.
- Suggest practical next actions.
- ALWAYS include reliable references at the end:
  - Government websites (e.g., india.gov.in, legislative.gov.in)
  - Official PDFs (Bare Acts, court documents, etc.)
  - Trusted legal resources
- Clearly label sources under a section: **"References / Sources"**
- Provide clickable links when possible.

Browser Search and PDF Link Policy:
- If the answer needs external or latest information, use browser search to find sources.
- For PDF references, provide only real, direct PDF links that were actually used to prepare the answer.
- Include only links that are openable from the source results; do not invent, guess, or rewrite URLs.
- Prefer official government or court PDF links whenever available.
- If no verified openable PDF link is found, explicitly state: "No verified openable PDF link found."

Tone:
- Helpful, calm, trustworthy, and supportive.

Output Format:
- Output must be valid Markdown.
- Use bullet points, numbered lists, and **bold labels** for clarity.
- Keep paragraphs short (2-4 lines max).
- If information is uncertain, add a clear Markdown note: `> Note: This point should be verified from an official source.`
"""


def generate_with_retry_groq(
    messages,
    model=None,
    use_browser_search=False,
    max_retries=5
):

    call_model = model or settings.groq_model
    can_use_browser_search = (
        bool(use_browser_search)
        and str(call_model) == str(settings.groq_fallback_model)
    )
    if use_browser_search and not can_use_browser_search:
        _debug_log(
            "BROWSER_SEARCH_SKIPPED",
            {
                "model": call_model,
                "reason": "browser_search_allowed_only_on_fallback_model",
            },
        )

    _debug_log(
        "LLM_CALL_START",
        {
            "model": call_model,
            "use_browser_search": can_use_browser_search,
            "message_count": len(messages),
            "max_retries": max_retries,
        },
    )

    for attempt in range(max_retries):

        try:
            request_payload = {
                "messages": messages,
                "model": call_model,
                "temperature": 0.3,
                "top_p": 1,
                "stream": False,
                "max_completion_tokens": settings.groq_max_completion_tokens,
            }

            # Some Groq models reject reasoning_effort; only attach it to known compatible models.
            if "gpt-oss" in str(call_model):
                request_payload["reasoning_effort"] = settings.groq_reasoning_effort

            if can_use_browser_search:
                request_payload["tools"] = [{"type": "browser_search"}]

            chat_completion = client.chat.completions.create(
                **request_payload
            )

            _debug_log(
                "LLM_CALL_SUCCESS",
                {
                    "model": call_model,
                    "attempt": attempt + 1,
                    "used_browser_search": can_use_browser_search,
                },
            )

            return chat_completion.choices[0].message.content

        except Exception as e:

            err = str(e).lower()

            # If a model does not support reasoning_effort, retry once without it.
            if "reasoning_effort" in err and "not supported" in err:
                try:
                    retry_payload = {
                        "messages": messages,
                        "model": call_model,
                        "temperature": 0.3,
                        "top_p": 1,
                        "stream": False,
                        "max_completion_tokens": settings.groq_max_completion_tokens,
                    }
                    if can_use_browser_search:
                        retry_payload["tools"] = [{"type": "browser_search"}]

                    chat_completion = client.chat.completions.create(**retry_payload)

                    _debug_log(
                        "LLM_CALL_SUCCESS_NO_REASONING_EFFORT",
                        {
                            "model": call_model,
                            "attempt": attempt + 1,
                            "used_browser_search": can_use_browser_search,
                        },
                    )

                    return chat_completion.choices[0].message.content
                except Exception:
                    pass

            if (
                "503" in err
                or "unavailable" in err
                or "overloaded" in err
                or "timeout" in err
            ):

                _debug_log(
                    "LLM_CALL_RETRY",
                    {
                        "model": call_model,
                        "attempt": attempt + 1,
                        "error": str(e),
                    },
                )

                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
                continue

            raise e

    raise Exception("Groq API overloaded. Try again later.")


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


def _looks_like_small_talk(query: str) -> bool:
    cleaned = " ".join((query or "").strip().lower().split())
    if not cleaned:
        return True

    small_talk_words = {
        "hi",
        "hello",
        "hey",
        "thanks",
        "thank you",
        "ok",
        "okay",
        "bye",
        "good morning",
        "good evening",
        "who are you",
    }

    if cleaned in small_talk_words:
        return True

    if len(cleaned.split()) <= 3 and cleaned.rstrip("!?.") in small_talk_words:
        return True

    # If it has no legal intent markers, treat very short conversational input as chitchat.
    legal_markers = (
        "law",
        "legal",
        "ipc",
        "crpc",
        "section",
        "act",
        "court",
        "judge",
        "police",
        "fir",
        "bail",
        "contract",
        "rights",
        "notice",
        "case",
        "complaint",
        "divorce",
        "property",
        "consumer",
        "labour",
        "labor",
        "cyber",
        "it act",
        "rti",
    )
    if len(cleaned.split()) <= 5 and not any(marker in cleaned for marker in legal_markers):
        return True

    return False


def _needs_browser_search(query: str) -> bool:
    cleaned = " ".join((query or "").strip().lower().split())
    if not cleaned:
        return False

    # Browser search helps when user asks for latest updates / notifications / recent changes.
    recency_patterns = [
        r"\blatest\b",
        r"\brecent\b",
        r"\bcurrent\b",
        r"\btoday\b",
        r"\bupdated\b",
        r"\bnew\s+rule\b",
        r"\bnew\s+amendment\b",
        r"\bamendment\b",
        r"\bnotification\b",
        r"\bcircular\b",
        r"\bgazette\b",
        r"\b202[5-9]\b",
    ]
    return any(re.search(pattern, cleaned) for pattern in recency_patterns)


def _decide_flow(query: str, history_text: str) -> dict:
    del history_text  # Reserved for future heuristics.

    if _looks_like_small_talk(query):
        return {
            "needs_tool_call": False,
            "needs_browser_search": False,
            "reason": "direct_answer_small_talk",
            "query_for_search": query,
        }

    return {
        "needs_tool_call": True,
        "needs_browser_search": _needs_browser_search(query),
        "reason": "retrieval_by_default_for_legal_query",
        "query_for_search": query,
    }


# ================== MAIN LEGAL CHAT ==================

def legal_chat(query: str, history=None) -> dict:

    context_list = []
    top_results = []
    scores = []
    context_relevance = "not_used"
    context_text = ""
    browser_context_text = ""
    retrieval_error = ""

    # ========== 2. Format History ==========

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

    _debug_log(
        "CHAT_INPUT",
        {
            "query": query,
            "history_chars": len(history_text),
        },
    )

    # ========== 3. Decide Flow (Deterministic Router) ==========
    decision = _decide_flow(query, history_text)

    retrieval_requested = bool(decision.get("needs_tool_call", False))
    browser_search_requested = bool(decision.get("needs_browser_search", False))
    retrieval_reason = decision.get("reason", "")
    retrieval_used = False

    _debug_log(
        "FLOW_DECISION",
        {
            "retrieval_requested": retrieval_requested,
            "browser_search_requested": browser_search_requested,
            "reason": retrieval_reason,
            "query_for_search": decision.get("query_for_search", query),
        },
    )

    if retrieval_requested:
        try:
            tool_query = decision.get("query_for_search", query)
            _debug_log(
                "TOOL_CALL_START",
                {
                    "tool": "search_atlas_direct",
                    "query": tool_query,
                    "top_k": settings.chat_top_k,
                    "mode": "auto",
                },
            )

            retrieved_docs = search_atlas_direct(tool_query, top_k=settings.chat_top_k, mode="auto")
            context_list = retrieved_docs.get("top_docs", [])
            top_results = retrieved_docs.get("top_results", [])
            scores = retrieved_docs.get("scores", [])
            top_score = max(scores) if scores else 0.0
            context_relevance = "high" if top_score >= 0.72 else "low"
            retrieval_used = bool(context_list)
            context_text = _format_context_with_metadata(top_results, context_list)

            _debug_log(
                "TOOL_CALL_CONTEXT",
                {
                    "tool": "search_atlas_direct",
                    "selected_mode": retrieved_docs.get("mode", "auto"),
                    "context_count": len(context_list),
                    "top_score": top_score,
                    "context_relevance": context_relevance,
                },
            )
        except Exception as err:
            retrieval_error = str(err)
            _debug_log(
                "TOOL_CALL_ERROR",
                {
                    "tool": "search_atlas_direct",
                    "error": retrieval_error,
                },
            )

    # ========== 4. Optional Browser Search via Fallback Model ==========
    try:
        need_browser_context = (
            settings.chat_enable_browser_search
            and retrieval_requested
            and browser_search_requested
            and ((not retrieval_used) or context_relevance == "low")
        )

        if need_browser_context:
            browser_context_prompt = f"""
You are a legal web researcher for India.
Use browser search and return concise factual context only.
Do not provide final legal advice.

User Question:
{query}

Conversation History:
{history_text}

Retrieved Legal Context:
{context_text}

Output format:
- Key facts (bullet points)
- Relevant Acts/Sections (if found)
- Verified sources with direct links
"""

            browser_messages = [
                {
                    "role": "system",
                    "content": "You collect verified legal web context and sources for India.",
                },
                {
                    "role": "user",
                    "content": browser_context_prompt,
                },
            ]

            _debug_log(
                "BROWSER_CONTEXT_CALL",
                {
                    "model": settings.groq_fallback_model,
                    "retrieval_used": retrieval_used,
                    "context_relevance": context_relevance,
                },
            )

            browser_context_text = generate_with_retry_groq(
                browser_messages,
                model=settings.groq_fallback_model,
                use_browser_search=True,
                max_retries=3,
            ) or ""
    except Exception as browser_err:
        _debug_log(
            "BROWSER_CONTEXT_ERROR",
            {
                "error": str(browser_err),
            },
        )

    # ========== 5. Build Prompt for Main Model ==========
    user_prompt = f"""
Conversation History (for reference only):
{history_text}

Legal Reference Context:
{context_text}

Browser Search Context:
{browser_context_text}

User Question:
{query}

Context Relevance Signal:
- Relevance level: {context_relevance}
- Retrieval requested by router: {retrieval_requested}
- Browser search requested by router: {browser_search_requested}
- Retrieval used: {retrieval_used}
- Router reason: {retrieval_reason}

Instructions:
- First, check whether the provided context is relevant to the user’s question.
- If the context directly matches the query topic, use it as the main source.
- If the context is partially related, use it carefully and supplement with general Indian law knowledge.
- If retrieved context is weak but Browser Search Context is useful, use Browser Search Context and cite those sources.
- If both contexts are weak, use your built-in legal knowledge carefully and clearly mark uncertainty.

- Use ONLY verified Indian law knowledge.
- Provide step-by-step guidance when applicable.
- Cite relevant Acts/Sections if available.
- If information is insufficient, say so honestly.
- Keep the final answer precise, direct, and focused on the user question.

"""

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "user",
            "content": user_prompt
        }

    ]

    # ========== 6. Generate Final Response from Main Model ==========

    try:
        _debug_log(
            "FINAL_LLM_CALL",
            {
                "selected_model": settings.groq_model,
                "retrieval_used": retrieval_used,
                "context_count": len(context_list),
                "browser_context_used": bool(browser_context_text.strip()),
            },
        )
        response_text = generate_with_retry_groq(
            messages,
            model=settings.groq_model,
            use_browser_search=False,
        )

    except Exception as e:

        return {
            "query": query,
            "answer": "The legal assistant is currently unavailable. Please try again later.",
            "error": str(e),
            "context_count": len(context_list),
            "retrieval_requested": retrieval_requested,
            "browser_search_requested": browser_search_requested,
            "retrieval_used": retrieval_used,
            "retrieval_error": retrieval_error,
        }

    # ========== 6. Return Clean Output ==========

    return {
        "query": query,
        "answer": response_text.strip(),
        "context_count": len(context_list),
        "retrieval_requested": retrieval_requested,
        "browser_search_requested": browser_search_requested,
        "retrieval_used": retrieval_used,
        "retrieval_error": retrieval_error,
    }