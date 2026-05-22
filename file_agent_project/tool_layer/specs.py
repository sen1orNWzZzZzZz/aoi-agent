from dataclasses import dataclass, field

@dataclass
class FieldIssue:
    field_name: str
    target_path: str    #字段路径 比如tool_args.file_name
    reason: str     #填补原因
    required: bool  #是否必填

@dataclass
class ToolSpec:
    name: str
    required_fields: list[str]
    repair_slots: dict[str]
    default_user_messages: dict[str]