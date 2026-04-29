from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urljoin, urldefrag, urlparse

from bs4 import BeautifulSoup

from noesis.models import NormalizedHtmlDocument, NormalizedLink


def normalize_run_html_sources(run_path: Path) -> list[Path]:
    sources_path = run_path / "sources"
    normalized_paths: list[Path] = []

    if not sources_path.exists():
        return normalized_paths

    for source_dir in sorted(path for path in sources_path.iterdir() if path.is_dir()):
        raw_html_path = source_dir / "raw.html"
        if not raw_html_path.exists():
            continue
        normalized_paths.append(normalize_html_source(source_dir))

    return normalized_paths


def normalize_html_source(source_dir: Path) -> Path:
    metadata = json.loads((source_dir / "metadata.json").read_text(encoding="utf-8"))
    raw_html = (source_dir / "raw.html").read_text(encoding="utf-8", errors="ignore")
    document = _extract_document(raw_html, metadata)

    normalized_path = source_dir / "normalized.json"
    normalized_path.write_text(
        json.dumps(document.to_dict(), indent=2),
        encoding="utf-8",
    )
    return normalized_path


def _extract_document(raw_html: str, metadata: dict[str, object]) -> NormalizedHtmlDocument:
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag_name in ("script", "style", "noscript", "svg"):
        for node in soup.find_all(tag_name):
            node.decompose()

    content_root = _select_content_root(soup)
    for tag_name in ("header", "nav", "footer", "aside", "form"):
        for node in content_root.find_all(tag_name):
            node.decompose()
    final_url = str(metadata.get("final_url") or metadata.get("url") or "")
    title = _extract_title(soup)
    headings = _extract_headings(content_root)
    text = _extract_text(content_root)
    links = _extract_links(content_root, final_url)

    return NormalizedHtmlDocument(
        source_id=str(metadata.get("source_id") or source_dir_name(metadata)),
        final_url=final_url,
        title=title,
        headings=headings,
        text=text,
        links=links,
    )


def _extract_title(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    heading = soup.find(["h1", "h2"])
    return heading.get_text(" ", strip=True) if heading else ""


def _select_content_root(soup: BeautifulSoup):
    candidates = [node for node in (soup.find("article"), soup.find("main"), soup.body) if node]
    if not candidates:
        return soup

    def score(node) -> int:
        text_length = len(node.get_text(" ", strip=True))
        structure_bonus = (
            len(node.find_all("p")) * 20
            + len(node.find_all(["h1", "h2", "h3"])) * 30
            + len(node.find_all("a", href=True)) * 5
        )
        return text_length + structure_bonus

    return max(candidates, key=score)


def _extract_headings(content_root) -> list[str]:
    headings: list[str] = []
    for heading in content_root.find_all(["h1", "h2", "h3"]):
        text = heading.get_text(" ", strip=True)
        if text and text not in headings:
            headings.append(text)
    return headings


def _extract_text(content_root) -> str:
    text_chunks: list[str] = []
    for node in content_root.find_all(["p", "li", "blockquote"]):
        text = node.get_text(" ", strip=True)
        if text:
            text_chunks.append(text)
    return "\n".join(text_chunks)


def _extract_links(content_root, base_url: str) -> list[NormalizedLink]:
    links: list[NormalizedLink] = []
    seen_urls: set[str] = set()
    for anchor in content_root.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href:
            continue
        absolute = urljoin(base_url, href)
        clean_url, _ = urldefrag(absolute)
        if not clean_url.startswith("http") or clean_url in seen_urls:
            continue
        if _is_noise_link(clean_url):
            continue
        text = anchor.get_text(" ", strip=True)
        if not text:
            continue
        links.append(NormalizedLink(url=clean_url, text=text))
        seen_urls.add(clean_url)
    return links


def _is_noise_link(url: str) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    noisy_domains = (
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "pinterest.com",
        "threads.net",
        "tiktok.com",
        "twitter.com",
        "x.com",
        "youtube.com",
    )
    if any(domain == noisy or domain.endswith(f".{noisy}") for noisy in noisy_domains):
        return True

    noisy_path_markers = (
        "/share",
        "/shares",
        "/login",
        "/signin",
        "/signup",
        "/register",
        "/account",
        "/privacy",
        "/terms",
        "/cookie",
    )
    return any(marker in path for marker in noisy_path_markers)


def source_dir_name(metadata: dict[str, object]) -> str:
    return str(metadata.get("source_id") or "source")
