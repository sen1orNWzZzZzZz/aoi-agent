import inspect
from typing import Dict, get_type_hints

from tool_layer.base import BaseTool, ToolSpec



class ToolRegistry:
    def __init__(self):
        # 核心存储：名字 -> {"实例": obj, "注解": spec}
        self._tools: Dict[str, dict] = {}
    
    def register(self, name: str, instance):
        """注册时自动解析类型注解和文档"""
        spec = self._parse_annotations(instance)
        self._tools[name] = {
            "instance": instance,   # 真正的工具实例
            "spec": spec,           # 解析出的「注解信息」
            "class": instance.__class__
        }
    
    def _parse_annotations(self, instance) -> ToolSpec:
        """自动从类的方法中提取类型注解"""
        # 1. 拿 execute_tool 方法的签名
        execute_method = getattr(instance, 'execute_tool', None)
        if not execute_method:
            return ToolSpec(name="unknown", description="", params={})
        
        # 2. 提取类型注解
        sig = inspect.signature(execute_method)
        type_hints = get_type_hints(execute_method)
        params = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            params[param_name] = {
                "type": str(type_hints.get(param_name, "any")),
                "required": param.default is inspect.Parameter.empty,
                "default": None if param.default is inspect.Parameter.empty else param.default
            }
        
        # 3. 提取文档和返回类型
        doc = inspect.getdoc(execute_method) or ""
        return_type = str(type_hints.get('return', 'any'))
        
        # 4. 尝试从 get_spec 拿描述（如果用户实现了）
        try:
            user_spec = instance.get_spec()
            name = getattr(user_spec, 'name', 'unknown')
            desc = getattr(user_spec, 'description', doc)
        except:
            name = instance.__class__.__name__
            desc = doc
        
        return ToolSpec(name=name, description=desc, params=params, returns=return_type)


    def execute(self, tool_name, tool_args):
        pass

    def get_tool(self, tool_name):
        entry = self._tools.get(tool_name)
        return entry.get("instance") if entry else None

    def get_all_tools(self):
        pass

    def get_all_spec(self):
        """拿出所有注解（给 LLM 用）"""
        return [t["spec"] for t in self._tools.values()]

registry = ToolRegistry()