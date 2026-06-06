from tool_layer.base import ToolResult, BaseTool, ToolSpec, ToolResult
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
                return f"错误：文件 '{file_name}' 不存在"
            except Exception as e:
                return f"读取出错：{e}"
        else:
            return ToolResult(success=False, content="", error_message="工具发生错误")

    def validate_args(self, file_name) -> tuple[bool, str | None]:
        if file_name is None or file_name=="":
            return False
        else:
            return True
