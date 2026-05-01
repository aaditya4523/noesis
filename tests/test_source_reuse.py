from datetime import UTC, datetime

from noesis.source_reuse import canonicalize_url, should_refresh_source


def test_canonicalize_url_strips_fragment_and_tracking_params():
    assert canonicalize_url(
        "https://example.com/article/?utm_source=twitter&utm_medium=social#section-2"
    ) == "https://example.com/article"


def test_canonicalize_url_keeps_meaningful_query_params():
    assert canonicalize_url(
        "https://example.com/search?q=distributed+systems&page=2"
    ) == "https://example.com/search?page=2&q=distributed+systems"


def test_should_refresh_source_reuses_recent_source():
    now = datetime(2026, 5, 1, tzinfo=UTC)

    assert should_refresh_source(
        last_fetched_at="2025-08-15T00:00:00+00:00",
        now=now,
        ttl_days=365,
    ) is False


def test_should_refresh_source_refreshes_old_source():
    now = datetime(2026, 5, 1, tzinfo=UTC)

    assert should_refresh_source(
        last_fetched_at="2024-12-31T00:00:00+00:00",
        now=now,
        ttl_days=365,
    ) is True


def test_should_refresh_source_refreshes_when_timestamp_missing():
    now = datetime(2026, 5, 1, tzinfo=UTC)

    assert should_refresh_source(
        last_fetched_at=None,
        now=now,
        ttl_days=365,
    ) is True
