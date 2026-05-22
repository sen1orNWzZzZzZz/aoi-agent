from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ToolSpec:
    name: str
    require_fields: List[str]
    description: str
    optional_fields: List[str] | None

    def post_init(self):
        if self.optional_fields is None:
            self.optional_fields = []
    
    def to_dict(self):
        return {"name":self.name, 
                "require_fields":self.require_fields, 
                "description":self.description,
                "optional_fields":self.optional_fields}

@dataclass
class ToolResult:
    success: bool
    content: any
    error_message: str | None = None

class BaseTool(ABC):
    @abstractmethod
    def get_spec(self)->ToolSpec:
        pass

    @abstractmethod
    def execute_tool(self, tool_args:Dict[str, any])->ToolResult:
        pass

    def validate_args(self, tool_args:Dict[str,any])->tuple[bool, Optional[str]]:
        spec = self.get_spec()
        missing = [f for f in spec.require_fields if f not in tool_args]
        if missing:
            return False, f"缺少必填字段：{','.join(missing)}"
        else:
            return True, None
