from dataclasses import dataclass, field
from typing import Literal

from core.schemas import AgentState
from agent.model import get_model_action
from recovery.build_recovery import resume_from_context

@dataclass
class Decision:
    next_action: Literal["respond", "call_tool", "ask_user", "finish", "resume"]
    tool_name: str | None = None
    tool_args: dict = field(default_factory=dict)
    assistant_message: str | None = None   # orchestrator需要记录到history的消息
    task_type: str | None = None
    record_message: bool = False#是否需要记录信息

def decide_next_step(
    state: AgentState,
    user_input: str,
    history: list[dict]
) -> Decision:
    if state.waiting_for_user is True:
        
        pass#执行恢复操作
    action = get_model_action(user_input=user_input, state=state,history=history)
    ret = Decision(next_action=action.action_type)
    if action.tool_name is not None:
        ret.tool_name = action.tool_name
    if action.tool_args is not None:
        ret.tool_args = action.tool_args
    if action.action_type != "call_tool":
        ret.record_message = True
        ret.assistant_message = action.message
    return ret