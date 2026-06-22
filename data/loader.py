"""Mock data loader used by the agent and tools.

This module is the single access point for records in ``mock_data/``.
All other modules must call these loader functions instead of reading JSON
files directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_MOCK_DATA_DIR = Path(__file__).resolve().parent.parent / "mock_data"


def _load_json(filename: str) -> list[dict[str, Any]]:
    """Read and parse a JSON file from the mock data directory."""
    path = _MOCK_DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Mock data file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_budgets() -> list[dict[str, Any]]:
    """Return all cost center budget records."""
    return _load_json("budgets.json")


def load_vendors() -> list[dict[str, Any]]:
    """Return all vendor records."""
    return _load_json("vendors.json")


def load_policies() -> list[dict[str, Any]]:
    """Return all procurement policy records."""
    return _load_json("policies.json")


def load_requests() -> list[dict[str, Any]]:
    """Return all sample purchase request records."""
    return _load_json("requests.json")
