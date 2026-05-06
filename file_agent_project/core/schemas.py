from dataclasses import dataclass, field
from agent.trace import TraceEvent
from tools.errors import ToolError

@dataclass
class ToolResult:
    tool_name: str
    content: str
    success: bool
    error_message: str
    error: ToolError | None = None

@dataclass
class ResumeDecision:#恢复判定字段
    resume_type: str
    resolved_value: str
    tool_name: str
    message: str
    tool_args: dict  = field(default_factory=dict)


@dataclass
class ResumeContext:#保存现场用字段
    workflow_type: str
    missing_info:str
    resume_kind:str #分为action patch 和 workflow_repair
    repair_target: str | None = None
    pending_action:  dict = field(default_factory=dict)
    resume_patch: dict | None = None #现场恢复字段



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
    resume_context: ResumeContext | None = None #agent的上下文保存器
    pending_files: list[str] = field(default_factory=list)  #给多文件队列用的
    completed_files: list[str] = field(default_factory=list)
    collected_contents: dict[str, str] = field(default_factory=dict)
    trace_events: list[TraceEvent] = field(default_factory=list)#是agent的输出trace相关字段


@dataclass
class Action:
    action_type: str
    tool_name: str
    message: str
    finish_reason: str
    task_type: str = ""
    resume: ResumeDecision | None = None
    tool_args: dict  = field(default_factory=dict)

