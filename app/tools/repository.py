
import shutil
import subprocess
import tempfile
from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
}


def clone_repository(repo_url: str) -> str:
    """Clone a GitHub repository into a temporary directory."""

    if not repo_url or not repo_url.strip():
        raise ValueError("Repository URL cannot be empty.")

    destination_path = Path(
        tempfile.mkdtemp(prefix="reporeview_")
    )

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                repo_url.strip(),
                str(destination_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    except subprocess.CalledProcessError as error:
        shutil.rmtree(
            destination_path,
            ignore_errors=True,
        )

        raise RuntimeError(
            f"Failed to clone repository:\n{error.stderr}"
        ) from error

    return str(destination_path.resolve())


def get_repository_structure(
    repository_path: str,
) -> list[str]:
    """Return relevant files and directories in a repository."""

    root = Path(repository_path)

    if not root.exists():
        raise FileNotFoundError(
            f"Repository not found: {repository_path}"
        )

    structure = []

    for path in root.rglob("*"):
        relative_path = path.relative_to(root)

        if any(
            part in IGNORED_DIRECTORIES
            for part in relative_path.parts
        ):
            continue

        structure.append(str(relative_path))

    return sorted(structure)


def read_file(
    repository_path: str,
    file_path: str,
) -> str:
    """Read a text file safely from the repository."""

    root = Path(repository_path).resolve()

    target = (
        root / file_path
    ).resolve()

    # Prevent path traversal outside the repository.
    if root not in target.parents and target != root:
        raise ValueError(
            "File path must remain inside the repository."
        )

    if not target.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not target.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    try:
        return target.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except OSError as error:
        raise RuntimeError(
            f"Could not read file: {file_path}"
        ) from error

