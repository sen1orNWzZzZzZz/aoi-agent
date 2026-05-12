from enum import Enum
from dataclasses import dataclass, field
from tools.errors import ToolError,ToolErrorCode, PlatErrorCategory
from tools.specs import FieldIssue


class RecoveryAction(Enum):
    ASK_USER = "ask_user"
    RETRY = "retry"
    ABORT = "abort"
    SKIP_STEP = "skip_step" #切换任务状态

@dataclass
class RecoveryDecision:
    action: RecoveryAction  #下一步动作
    reason: str   #动作原因 ++trace
    missing_fields: list | None = None
    user_message: str | None = None #给user的提示
    missing_info: str | None = None
    repair_target: str | None = None
    max_retries: int = 3
    resume_patch: dict[str, object] = field(default_factory=dict)  #用来修补现场某个字段
#     #{
#     "patch_type": "action_patch",
#     "fields": {
#       "file_name": "tool_args.file_name",
#       "start_date": "tool_args.start_date"
#     }
#   }


def create_recovery_decision(tool_error:ToolError) ->RecoveryDecision:
    if tool_error.category==PlatErrorCategory.USER_FIXABLE:
        resume_patch_builder = {}
        
        if len(tool_error.field_issues)!=0:
            #类型为用户可修复并且有需要修复的字段
            resume_patch_builder["fields"] = {}
            resume_patch_builder["patch_type"] = "action_patch"
            resume_patch_builder["missing_fields"] = []
            for field_issue in tool_error.field_issues:
                resume_patch_builder["fields"][field_issue.field_name] = field_issue.target_path
                resume_patch_builder["missing_fields"].append(field_issue.field_name)
            return RecoveryDecision(action=RecoveryAction.ASK_USER, reason="user_fixable",
                                    user_message=tool_error.message, resume_patch=resume_patch_builder,missing_info=resume_patch_builder["missing_fields"][0])
        elif tool_error.repair_target is not None:
            resume_patch_builder["patch_type"] = "workflow_repair"
            resume_patch_builder["payload"] = {}
            resume_patch_builder["payload"]["repair_target"] = tool_error.repair_target
            return RecoveryDecision(action=RecoveryAction.ASK_USER, reason="user_fixable", 
                            user_message=tool_error.message, missing_info=tool_error.missing_info,
                            repair_target=tool_error.repair_target, resume_patch=resume_patch_builder)
    elif tool_error.category==PlatErrorCategory.RETRYABLE:
        return RecoveryDecision(action=RecoveryAction.RETRY, reason="retryable")
    elif tool_error.category in [PlatErrorCategory.FATAL, PlatErrorCategory.SECURITY, PlatErrorCategory.PROTOCOL]:
        return RecoveryDecision(action=RecoveryAction.ABORT, reason="fatal_error")
    else:
        raise ValueError(
            f"Unhandled PlatErrorCategory: {tool_error.category} "
            f"(error: {tool_error.message})"
        )