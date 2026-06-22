"""Architecture guard: only data.loader may reference mock_data files directly."""

from __future__ import annotations

from pathlib import Path


def test_only_loader_references_mock_data() -> None:
    """Ensure agent code does not read mock data files directly."""
    project_root = Path(__file__).resolve().parent.parent
    allowed = project_root / "data" / "loader.py"

    candidate_paths: list[Path] = []
    for pattern in ("tools/**/*.py", "data/**/*.py", "agent.py", "models.py"):
        candidate_paths.extend(project_root.glob(pattern))

    violations: list[str] = []
    for path in candidate_paths:
        if path == allowed or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "mock_data/" in text or "mock_data\\" in text:
            violations.append(str(path.relative_to(project_root)))

    assert not violations, (
        "Direct mock_data references found outside data/loader.py: "
        + ", ".join(sorted(violations))
    )
