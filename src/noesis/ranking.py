from __future__ import annotations

from noesis.models import SourceCandidate


def prioritize_candidates(candidates: list[SourceCandidate]) -> list[SourceCandidate]:
    def priority(candidate: SourceCandidate) -> tuple[int, str]:
        tier = 0 if candidate.source_type == "official" else 1
        return (tier, candidate.domain)

    return sorted(candidates, key=priority)
