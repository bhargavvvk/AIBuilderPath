from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from pathlib import Path
import re

from rag_tool import search_hr_policy
from web_tool import web_search
from google_docs_tool import search_insurance_docs

load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)


# Initialize the LLM
llm = ChatOllama(
    model="mistral",
    temperature=0,
)

def _should_use_web_search(query: str) -> bool:
    keywords = (
        "current",
        "latest",
        "today",
        "news",
        "web",
        "internet",
        "regulation",
        "regulations",
        "law",
        "laws",
        "legal",
        "government",
        "federal",
        "state",
    )
    return _contains_any_keyword(query, keywords)


def _should_use_insurance_docs(query: str) -> bool:
    keywords = ("insurance", "benefit", "benefits", "coverage", "claim")
    return _contains_any_keyword(query, keywords)


def _contains_any_keyword(query: str, keywords: tuple[str, ...]) -> bool:
    query_lower = query.lower()

    for keyword in keywords:
        if " " in keyword:
            if keyword in query_lower:
                return True
            continue

        if re.search(rf"\b{re.escape(keyword)}\b", query_lower):
            return True

    return False


def _is_internal_hr_query(query: str) -> bool:
    keywords = (
        "leave",
        "vacation",
        "pto",
        "attendance",
        "payroll",
        "salary",
        "holiday",
        "hr",
        "policy",
        "maternity",
        "termination",
        "separation",
    )
    return _contains_any_keyword(query, keywords)


def _is_external_public_query(query: str) -> bool:
    keywords = (
        "ai",
        "artificial intelligence",
        "us",
        "united states",
        "regulation",
        "regulations",
        "law",
        "laws",
        "legal",
    )
    return _contains_any_keyword(query, keywords)


def gather_context(query: str) -> str:
    context_parts = []
    query_lower = query.lower()

    use_web = _should_use_web_search(query)
    use_hr = _is_internal_hr_query(query)
    use_insurance = _should_use_insurance_docs(query)

    # Public legal/regulation queries should prioritize web context.
    if _is_external_public_query(query):
        use_web = True
        use_hr = False
        use_insurance = False

    if use_hr:
        try:
            hr_context = search_hr_policy.invoke({"query": query})
            if hr_context.strip():
                context_parts.append(f"HR policy context:\n{hr_context}")
        except Exception as exc:
            context_parts.append(f"HR policy lookup failed: {exc}")

    if use_insurance:
        try:
            insurance_context = search_insurance_docs.invoke({"query": query})
            if insurance_context.strip():
                context_parts.append(f"Insurance context:\n{insurance_context}")
        except Exception as exc:
            context_parts.append(f"Insurance lookup failed: {exc}")

    if use_web:
        try:
            web_context = web_search.invoke({"query": query})
            if web_context:
                context_parts.append(f"Web context:\n{web_context}")
        except Exception as exc:
            context_parts.append(f"Web lookup failed: {exc}")

    return "\n\n".join(context_parts)


def answer_query(query: str) -> str:
    context = gather_context(query)
    context_lower = context.lower()

    if not context:
        return (
            "I couldn't find relevant context for this question. "
            "If this is an internal policy question, please check the HR handbook; "
            "if it is an external regulations question, ensure web search is configured."
        )

    if "tavily_api_key" in context_lower:
        return (
            "Web search is not configured: set the TAVILY_API_KEY environment variable "
            "to answer external questions like US AI regulations."
        )

    if "lookup failed" in context and "context:" not in context.lower():
        return (
            "I could not retrieve usable sources for this question. "
            "Please verify data sources and API keys, then try again."
        )

    messages = [
        SystemMessage(
            content=(
                "You are an internal research assistant. Answer using only the provided context. "
                "If the context is insufficient, say what is missing and do not invent facts."
            )
        ),
        HumanMessage(
            content=(
                f"Question: {query}\n\n"
                f"Context:\n{context if context else 'No relevant context was found.'}"
            )
        ),
    ]

    response = llm.invoke(messages)
    return response.content


def chat():
    print("=" * 60)
    print("🏢 Internal Research Agent")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:
        query = input("\nYou: ")

        if query.lower() == "exit":
            break

        print("\nAssistant:\n")
        print(answer_query(query))


if __name__ == "__main__":
    chat()