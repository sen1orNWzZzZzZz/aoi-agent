from tool_layer.decorator import register_tool
from tool_layer.base import BaseTool
from typing import Dict
from tool_layer.base import ToolResult, ToolSpec
from core.constants import WORKSPACE_ROOT

@register_tool("list_files_tool")
class ListFileTool(BaseTool):
    def get_spec(self):
        return ToolSpec(name="list_files_tool",
                        description="在指定目录下列出当前目录下的文件树",
                        params={"target_dir":{"type":"string",
                                              "require":True,
                                              "default": WORKSPACE_ROOT}},
                        returns=ToolResult)
    
    def execute_tool(self, **kwargs):
        return super().execute_tool(**kwargs)
    
    def validate_args(self, tool_args):
        return super().validate_args(tool_args)
    