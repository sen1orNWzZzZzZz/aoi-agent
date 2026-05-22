from dataclasses import dataclass, field
from agent.trace import TraceEvent
from tool_layer.errors import ToolError

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
    # === 会话级（跨 turn 不变）===
    session_id: str
    turn_id: int

    # === 工作流级（根据 workflow_type 动态使用）===
    workflow_type: str        # idle / single_file_read / single_file_summary / multi_file_summary
    current_file: str         # 单文件场景使用

    # === 工具级（最近一次的执行记录）===
    last_tool_result: ToolResult  # 保留这个，删掉 last_tool_name

    # === 轮次级（每轮重置或递增）===
    loop_count: int           # while 循环计数
    error_count: int          # 新增：本轮累计错误数，用于熔断
    waiting_for_user: bool
    missing_info: str
    resume_context: ResumeContext | None

    # === 工作流级（根据 workflow_type 动态使用）===
    pending_files: list[str] = field(default_factory=list)      # 多文件场景使用
    completed_files: list[str] = field(default_factory=list)    # 多文件场景使用
    collected_contents: dict[str, str] = field(default_factory=dict)  # 多文件场景使用

    

    # === 追踪级 ===
    trace_events: list[TraceEvent] = field(default_factory=list)


@dataclass
class Action:
    action_type: str   #下一步动作
    tool_name: str
    message: str
    finish_reason: str
    task_type: str = ""   #工作类型
    resume: ResumeDecision | None = None
    tool_args: dict  = field(default_factory=dict)

