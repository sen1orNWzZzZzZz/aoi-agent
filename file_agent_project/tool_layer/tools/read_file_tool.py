from tool_layer.base import ToolResult, BaseTool, ToolSpec, ToolResult
from tool_layer.decorator import register_tool

@register_tool("read_file")
class ReadFileTool(BaseTool):
    def get_spec(self):
        return ToolSpec(
            name="read_file",
            description="读取指定文件内容",
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
        # 直接拿具名参数，不用解包 kwargs
        return read_file(file_name)

    def validate_args(self, tool_args: dict) -> tuple[bool, str | None]:
        if "file_name" not in tool_args:
            return False, "缺少必填参数: file_name"
        return True, None

