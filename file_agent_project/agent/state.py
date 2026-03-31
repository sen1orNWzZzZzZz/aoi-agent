from core.schemas import AgentState
from core.schemas import ToolResult


def create_initial_state():
    empty_result = ToolResult(
        tool_name="",
        content="",
        success=False,
        error_message="",
    )
    return AgentState(
        current_intent="",
        current_file="",
        missing_info="",
        waiting_for_user=False,
        loop_count=0,
        retry_count=0,
        last_tool_name="",
        last_tool_result=empty_result,
        pending_files=[],
        completed_files=[],
        collected_contents={},
        workflow_type="idle",
        resume_context={},
        turn_id=0,
        session_id="",
        trace_events=[]
    )


def reset_state():
    return create_initial_state()
