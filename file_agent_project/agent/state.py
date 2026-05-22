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
    
    return state

def create_initial_state():
    empty_result = ToolResult(
        tool_name="",
        content="",
        success=False,
        error_message="",
    )
    return AgentState(
        session_id="",
        turn_id=0,
        loop_count=0,
        error_count=0,
        waiting_for_user=False,
        missing_info="",
        resume_context=None,

        workflow_type="idle",
        current_file="",
        pending_files=[],
        completed_files=[],
        collected_contents=dict(),
        last_tool_result=ToolResult,
        trace_events=[]
    )


def reset_state():
    return create_initial_state()
