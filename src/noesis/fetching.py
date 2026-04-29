from __future__ import annotations

from bs4 import BeautifulSoup
import httpx

from noesis.models import FetchResult, SourceCandidate


class HttpSourceFetcher:
    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def fetch(self, candidate: SourceCandidate) -> FetchResult:
        response = httpx.get(
            candidate.url,
            follow_redirects=True,
            timeout=self.timeout,
            headers={"User-Agent": "Noesis/0.1"},
        )
        response.raise_for_status()
        published_date = _extract_published_date(response.text)
        return FetchResult(
            candidate=candidate,
            final_url=str(response.url),
            status_code=response.status_code,
            content_type=response.headers.get("content-type"),
            raw_content=response.content,
            published_date=published_date,
        )


def _extract_published_date(raw_html: bytes) -> str | None:
    try:
        parsed_html = raw_html.decode("utf-8", errors="ignore")
    except Exception:
        return None
    soup = BeautifulSoup(parsed_html, "html.parser")
    selectors = (
        ("meta", "property", "article:published_time"),
        ("meta", "property", "article:modified_time"),
        ("meta", "name", "pubdate"),
        ("meta", "name", "publishdate"),
        ("meta", "name", "date"),
    )

    for tag, attr, value in selectors:
        node = soup.find(tag, attrs={attr: value})
        if node and node.get("content"):
            return str(node["content"])
    return None
