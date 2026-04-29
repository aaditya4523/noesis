from __future__ import annotations

from urllib.parse import urlparse

from ddgs import DDGS

from noesis.models import SourceCandidate


class DDGSDiscoverer:
    def __init__(self, max_results: int = 10) -> None:
        self.max_results = max_results

    def discover(self, topic: str) -> list[SourceCandidate]:
        with DDGS() as ddgs:
            results = ddgs.text(topic, max_results=self.max_results)

        candidates: list[SourceCandidate] = []
        for result in results:
            url = result.get("href") or result.get("url")
            if not url:
                continue

            domain = urlparse(url).netloc
            candidates.append(
                SourceCandidate(
                    url=url,
                    title=result.get("title") or url,
                    domain=domain,
                    snippet=result.get("body"),
                    source_type=_classify_source_type(domain),
                )
            )
        return candidates


def _classify_source_type(domain: str) -> str:
    lowered = domain.lower()
    official_markers = (
        ".gov",
        ".edu",
        "docs.",
        "developer.",
        "api.",
        "support.",
        "learn.",
        "aws.amazon.com",
        "cloud.google.com",
        "learn.microsoft.com",
    )
    return "official" if any(marker in lowered for marker in official_markers) else "secondary"
