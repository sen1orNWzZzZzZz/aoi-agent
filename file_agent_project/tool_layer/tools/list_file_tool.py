from tool_layer.decorator import register_tool
from tool_layer.base import BaseTool
from tool_layer.base import ToolResult, ToolSpec
from core.constants import WORKSPACE_ROOT
from rich.tree import Tree
from rich.filesize import decimal
from rich.console import Console
from pathlib import Path

@register_tool("list_files_tool")
class ListFileTool(BaseTool):
    def get_spec(self):
        return ToolSpec(
            name="list_files_tool",
            description="这是一个列出目录的工具，可以在指定目录下列出当前目录下的文件树",
            params={
                "target_dir": {
                    "type": "string",
                    "require": True,
                    "default": WORKSPACE_ROOT
                }
            },
            returns=ToolResult
        )
    
    def execute_tool(self, tool_args):
        if not self.validate_args(tool_args):
            return ToolResult(success=False, error_message="参数不正确")
        
        root = Path(tool_args["target_dir"])
        
        if not root.exists():
            return ToolResult(success=False, error_message=f"目录不存在: {root}")
        
        tree = Tree(f"📁 [bold green]{root.name}")
        
        try:
            self.build_rich_tree(root, tree)
            console = Console(record=True)
            console.print(tree)
            tree_str = console.export_text()
        except Exception as e:
            return ToolResult(success=False, error_message=str(e))
        
        return ToolResult(success=True, content={"tree": tree_str})
    
    def validate_args(self, tool_args):
        if not tool_args or not isinstance(tool_args, dict):
            return False
        return "target_dir" in tool_args
    
    def build_rich_tree(self, directory: Path, tree: Tree, ignore=None):
        if ignore is None:
            ignore = {'.git', '__pycache__', '.idea', '.vscode', 'node_modules'}
        
        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda e: (not e.is_dir(), e.name.lower())
            )
        except PermissionError:
            tree.add("🔒 [dim][权限拒绝]")
            return
        
        for entry in entries:
            if entry.name in ignore:
                continue
                
            if entry.is_dir():
                branch = tree.add(f"📁 [bold]{entry.name}")
                self.build_rich_tree(entry, branch, ignore)
            else:
                size = decimal(entry.stat().st_size)
                tree.add(f"📄 {entry.name} [dim]({size})")
