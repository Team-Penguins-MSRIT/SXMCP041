"""
Deterministic commit-concentration metrics (no LLM).

Bus factor breadth: contributors_90pct = smallest k such that the top k authors
(by commit count) account for at least 90pct of commits. Higher k means work is
spread across more people (healthier). Lower k means higher key-person risk.

Systemic risk level and the 1-10 score both increase when breadth is low or
when concentration (HHI) is high.
"""

from __future__ import annotations

from typing import Any


def _systemic_risk_level(n: int, k90: int, k50: int, top_share: float) -> str:
    """Higher systemic risk when fewer contributors are needed for most commits."""
    if n <= 1:
        return "CRITICAL"
    if k90 <= 1:
        return "CRITICAL"
    if k50 == 1 and top_share >= 0.45:
        return "HIGH"
    if k90 == 2:
        return "HIGH"
    if k90 <= 3:
        return "MEDIUM"
    if top_share >= 0.35:
        return "MEDIUM"
    if k90 <= 4:
        return "LOW-MEDIUM"
    return "LOW"


def concentration_from_counts(author_counts: dict[str, int]) -> dict[str, Any]:
    total = sum(author_counts.values())
    if total <= 0:
        return {
            "total_commits": 0,
            "contributor_count": 0,
            "hhi": 0.0,
            "effective_contributors": 0.0,
            "contributors_50pct": 0,
            "contributors_90pct": 0,
            "top_share": 0.0,
            "concentration_index": 0.0,
            "key_person_risk_score": 0,
            "risk_level": "UNKNOWN",
            "repository_bus_factor_breadth": 0,
        }

    shares = sorted((c / total for c in author_counts.values()), reverse=True)
    n = len(shares)
    top_share = float(shares[0])
    hhi = sum(s * s for s in shares)
    n_eff = (1.0 / hhi) if hhi > 1e-15 else float(n)

    if n <= 1:
        c_norm = 1.0
    else:
        hhi_min = 1.0 / n
        denom = 1.0 - hhi_min
        if denom > 1e-12:
            c_norm = max(0.0, min(1.0, (hhi - hhi_min) / denom))
        else:
            c_norm = 1.0

    conc_score = 1.0 + 9.0 * c_norm

    cum = 0.0
    k50: int | None = None
    k90: int | None = None
    for i, s in enumerate(shares, start=1):
        cum += s
        if k50 is None and cum + 1e-12 >= 0.50:
            k50 = i
        if cum + 1e-12 >= 0.90:
            k90 = i
            break
    k50 = k50 if k50 is not None else n
    k90 = k90 if k90 is not None else n

    if n <= 1:
        breadth_score = 10.0
    else:
        breadth_score = 1.0 + 9.0 * (1.0 - (k90 - 1) / max(n - 1, 1))

    risk_score = int(round(max(breadth_score, conc_score)))
    risk_score = max(1, min(10, risk_score))

    risk_level = _systemic_risk_level(n, k90, k50, top_share)

    # Keep the 1–10 dial consistent with the qualitative band (e.g. HIGH implies elevated score).
    _floor = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 5, "LOW-MEDIUM": 4, "LOW": 1}
    risk_score = max(risk_score, _floor.get(risk_level, 1))
    risk_score = min(10, risk_score)

    return {
        "total_commits": total,
        "contributor_count": n,
        "hhi": round(hhi, 4),
        "effective_contributors": round(n_eff, 2),
        "contributors_50pct": int(k50),
        "contributors_90pct": int(k90),
        "top_share": round(top_share, 4),
        "concentration_index": round(c_norm, 4),
        "key_person_risk_score": risk_score,
        "risk_level": risk_level,
        "repository_bus_factor_breadth": int(k90),
    }
