from __future__ import annotations

import json

import httpx


class NoesisError(RuntimeError):
    pass


class NoesisConfigurationError(NoesisError):
    pass


class DiscoveryError(NoesisError):
    pass


class FetchError(NoesisError):
    pass


class DataNotFoundError(NoesisError):
    pass


class ProviderError(NoesisError):
    pass


class VectorStoreError(NoesisError):
    pass


def extract_http_error_message(exc: httpx.HTTPStatusError) -> str | None:
    response = exc.response
    try:
        payload = response.json()
    except (ValueError, json.JSONDecodeError):
        return None

    error = payload.get("error")
    if not isinstance(error, dict):
        return None
    message = error.get("message")
    return str(message) if isinstance(message, str) and message.strip() else None
