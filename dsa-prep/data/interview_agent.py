from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import requests

from data.questions import get_topics


SYSTEM_PROMPT = """You are a senior technical interviewer for DSA live coding rounds.

Behave like a capable conversational LLM in a Claude-style chat UI, but stay in the interviewer role.
You are not a static answer key. Respond directly to the candidate's latest message, using the
conversation history, selected problem resource, and available problem-bank tools.

Interview behavior:
- If the candidate asks you to restate, explain, clarify, or summarize the problem, do that directly.
- If the candidate gives an approach, evaluate it, ask one focused follow-up, and avoid dumping the full solution.
- If the candidate asks for a hint, give a graduated hint, not the complete answer.
- If the candidate asks for the solution, ask whether they want a guided reveal; if they insist, give a clear solution.
- If the candidate provides code, review correctness, complexity, edge cases, and implementation risk.
- Keep responses concise, natural, and specific to the selected problem.
- Do not pretend to use tools you do not have. Use only the provided tool results and context.
"""


@dataclass
class LLMConfig:
    provider: str
    model: str
    base_url: str
    api_key: str | None
    timeout: int = 45

    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = os.environ.get("LLM_PROVIDER", "openai").strip().lower()
        default_model = "command-a-03-2025" if provider == "cohere" else "gpt-4o-mini"
        default_base_url = "https://api.cohere.com/v2" if provider == "cohere" else "https://api.openai.com/v1"
        model = os.environ.get("LLM_MODEL", default_model).strip()
        base_url = os.environ.get("LLM_BASE_URL", default_base_url).rstrip("/")
        api_key = (
            os.environ.get("COHERE_API_KEY")
            if provider == "cohere"
            else os.environ.get("OPENAI_API_KEY")
        ) or os.environ.get("LLM_API_KEY")
        return cls(provider=provider, model=model, base_url=base_url, api_key=api_key)


class InterviewAgent:
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_env()

    def reply(
        self,
        *,
        candidate_message: str,
        history: list[dict],
        topic_title: str | None,
        question_title: str | None,
        problem_statement: str | None,
    ) -> str:
        if not self.config.api_key or self.config.api_key.startswith("replace-with"):
            return (
                "LLM is not configured yet. Add `COHERE_API_KEY`, `OPENAI_API_KEY`, or `LLM_API_KEY` to your environment, "
                "optionally set `LLM_MODEL`, then restart the Flask app."
            )

        messages = self._build_messages(
            candidate_message=candidate_message,
            history=history,
            topic_title=topic_title,
            question_title=question_title,
            problem_statement=problem_statement,
        )
        if self.config.provider == "cohere":
            return self._cohere_chat(messages)
        if self.config.provider != "openai":
            return "Unsupported `LLM_PROVIDER`. Use `cohere` or `openai`."
        return self._openai_chat(messages)

    def _build_messages(
        self,
        *,
        candidate_message: str,
        history: list[dict],
        topic_title: str | None,
        question_title: str | None,
        problem_statement: str | None,
    ) -> list[dict[str, str]]:
        resource = {
            "selected_problem": {
                "topic": topic_title,
                "title": question_title,
                "problem_statement": problem_statement,
            },
            "available_tools": [
                "search_problem_bank(query): search local DSA problems by title/topic/statement",
                "get_problem_bank_summary(): summarize available local interview resources",
            ],
        }
        messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": "MCP-style resources:\n" + json.dumps(resource, ensure_ascii=True)},
            {"role": "system", "content": "Problem bank summary:\n" + self.get_problem_bank_summary()},
        ]

        for item in history[-12:]:
            role = "assistant" if item.get("role") == "interviewer" else "user"
            content = item.get("content") or ""
            if content:
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": candidate_message})
        return messages

    def _openai_chat(self, messages: list[dict[str, str]]) -> str:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.5")),
            "tools": self._tool_specs(),
            "tool_choice": "auto",
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        response = self._post_chat_completion(payload, headers)
        data = response.json()
        message = data["choices"][0]["message"]

        if message.get("tool_calls"):
            messages = messages + [message]
            for call in message["tool_calls"]:
                result = self._run_tool_call(call)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": json.dumps(result, ensure_ascii=True),
                    }
                )
            return self._openai_chat_without_tools(messages)

        return (message.get("content") or "").strip()

    def _openai_chat_without_tools(self, messages: list[dict[str, Any]]) -> str:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.5")),
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        response = self._post_chat_completion(payload, headers)
        data = response.json()
        return (data["choices"][0]["message"].get("content") or "").strip()

    def _cohere_chat(self, messages: list[dict[str, str]]) -> str:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": self._cohere_messages(messages),
            "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.5")),
            "tools": self._tool_specs(),
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        response = self._post_cohere_chat(payload, headers)
        data = response.json()
        message = data.get("message", {})

        if message.get("tool_calls"):
            cohere_messages = payload["messages"] + [message]
            for call in message["tool_calls"]:
                result = self._run_tool_call(call)
                cohere_messages.append(self._cohere_tool_message(call, result))
            return self._cohere_chat_without_tools(cohere_messages, headers)

        return self._cohere_text(message)

    def _cohere_chat_without_tools(self, messages: list[dict[str, Any]], headers: dict[str, str]) -> str:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.5")),
            "tools": self._tool_specs(),
        }
        response = self._post_cohere_chat(payload, headers)
        return self._cohere_text(response.json().get("message", {}))

    def _post_chat_completion(self, payload: dict[str, Any], headers: dict[str, str]) -> requests.Response:
        response = requests.post(
            f"{self.config.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.config.timeout,
        )
        if response.ok:
            return response

        detail = response.text
        try:
            body = response.json()
            detail = body.get("error", {}).get("message") or detail
        except ValueError:
            pass
        raise RuntimeError(f"LLM API error {response.status_code}: {detail}")

    def _post_cohere_chat(self, payload: dict[str, Any], headers: dict[str, str]) -> requests.Response:
        response = requests.post(
            f"{self.config.base_url}/chat",
            headers=headers,
            json=payload,
            timeout=self.config.timeout,
        )
        if response.ok:
            return response

        detail = response.text
        try:
            body = response.json()
            detail = (
                body.get("message")
                or body.get("error", {}).get("message")
                or detail
            )
        except ValueError:
            pass
        raise RuntimeError(f"Cohere API error {response.status_code}: {detail}")

    def _cohere_messages(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        cohere_messages: list[dict[str, Any]] = []
        for message in messages:
            cohere_messages.append(
                {
                    "role": message["role"],
                    "content": [{"type": "text", "text": message["content"]}],
                }
            )
        return cohere_messages

    def _cohere_text(self, message: dict[str, Any]) -> str:
        chunks = message.get("content") or []
        return "".join(chunk.get("text", "") for chunk in chunks if chunk.get("type") == "text").strip()

    def _cohere_tool_message(self, call: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        return {
            "role": "tool",
            "tool_call_id": call["id"],
            "content": [
                {
                    "type": "document",
                    "document": {"data": json.dumps(result, ensure_ascii=True)},
                }
            ],
        }

    def _tool_specs(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_problem_bank",
                    "description": "Search local DSA problem resources by topic, title, or statement.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search phrase."}
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_problem_bank_summary",
                    "description": "Return a compact summary of local interview problem resources.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]

    def _run_tool_call(self, call: dict[str, Any]) -> dict[str, Any]:
        function = call.get("function") or {}
        name = function.get("name")
        try:
            args = json.loads(function.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}

        if name == "search_problem_bank":
            return {"results": self.search_problem_bank(args.get("query", ""))}
        if name == "get_problem_bank_summary":
            return {"summary": self.get_problem_bank_summary()}
        return {"error": f"Unknown tool: {name}"}

    def search_problem_bank(self, query: str, limit: int = 8) -> list[dict[str, str]]:
        terms = [term for term in query.lower().split() if term]
        results: list[tuple[int, dict[str, str]]] = []
        for topic in get_topics():
            for question in topic.get("questions", []):
                haystack = " ".join(
                    [
                        topic.get("title", ""),
                        question.get("title", ""),
                        question.get("problem_statement", ""),
                    ]
                ).lower()
                score = sum(1 for term in terms if term in haystack)
                if score:
                    results.append(
                        (
                            score,
                            {
                                "topic": topic.get("title", ""),
                                "title": question.get("title", ""),
                                "problem_statement": question.get("problem_statement", "")[:500],
                            },
                        )
                    )
        results.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in results[:limit]]

    def get_problem_bank_summary(self) -> str:
        topics = get_topics()
        lines = [f"{len(topics)} topics, {sum(len(t.get('questions', [])) for t in topics)} problems available."]
        for topic in topics:
            lines.append(f"- {topic.get('title')}: {len(topic.get('questions', []))} problems")
        return "\n".join(lines)
