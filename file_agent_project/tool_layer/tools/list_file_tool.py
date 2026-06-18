import os

from tool_layer.decorator import register_tool
from tool_layer.base import ToolResult, ToolSpec, BaseTool, ValidationResult
from core.constants import WORKSPACE_ROOT
from core.path_utils import resolve_workspace_path
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
                    "required": True,
                    "default": WORKSPACE_ROOT
                }
            },
            returns="string"
        )

    def execute_tool(self, target_dir)->ToolResult:
        target = resolve_workspace_path(target_dir)

        #构建文件树
        result = []
        try:

            for root, dirs, files in os.walk(target):
                for d in dirs:
                    full = os.path.join(root, d)
                    result.append((os.path.relpath(full, WORKSPACE_ROOT).replace("\\", "/"), "directory"))#美化一下输出，稍微好看点吧，针对dbg来说
                for f in files:
                    full = os.path.join(root, f)
                    result.append((os.path.relpath(full, WORKSPACE_ROOT).replace("\\", "/"), "file"))
    
        except Exception as e:
            return ToolResult(success=False, error_message=str(e),tool_name="list_files_tool", tool_args={"target_dir":target_dir})
        
        return ToolResult(success=True, content={"tree": result},tool_name="list_files_tool", tool_args={"target_dir":target_dir})
    
    def validate_business(self, **kwargs)->ValidationResult:
        if kwargs.get("target_dir") is None:
            return ValidationResult(validate=False,error="参数为空或不存在")
        try:
            target = resolve_workspace_path(kwargs.get("target_dir"))
        except ValueError as ve:
            return ValidationResult(validate=False,error = str(ve))
        if not target.exists():
            return ValidationResult(validate=False, error=f"{target}文件夹不存在")
        if not target.is_dir():
            return ValidationResult(validate=False, error=f"{target}不是文件夹")

        # if not target.startswith(work_space+os.sep) and target!=work_space:
        #     return ValidationResult(validate=False, error=f"{target}超出工作目录范围，请求驳回")
            # return ToolResult(success=False,error_message=f"{target}超出工作目录范围，请求驳回",tool_name="list_file", tool_args={"target_dir":target_dir})
        
        return ValidationResult(validate=True)
    
    