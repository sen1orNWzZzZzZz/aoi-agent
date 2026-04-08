from enum import Enum
from dataclasses import dataclass, field
from file_agent_project.tools.errors import ToolError,ToolErrorCode, PlatErrorCategory

class RecoveryAction(Enum):
    ASK_USER = "ask_user"
    RETRY = "retry"
    ABORT = "abort"
    SKIP_STEP = "skip_step" #切换任务状态

@dataclass
class RecoveryDecision:
    action: RecoveryAction  #下一步动作
    reason: str   #动作原因 ++trace
    user_message: str | None = None #给user的提示
    missing_info: str | None = None
    repair_target: str | None = None
    max_retries: int = 3
    resume_patch: dict[str, object] = field(default_factory=dict)  #用来修补现场某个字段

def create_recovery_decision(tool_error:ToolError) ->RecoveryDecision:
    if tool_error.category==PlatErrorCategory.USER_FIXABLE:
        if tool_error.repair_target is not None:
            resume_patch_builder = {}
            resume_patch_builder["repair_target"] = tool_error.repair_target
            return RecoveryDecision(action=RecoveryAction.ASK_USER, reason="用户可修复，需要询问用户", 
                                user_message=tool_error.message, missing_info=tool_error.missing_info,
                                repair_target=tool_error.repair_target, resume_patch=resume_patch_builder)
    if tool_error.category==PlatErrorCategory.RETRYABLE:
        return RecoveryDecision(action=RecoveryAction.RETRY, reason="retryable")
    if tool_error.category in [PlatErrorCategory.FATAL, PlatErrorCategory.SECURITY, PlatErrorCategory.PROTOCOL]:
        return RecoveryDecision(action=RecoveryAction.ABORT, reason="touch the security limit")