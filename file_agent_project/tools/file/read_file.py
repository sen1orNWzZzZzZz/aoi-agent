from core.constants import MAX_FILE_CHARS
from core.path_utils import resolve_workspace_path, to_workspace_display
from core.schemas import ToolResult
from file_agent_project.tools.specs import ToolSpec

read_file_spec = ToolSpec(name="read_file", required_fields=["file_name"], repair_slots={"file_name":"tool_args.file_name"}, default_user_messages={"file_name":"请提供正确的文件路径名"})


def read_file(file_name: str) -> ToolResult:
    if not file_name:
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="缺少文件路径，需要用户补充明确的 file_name。",
        )

    try:
        file_path = resolve_workspace_path(file_name)
    except ValueError as error:
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message=str(error),
        )

    if not file_path.exists():
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="文件路径不存在，请补充正确的文件路径。",
        )

    if file_path.is_dir():
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="目标路径是目录，不是文件，请补充正确的文件路径。",
        )

    try:
        with file_path.open("r", encoding="utf-8") as file:
            file_content = file.read()
    except UnicodeDecodeError:
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="文件不是 UTF-8 编码，当前版本暂不支持读取。",
        )
    except Exception as error:
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message=f"打开文件时发生错误: {error}",
        )

    if len(file_content) > MAX_FILE_CHARS:
        file_content = (
            f"[文件: {to_workspace_display(file_path)}]\n"
            f"{file_content[:MAX_FILE_CHARS]}\n\n"
            "[文件内容过长，已截断]"
        )
    else:
        file_content = f"[文件: {to_workspace_display(file_path)}]\n{file_content}"

    return ToolResult(
        tool_name="read_file",
        content=file_content,
        success=True,
        error_message="",
    )

