from core.path_utils import resolve_workspace_path, to_workspace_display
from core.schemas import ToolResult
from file_agent_project.tools.specs import ToolSpec

list_files_spec = ToolSpec(name="list_files", required_fields=[], repair_slots={"target_dir":"tool_args.target_dir"}, default_user_messages={"target_dir":"请提供正确的文件夹路径名"})

def list_files(target_dir: str = "") -> ToolResult:
    try:
        directory = resolve_workspace_path(target_dir)
    except ValueError as error:
        return ToolResult(
            tool_name="list_files",
            success=False,
            content="",
            error_message=str(error),
        )

    if not directory.exists():
        return ToolResult(
            tool_name="list_files",
            success=False,
            content="",
            error_message="目标目录不存在，请确认路径是否正确。",
        )

    if not directory.is_dir():
        return ToolResult(
            tool_name="list_files",
            success=False,
            content="",
            error_message="给定路径不是目录，无法列出文件。",
        )

    try:
        items = []
        for item in sorted(directory.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.lower())):
            display_name = to_workspace_display(item)
            if item.is_dir():
                display_name = f"{display_name}/"
            items.append(display_name)

        return ToolResult(
            tool_name="list_files",
            success=True,
            content="\n".join(items) if items else "(empty directory)",
            error_message="",
        )
    except Exception as error:
        return ToolResult(
            tool_name="list_files",
            success=False,
            content="",
            error_message=f"列出目录时发生错误: {error}",
        )
