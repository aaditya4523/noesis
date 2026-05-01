from __future__ import annotations

from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


_TRACKING_PARAM_PREFIXES = ("utm_",)
_TRACKING_PARAM_NAMES = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
}


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or "/"
    query_items = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not _is_tracking_param(key)
    ]
    normalized_query = urlencode(sorted(query_items))
    normalized_path = "" if path == "/" else path
    return urlunsplit((parts.scheme, parts.netloc.lower(), normalized_path, normalized_query, ""))


def should_refresh_source(
    last_fetched_at: str | None,
    *,
    now: datetime | None = None,
    ttl_days: int = 365,
) -> bool:
    if not last_fetched_at:
        return True

    current_time = now or datetime.now(UTC)
    last_fetched = datetime.fromisoformat(last_fetched_at)
    if last_fetched.tzinfo is None:
        last_fetched = last_fetched.replace(tzinfo=UTC)
    return current_time - last_fetched > timedelta(days=ttl_days)


def _is_tracking_param(name: str) -> bool:
    lowered = name.lower()
    return lowered.startswith(_TRACKING_PARAM_PREFIXES) or lowered in _TRACKING_PARAM_NAMES
