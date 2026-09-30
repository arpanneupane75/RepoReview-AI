from pydantic_ai import RunContext

from app.tools.repository import (
    get_repository_structure,
    read_file,
)


@agent.tool
def get_repo_structure(ctx: RunContext[str]) -> list[str]:
    """Return the relevant files and directories in the repository."""
    return get_repository_structure(ctx.deps)


@agent.tool
def read_repo_file(
    ctx: RunContext[str],
    file_path: str,
) -> str:
    """Read a text file from the repository."""
    return read_file(ctx.deps, file_path)