import os

from tool_layer.base import ToolResult, BaseTool, ToolSpec, ToolResult, ValidationResult
from tool_layer.decorator import register_tool

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
        if self.validate_args(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    return ToolResult(success=True, content=f.read())
            except FileNotFoundError:
                return ToolResult(success=False, error_message="文件未找到")
            except Exception as e:
                return ToolResult(success=False, error_message=str(e))
        else:
            return ToolResult(success=False, content="", error_message="工具发生错误")

    def validate_business(self, **kwargs) -> ValidationResult:
        current_file = kwargs.get("file_name")
        if os.path.exists(current_file):
            return ValidationResult(validate=True)
        else:
            return ValidationResult(validate=False, error="文件不存在")
