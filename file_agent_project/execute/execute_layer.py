from venv import logger

from core.schemas import ToolResult
from tools.registry import TOOL_SPECS,TOOL_HANDLER

def call_execute(tool_name:str, tool_args:dict)->ToolResult:
    logger.info(f"[EXEC] tool={tool_name}, args={tool_args}")
    if TOOL_HANDLER[tool_name] is not None:#工具存在性判断
        tool = TOOL_HANDLER[tool_name]
        #工具参数合法性判断
        fields = TOOL_SPECS[tool_name].required_fields
        for field in fields:
            if tool_args[field] is not None:
                continue
            else:
                #Todo:参数缺失错误处理
                pass
        ret = tool(**tool_args)
        logger.info(f"[EXEC-RESULT] success={ret.success}, content_len={len(ret.content)}")
        return ret
    else:
        #Todo：工具不存在错误处理
        pass