from tool_layer.base import BaseTool

from .registry import registry  # 导入全局注册中心
def register_tool(name: str):     
    """     自定义装饰器：把工具类自动注册进 registry     """
    def decorator(cls):         # 检查是不是 BaseTool 的子类 
        if not issubclass(cls, BaseTool):
            raise TypeError(f"{cls.__name__} 必须继承 BaseTool")
#实例化 + 注册         
        instance = cls()         
        registry.register(name, instance)
#返回原类，不改它         
        return cls
    return decorator

#这个嵌套的写法等价于HelloWorldTool = register_tool("hello_world_tool")(HelloWorldTool)