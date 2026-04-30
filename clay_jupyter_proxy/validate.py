"""Path validation for Clay render requests.

v1 policy: only files under notebooks/ with a .clj extension are accepted.
"""

from pathlib import Path


def validate_render_path(source_path: str, workspace_root: str) -> str | None:
    """Validate a workspace-relative render path.

    Returns an error string describing the violation, or None if the path is
    acceptable.
    """
    if not source_path:
        return "path must not be empty"

    p = Path(source_path)

    if p.is_absolute():
        return "path must be workspace-relative, not absolute"

    root = Path(workspace_root).resolve()
    resolved = (root / p).resolve()

    # Reject anything that escapes the workspace root.
    try:
        resolved.relative_to(root)
    except ValueError:
        return "path traversal is not allowed"

    # v1 policy: only notebooks/*.clj
    try:
        resolved.relative_to(root / "notebooks")
    except ValueError:
        return "only files under notebooks/ are supported in v1"

    if resolved.suffix != ".clj":
        return "only .clj files are supported"

    return None
