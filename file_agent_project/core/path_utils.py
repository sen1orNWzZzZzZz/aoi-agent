from pathlib import Path

from core.constants import WORKSPACE_ROOT


def resolve_workspace_path(path_str: str = "") -> Path:
    raw_path = Path(path_str) if path_str else WORKSPACE_ROOT
    candidate = raw_path if raw_path.is_absolute() else WORKSPACE_ROOT / raw_path
    resolved = candidate.resolve(strict=False)

    if resolved != WORKSPACE_ROOT and WORKSPACE_ROOT not in resolved.parents:
        raise ValueError("目标路径超出工作区范围，当前 Agent 不允许访问。")

    return resolved


def to_workspace_display(path: Path) -> str:
    relative = path.relative_to(WORKSPACE_ROOT)
    return "." if str(relative) == "." else relative.as_posix()
