
from pathlib import Path

import pytest

from app.report import generate_markdown_report
from app.models import (
    CodeQualityFinding,
    CodeReview,
    SecurityFinding,
)
from app.tools.repository import (
    get_repository_structure,
    read_file,
)


def test_get_repository_structure(tmp_path: Path):
    """Repository structure should include files and directories."""

    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    structure = get_repository_structure(
        str(tmp_path)
    )

    assert "app" in structure
    assert str(Path("app") / "main.py") in structure


def test_ignored_directories_are_excluded(
    tmp_path: Path,
):
    """Ignored directories should not appear in the structure."""

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text(
        "test",
        encoding="utf-8",
    )

    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "package.js").write_text(
        "test",
        encoding="utf-8",
    )

    (tmp_path / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    structure = get_repository_structure(
        str(tmp_path)
    )

    assert "main.py" in structure
    assert ".git" not in structure
    assert ".git/config" not in structure
    assert "node_modules" not in structure


def test_read_file(tmp_path: Path):
    """read_file should return the contents of a valid file."""

    file_path = tmp_path / "README.md"

    file_path.write_text(
        "# RepoReview",
        encoding="utf-8",
    )

    content = read_file(
        str(tmp_path),
        "README.md",
    )

    assert content == "# RepoReview"


def test_read_file_blocks_path_traversal(
    tmp_path: Path,
):
    """read_file must prevent access outside the repository."""

    outside_file = tmp_path.parent / "secret.txt"

    outside_file.write_text(
        "secret",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        read_file(
            str(tmp_path),
            "../secret.txt",
        )


def test_read_file_missing_file(tmp_path: Path):
    """read_file should raise an error for missing files."""

    with pytest.raises(FileNotFoundError):
        read_file(
            str(tmp_path),
            "missing.txt",
        )


def test_generate_markdown_report():
    """Markdown report should contain the review sections."""

    review = CodeReview(
        repository="test/repository",
        summary="Test repository review.",
        strengths=[
            "Good project structure.",
        ],
        quality_findings=[
            CodeQualityFinding(
                title="Missing tests",
                description="More tests are needed.",
                severity="medium",
                file="tests/test_app.py",
                line=10,
                recommendation="Add unit tests.",
            )
        ],
        security_findings=[
            SecurityFinding(
                title="Debug mode enabled",
                description="Debug mode should be disabled.",
                severity="high",
                file="settings.py",
                line=20,
                recommendation="Set DEBUG to False.",
            )
        ],
        recommendations=[
            "Improve test coverage.",
            "Harden production configuration.",
        ],
    )

    report = generate_markdown_report(review)

    assert "# Code Review: test/repository" in report
    assert "## Summary" in report
    assert "## Strengths" in report
    assert "## Code Quality Findings" in report
    assert "## Security & Bug Findings" in report
    assert "## Recommendations" in report

    assert "Missing tests" in report
    assert "Debug mode enabled" in report
    assert "Improve test coverage." in report

