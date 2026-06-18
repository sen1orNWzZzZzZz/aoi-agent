from typing import Dict

from tool_layer.base import BaseTool
from tool_layer.base import ToolResult, ToolSpec
from tool_layer.decorator import register_tool

# @register_tool("hello_world_tool")
class HelloWorldTool(BaseTool):
    def get_spec(self):
        return ToolSpec(name="hello_world_tool",description="这是一个helloworld的工具",params={}, returns=any)
    
    def execute_tool(self):
        content = self.helloworld()

        return ToolResult(success=True, content=content) 
    
    def validate_args(self, tool_args):
        if tool_args is None:
            return True, None
        return True, None

    def helloworld(self):
        return "hello tools"