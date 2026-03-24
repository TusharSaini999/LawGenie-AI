import os
import time
import random
import json

from groq import Groq

from core.query_engine import search_atlas_direct
from config.settings import settings


# ================== GROQ CLIENT ==================

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY") or settings.groq_api_key
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
- Mention relevant laws/sections when applicable.
- Provide step-by-step guidance.
- Suggest practical next actions.
- ALWAYS include reliable references at the end:
  - Government websites (e.g., india.gov.in, legislative.gov.in)
  - Official PDFs (Bare Acts, court documents, etc.)
  - Trusted legal resources
- Clearly label sources under a section: **"References / Sources"**
- Provide clickable links when possible.

Tone:
- Helpful, calm, trustworthy, and supportive.

Output Format:
- Output should be in Markdown format.
- Use bullet points, numbered lists, and bold text for clarity.
"""


def generate_with_retry_groq(
    messages,
    model=None,
    use_browser_search=False,
    max_retries=5
):

    call_model = model or settings.groq_model
    _debug_log(
        "LLM_CALL_START",
        {
            "model": call_model,
            "use_browser_search": use_browser_search,
            "message_count": len(messages),
            "max_retries": max_retries,
        },
    )

    for attempt in range(max_retries):

        try:
            request_payload = {
                "messages": messages,
                "model": model or settings.groq_model,
                "temperature": 0.3,
                "max_completion_tokens": settings.groq_max_completion_tokens,
                "top_p": 1,
                "reasoning_effort": settings.groq_reasoning_effort,
                "stream": False,
            }

            if use_browser_search:
                request_payload["tools"] = [{"type": "browser_search"}]

            chat_completion = client.chat.completions.create(
                **request_payload
            )

            _debug_log(
                "LLM_CALL_SUCCESS",
                {
                    "model": call_model,
                    "attempt": attempt + 1,
                    "used_browser_search": use_browser_search,
                },
            )

            return chat_completion.choices[0].message.content

        except Exception as e:

            err = str(e).lower()

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


def _decide_retrieval_via_llm(query: str, history_text: str) -> dict:
    """Ask the model whether retrieval is needed before answering."""
    router_messages = [
        {
            "role": "system",
            "content": (
                "You are a retrieval router for Indian legal Q&A. "
                "Return ONLY valid JSON with keys: needs_retrieval (boolean), reason (string), query_for_search (string). "
                "Rules: If the query is legal (laws, sections, acts, FIR, bail, court, rights, legal notices, petitions), "
                "set needs_retrieval=true and reason='tool_call'. "
                "If it is greeting/chit-chat/general and can be answered directly, set needs_retrieval=false and reason='direct_answer'."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Conversation History:\n{history_text}\n\n"
                f"User Query:\n{query}\n\n"
                "Decide whether to call retrieval tool. "
                "For legal queries, output reason exactly as 'tool_call'. "
                "For direct answers, output reason exactly as 'direct_answer'."
            ),
        },
    ]

    raw = generate_with_retry_groq(
        router_messages,
        use_browser_search=False,
        max_retries=2,
    )

    _debug_log(
        "ROUTER_RAW_OUTPUT",
        {
            "query": query,
            "raw": raw,
        },
    )

    try:
        decision = json.loads((raw or "").strip())
    except Exception:
        decision = {}

    return {
        "needs_retrieval": bool(decision.get("needs_retrieval", True)),
        "reason": str(decision.get("reason", "")),
        "query_for_search": str(decision.get("query_for_search", query)).strip() or query,
    }


# ================== MAIN LEGAL CHAT ==================

def legal_chat(query: str, history=None) -> dict:

    context_list = []
    top_results = []
    scores = []
    context_relevance = "not_used"
    context_text = ""
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

    # ========== 3. Decide Tool Use (LLM Router) ==========
    try:
        decision = _decide_retrieval_via_llm(query, history_text)
    except Exception:
        decision = {
            "needs_retrieval": True,
            "reason": "router_failed_default_to_retrieval",
            "query_for_search": query,
        }

    retrieval_requested = bool(decision.get("needs_retrieval", True))
    retrieval_reason = decision.get("reason", "")
    retrieval_used = False

    _debug_log(
        "ROUTER_DECISION",
        {
            "retrieval_requested": retrieval_requested,
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

    # ========== 4. Build Prompt ==========
    user_prompt = f"""
Conversation History (for reference only):
{history_text}

Legal Reference Context:
{context_text}

User Question:
{query}

Context Relevance Signal:
- Relevance level: {context_relevance}
- Retrieval requested by router: {retrieval_requested}
- Retrieval used: {retrieval_used}
- Router reason: {retrieval_reason}

Instructions:
- First, check whether the provided context is relevant to the user’s question.
- If the context directly matches the query topic, use it as the main source.
- If the context is partially related, use it carefully and supplement with general Indian law knowledge.
- If the context is not related, switch to Inbuilt Search Fallback Mode:
    1) Ignore unrelated retrieved context.
    2) Use your built-in legal knowledge and reasoning about Indian law.
    3) Provide the best possible helpful answer.
    4) Clearly mark uncertain points and suggest verification from official sources.

- Use ONLY verified Indian law knowledge.
- Provide step-by-step guidance when applicable.
- Cite relevant Acts/Sections if available.
- If information is insufficient, say so honestly.

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

    # ========== 5. Generate Response ==========

    try:
        use_browser_search = settings.chat_enable_browser_search and (not retrieval_used)
        _debug_log(
            "FINAL_LLM_CALL",
            {
                "retrieval_used": retrieval_used,
                "context_count": len(context_list),
                "use_browser_search": use_browser_search,
            },
        )
        response_text = generate_with_retry_groq(
            messages,
            use_browser_search=use_browser_search,
        )

    except Exception as e:

        return {
            "query": query,
            "answer": "The legal assistant is currently unavailable. Please try again later.",
            "error": str(e),
            "context_count": len(context_list),
            "retrieval_requested": retrieval_requested,
            "retrieval_used": retrieval_used,
            "retrieval_error": retrieval_error,
        }

    # ========== 6. Return Clean Output ==========

    return {
        "query": query,
        "answer": response_text.strip(),
        "context_count": len(context_list),
        "retrieval_requested": retrieval_requested,
        "retrieval_used": retrieval_used,
        "retrieval_error": retrieval_error,
    }