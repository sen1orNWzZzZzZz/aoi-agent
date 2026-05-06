from core.schemas import AgentState
from core.schemas import ToolResult, ResumeContext

def set_default_state_workflow(state:AgentState):
    state.pending_files=[]
    state.current_file_retry_count=0
    state.workflow_type="idle"
    state.current_file=""
    state.collected_contents={}
    state.waiting_for_user = False
    state.missing_info = ""
    state.resume_context = None
    state.completed_files = []
    state.retry_count = 0
    return state

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
        resume_context=None,
        turn_id=0,
        session_id="",
        trace_events=[],
        current_file_retry_count=0
    )


def reset_state():
    return create_initial_state()
