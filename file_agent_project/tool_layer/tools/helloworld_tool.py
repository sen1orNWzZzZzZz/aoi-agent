from tool_layer.base import BaseTool
from tool_layer.base import ToolResult, ToolSpec
from tool_layer.registry import register_tool

@register_tool("hello_world_tool")
class HelloWorldTool(BaseTool):
    def get_spec(self):
        return ToolSpec(name="helloworld",require_fields=[],description="这是一个helloworld的工具")
    
    def execute_tool(self):
        content = self.helloworld()

        return ToolResult(success=True, content=content) 
    
    def helloworld(self):
        return "hello tools"