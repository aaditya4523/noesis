import json
from pathlib import Path

from noesis.normalization import normalize_html_source, normalize_run_html_sources


ARTICLE_HTML = """
<html>
  <head>
    <title>Distributed Systems Primer</title>
    <meta property="og:type" content="article" />
    <meta property="article:published_time" content="2026-01-02T00:00:00Z" />
  </head>
  <body>
    <main>
      <h1>Distributed Systems Primer</h1>
      <p>Distributed systems are collections of independent computers.</p>
      <h2>Replication</h2>
      <p>Replication improves availability and read throughput for critical data.</p>
      <h2>Sharding</h2>
      <p>Sharding partitions data to distribute write and storage load across nodes.</p>
      <a href="https://example.com/child-article">Child article</a>
      <a href="https://external.example.org/reference">External reference</a>
    </main>
  </body>
</html>
"""


HUB_HTML = """
<html>
  <head>
    <title>System Design Topics List</title>
  </head>
  <body>
    <main>
      <h1>System Design Topics</h1>
      <p>Use this roadmap to study the major system design concepts.</p>
      <ul>
        <li><a href="https://example.com/system-design/load-balancing">Load Balancing</a></li>
        <li><a href="https://example.com/system-design/caching">Caching</a></li>
        <li><a href="https://example.com/system-design/sharding">Sharding</a></li>
        <li><a href="https://example.com/system-design/pubsub">Pub/Sub</a></li>
        <li><a href="https://example.com/system-design/queues">Queues</a></li>
        <li><a href="https://example.com/system-design/consistency">Consistency</a></li>
      </ul>
    </main>
  </body>
</html>
"""


MISLEADING_ARTICLE_HTML = """
<html>
  <head>
    <title>System Design Deep Dive</title>
    <meta property="og:type" content="article" />
  </head>
  <body>
    <main>
      <h1>System Design Deep Dive</h1>
      <p>This guide explains scalability, consistency, queues, and caches in depth.</p>
      <p>It walks through trade-offs with examples and concrete architecture choices.</p>
      <a href="https://example.com/system-design/caching">Caching article</a>
    </main>
    <article>
      <p>Short promo block.</p>
    </article>
  </body>
</html>
"""


def test_normalize_html_source_extracts_article_content(tmp_path: Path):
    source_dir = _create_html_source(
        tmp_path,
        source_id="source-001",
        final_url="https://example.com/distributed-systems-primer",
        raw_html=ARTICLE_HTML,
    )

    normalized_path = normalize_html_source(source_dir)

    data = json.loads(normalized_path.read_text(encoding="utf-8"))
    assert data["title"] == "Distributed Systems Primer"
    assert data["headings"] == ["Distributed Systems Primer", "Replication", "Sharding"]
    assert "text" not in data
    assert data["sections"] == [
        {
            "heading_path": ["Distributed Systems Primer"],
            "paragraphs": ["Distributed systems are collections of independent computers."],
        },
        {
            "heading_path": ["Distributed Systems Primer", "Replication"],
            "paragraphs": ["Replication improves availability and read throughput for critical data."],
        },
        {
            "heading_path": ["Distributed Systems Primer", "Sharding"],
            "paragraphs": ["Sharding partitions data to distribute write and storage load across nodes."],
        },
    ]
    assert data["links"] == [
        {"url": "https://example.com/child-article", "text": "Child article"},
        {"url": "https://external.example.org/reference", "text": "External reference"},
    ]


def test_normalize_html_source_detects_hub_and_preserves_child_links(tmp_path: Path):
    source_dir = _create_html_source(
        tmp_path,
        source_id="source-002",
        final_url="https://example.com/system-design/topics",
        raw_html=HUB_HTML,
    )

    normalized_path = normalize_html_source(source_dir)

    data = json.loads(normalized_path.read_text(encoding="utf-8"))
    assert len(data["links"]) == 6
    assert data["sections"] == [
        {
            "heading_path": ["System Design Topics"],
            "paragraphs": [
                "Use this roadmap to study the major system design concepts.",
                "Load Balancing",
                "Caching",
                "Sharding",
                "Pub/Sub",
                "Queues",
                "Consistency",
            ],
        }
    ]
    assert {"url": "https://example.com/system-design/caching", "text": "Caching"} in data["links"]


def test_normalize_run_html_sources_skips_non_html_sources(tmp_path: Path):
    run_path = tmp_path / "system-design-run"
    (run_path / "sources").mkdir(parents=True)

    html_source = _create_html_source(
        run_path / "sources",
        source_id="source-001",
        final_url="https://example.com/article",
        raw_html=ARTICLE_HTML,
    )
    pdf_source = run_path / "sources" / "source-002"
    pdf_source.mkdir(parents=True)
    (pdf_source / "raw.pdf").write_bytes(b"%PDF-1.7 fake")
    (pdf_source / "metadata.json").write_text(
        json.dumps(
            {
                "source_id": "source-002",
                "url": "https://example.com/slides.pdf",
                "final_url": "https://example.com/slides.pdf",
                "content_type": "application/pdf",
            }
        ),
        encoding="utf-8",
    )

    normalized_paths = normalize_run_html_sources(run_path)

    assert len(normalized_paths) == 1
    assert normalized_paths[0] == html_source / "normalized.json"
    assert not (pdf_source / "normalized.json").exists()


def test_normalize_html_source_picks_richest_content_root(tmp_path: Path):
    source_dir = _create_html_source(
        tmp_path,
        source_id="source-003",
        final_url="https://example.com/system-design-deep-dive",
        raw_html=MISLEADING_ARTICLE_HTML,
    )

    normalized_path = normalize_html_source(source_dir)

    data = json.loads(normalized_path.read_text(encoding="utf-8"))
    assert data["title"] == "System Design Deep Dive"
    assert "text" not in data
    assert data["sections"] == [
        {
            "heading_path": ["System Design Deep Dive"],
            "paragraphs": [
                "This guide explains scalability, consistency, queues, and caches in depth.",
                "It walks through trade-offs with examples and concrete architecture choices.",
            ],
        }
    ]
    assert data["links"] == [
        {"url": "https://example.com/system-design/caching", "text": "Caching article"}
    ]


def _create_html_source(parent: Path, source_id: str, final_url: str, raw_html: str) -> Path:
    source_dir = parent / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "raw.html").write_text(raw_html, encoding="utf-8")
    (source_dir / "metadata.json").write_text(
        json.dumps(
            {
                "source_id": source_id,
                "url": final_url,
                "final_url": final_url,
                "content_type": "text/html",
            }
        ),
        encoding="utf-8",
    )
    return source_dir
