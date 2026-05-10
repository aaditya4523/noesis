from __future__ import annotations

import os
from typing import Protocol

import httpx

from noesis.errors import ProviderError, extract_http_error_message
from noesis.embeddings import MissingGeminiApiKeyError


class AnswerGenerator(Protocol):
    def generate_answer(self, *, question: str, evidence_rows: list[dict[str, object]]) -> str: ...


class GeminiAnswerGenerator:
    def __init__(self, *, api_key: str | None = None, model: str = "gemini-3-flash-preview") -> None:
        resolved_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_key:
            raise MissingGeminiApiKeyError("GEMINI_API_KEY is required for the answer command")
        self._api_key = resolved_key
        self._model = model

    def generate_answer(self, *, question: str, evidence_rows: list[dict[str, object]]) -> str:
        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent",
                headers={"x-goog-api-key": self._api_key, "Content-Type": "application/json"},
                json={
                    "system_instruction": {
                        "parts": [
                            {
                                "text": (
                                    "Answer only from the provided evidence. "
                                    "If the evidence is insufficient, say so clearly. "
                                    "Do not invent facts."
                                )
                            }
                        ]
                    },
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": _build_answer_prompt(question, evidence_rows),
                                }
                            ],
                        }
                    ],
                },
                timeout=60.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            message = extract_http_error_message(exc) or "Gemini generation request failed"
            raise ProviderError(message) from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Gemini generation request failed: {exc}") from exc
        payload = response.json()
        candidates = payload.get("candidates", [])
        if not candidates:
            raise ProviderError("Gemini generation returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts = [str(part.get("text", "")) for part in parts if part.get("text")]
        answer = "\n".join(text_parts).strip()
        if not answer:
            raise ProviderError("Gemini generation returned an empty answer")
        return answer


def answer_question(
    *,
    question: str,
    evidence_rows: list[dict[str, object]],
    generator: AnswerGenerator,
) -> str:
    return generator.generate_answer(question=question, evidence_rows=evidence_rows)


def _build_answer_prompt(question: str, evidence_rows: list[dict[str, object]]) -> str:
    context_blocks: list[str] = []
    for row in evidence_rows:
        heading_path = row.get("heading_path")
        headings = " > ".join(_coerce_heading_path(heading_path))
        context_blocks.append(
            "\n".join(
                [
                    f"Title: {row['title']}",
                    f"Headings: {headings}",
                    f"Source URL: {row['source_url']}",
                    f"Content: {row['text']}",
                ]
            )
        )
    joined_context = "\n\n".join(context_blocks)
    return f"Question: {question}\n\nContext:\n{joined_context}"


def _coerce_heading_path(value: object) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("heading_path must be a list")
    headings: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise TypeError("heading_path items must be strings")
        headings.append(item)
    return headings
