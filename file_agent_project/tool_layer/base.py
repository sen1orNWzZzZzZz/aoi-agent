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
    optional_fields: List[str] | None = None

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
    tool_name: str
    content: any | None = None
    error_message: str | None = None
    tool_args: dict | None = None
    
@dataclass
class ValidationResult:
    validate: bool
    error: str | None = None


class BaseTool(ABC):

      @abstractmethod
      def get_spec(self) -> ToolSpec:
          pass

      @abstractmethod
      def execute_tool(self, **kwargs) -> ToolResult:
          pass

      #自动基础校验
      def validate_args(self, **kwargs) -> ValidationResult:
          """
          默认实现：根据 ToolSpec 自动检查必填字段和基础类型。
          子类可以 override，也可以 super() 调用后再加自己的业务校验。
          """
          spec = self.get_spec()
          errors = []

          # 1. 检查必填
          for name, meta in spec.params.items():
              if meta.get("required") and kwargs.get(name) in (None, ""):
                  errors.append(f"参数 '{name}' 为必填项")

          # 2. 基础类型检查
          for name, meta in spec.params.items():
              expected_type = meta.get("type")
              value = kwargs.get(name)
              if value is not None and expected_type == "string" and not isinstance(value, str):
                  errors.append(f"参数 '{name}' 必须是字符串")

          if errors:
              return ValidationResult(validate=False, error="; ".join(errors))

          return ValidationResult(validate=True)

      #业务校验
      def validate_business(self, **kwargs) -> ValidationResult:
        
        #   子类只写业务层校验，比如：
        #   路径是否存在
        #   文件大小是否超限
        #   数值范围是否合理
          
          return ValidationResult(validate=True)
