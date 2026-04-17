"""Single source of truth for repository root and common output dirs.

``sql/<category>/`` — budget, sector, segments, dim, profiling, cost_codes,
data_quality, analytics, curated.

``data/<category>/`` — projects, budget, closeout, cost_codes, dim, sector,
profiling, mappings, sharepoint, quality, analysis.
"""
from pathlib import Path


def repo_root() -> Path:
    """Workspace root (parent of Python/)."""
    return Path(__file__).resolve().parents[1]


def reports_dir() -> Path:
    """Generated HTML reports (standalone dashboards, embed targets)."""
    return repo_root() / "reports"


def sql_path(*parts: str) -> Path:
    """Path under ``sql/``, e.g. ``sql_path('budget', 'foo.sql')``."""
    return repo_root().joinpath("sql", *parts)


def data_path(*parts: str) -> Path:
    """Path under ``data/``, e.g. ``data_path('projects', 'out.csv')``."""
    return repo_root().joinpath("data", *parts)
