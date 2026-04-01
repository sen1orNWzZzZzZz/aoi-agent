from dataclasses import dataclass, field
from agent.trace import TraceEvent


@dataclass
class ToolResult:
    tool_name: str
    content: str
    success: bool
    error_message: str


@dataclass
class AgentState:
    current_intent: str
    current_file: str
    missing_info: str
    waiting_for_user: bool
    loop_count: int
    retry_count: int
    last_tool_name: str
    last_tool_result: ToolResult
    workflow_type: str
    session_id: str#日志
    turn_id: int#rizhi
    current_file_retry_count: int #最近文件的重试次数
    pending_files: list[str] = field(default_factory=list)  #给多文件队列用的
    completed_files: list[str] = field(default_factory=list)
    collected_contents: dict[str, str] = field(default_factory=dict)
    resume_context: dict[str, str] = field(default_factory=dict)  #agent的上下文保存器
    trace_events: list[TraceEvent] = field(default_factory=list)#是agent的输出trace相关字段


@dataclass
class Action:
    action_type: str
    tool_name: str
    tool_args: dict
    message: str
    finish_reason: str
    task_type: str
