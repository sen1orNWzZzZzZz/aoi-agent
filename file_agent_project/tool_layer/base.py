from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class ToolSpec:
    name: str
    # require_fields: List[str]
    description: str
    params: dict = field(default_factory=dict)       
    returns: str = "any" 
    # optional_fields: List[str] | None = None

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
    content: any | None = None
    error_message: str | None = None

class BaseTool(ABC):
    @abstractmethod
    def get_spec(self)->ToolSpec:
        pass

    @abstractmethod
    def execute_tool(self, **kwargs)->ToolResult:
        pass

    @abstractmethod
    def validate_args(self, tool_args:Dict[str,any])->tuple[bool, Optional[str]]:
        pass
