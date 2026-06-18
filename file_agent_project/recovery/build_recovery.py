#保存现场
from core.schemas import AgentState, ResumeContext


def save_recovery_info(state:AgentState, missing_field: str, pending_action: dict):
#修改当前状态
      state.waiting_for_user = True

      #记录缺失字段
      state.missing_info = missing_field

      # 存档：原来的 action 是什么
      state.resume_context = ResumeContext(
          resume_kind="action_patch",
          missing_info=missing_field,
          pending_action=pending_action,
          workflow_type=state.workflow_type
      )