from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional

from tool_layer.base import ToolResult

###############枚举类
class FileConsume(Enum):
    RETRY = "retry"
    ASK_USER = "ask_user"
    UNKOWN = "unknow"
    FALL_BACK = "fall_back"

@dataclass
class ConsumptionDecision:
    """消费后的决策，告诉 orchestrator 下一步做什么"""
    action: Literal["continue", "ask_user", "retry", "give_up", "summarize"]
    observation: str           #消化后的结果，要加入 history 的文本
    state_patch: dict          #要更新到 state 的字段
    recovery_hint: Optional[str] = None  #给用户看的提示（如果是 ask_user）
    
#这里打算用三层。先解析原始结果，然后做context压缩。最后进行失败分类
def _first_layer(tool_result:ToolResult):
    if tool_result.tool_name=="read_file":
        return {
            "file_name":tool_result.tool_args
        }