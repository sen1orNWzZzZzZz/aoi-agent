import os

from tool_layer.base import ToolResult, BaseTool, ToolSpec, ToolResult, ValidationResult
from tool_layer.decorator import register_tool
from core.path_utils import resolve_workspace_path

@register_tool("read_file")
class ReadFileTool(BaseTool):
    def get_spec(self):
        return ToolSpec(
            name="read_file",
            description="这是一个文件读取的工具，通过文件路径来读取指定文件内容",
            params={
                "file_name": {
                    "type": "string",
                    "required": True,
                    "default": None
                }
            },
            returns="string"
        )

    def execute_tool(self, file_name: str) -> ToolResult:
        try:
            with open(resolve_workspace_path(path_str=file_name), 'r', encoding='utf-8') as f:
                return ToolResult(success=True, content=f.read(),tool_name="read_file", tool_args={"file_name":file_name})
        except Exception as e:
            return ToolResult(success=False, tool_name="read_file", tool_args={"file_name":file_name},error_message=str(e))



    def validate_business(self, **kwargs) -> ValidationResult:
        current_file = kwargs.get("file_name")
        try:
            if os.path.exists(resolve_workspace_path(current_file)):
                return ValidationResult(validate=True)
            else:
                return ValidationResult(validate=False, error="文件不存在")
        except Exception as e:
            return ValidationResult(validate=False, error=str(e))
