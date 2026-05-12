# Current Data Structure Examples

This file is a memory note for the current protocol-layer and recovery-layer data structures.

It does not mean the design is final. It only records the current agreed examples so they are easy to revisit.

## 1. ToolSpec

Meaning:
- Describes one tool's input contract and repair slots.

Example:

```python
ToolSpec(
    name="read_file",
    required_fields=["file_name"],
    repair_slots={
        "file_name": "tool_args.file_name"
    },
    default_user_messages={
        "file_name": "请提供正确的文件路径名"
    }
)
```

## 2. FieldIssue

Meaning:
- Describes one field-level problem.

Example:

```python
FieldIssue(
    field_name="file_name",
    target_path="tool_args.file_name",
    reason="missing",
    required=True
)
```

## 3. ToolError

Meaning:
- Describes a structured tool failure.

Example:

```python
ToolError(
    code=ToolErrorCode.TOOL_ARGUMENT_MISSING,
    category=PlatErrorCategory.USER_FIXABLE,
    message="请提供正确的文件路径名",
    field_issues=[
        FieldIssue(
            field_name="file_name",
            target_path="tool_args.file_name",
            reason="missing",
            required=True
        )
    ],
    missing_info="file_name",
    repair_target=None,
    retryable=False,
    raw_error=None
)
```

## 4. ToolResult

Meaning:
- Standard tool execution result.

Success example:

```python
ToolResult(
    tool_name="read_file",
    content="file content here",
    success=True,
    error_message="",
    error=None
)
```

Failure example:

```python
ToolResult(
    tool_name="read_file",
    content="",
    success=False,
    error_message="缺少文件路径，需要用户补充明确的 file_name。",
    error=ToolError(
        code=ToolErrorCode.TOOL_ARGUMENT_MISSING,
        category=PlatErrorCategory.USER_FIXABLE,
        message="请提供正确的文件路径名",
        field_issues=[
            FieldIssue(
                field_name="file_name",
                target_path="tool_args.file_name",
                reason="missing",
                required=True
            )
        ]
    )
)
```

## 5. Action

Meaning:
- Model decision output for current step.

Example:

```python
Action(
    action_type="call_tool",
    tool_name="read_file",
    message="",
    finish_reason="",
    task_type="single_file_read",
    resume=None,
    tool_args={
        "file_name": ""
    }
)
```

## 6. RecoveryDecision

Meaning:
- Recovery layer decision after a structured tool error.

Action patch example:

```python
RecoveryDecision(
    action=RecoveryAction.ASK_USER,
    reason="user_fixable",
    missing_fields=["file_name"],
    user_message="请提供正确的文件路径名",
    missing_info="file_name",
    repair_target=None,
    max_retries=3,
    resume_patch={
        "patch_type": "action_patch",
        "fields": {
            "file_name": "tool_args.file_name"
        },
        "missing_fields": ["file_name"]
    }
)
```

Workflow repair example:

```python
RecoveryDecision(
    action=RecoveryAction.ASK_USER,
    reason="user_fixable",
    missing_fields=None,
    user_message="文件不存在，请补充正确路径",
    missing_info=None,
    repair_target="a.py",
    max_retries=3,
    resume_patch={
        "patch_type": "workflow_repair",
        "payload": {
            "repair_target": "a.py"
        }
    }
)
```

## 7. ResumeContext

Meaning:
- Saved recovery scene while waiting for user input.

Example:

```python
ResumeContext(
    workflow_type="single_file_read",
    missing_info="file_name",
    resume_kind="action_patch",
    repair_target=None,
    pending_action={
        "tool_name": "read_file",
        "tool_args": {
            "file_name": ""
        }
    },
    resume_patch={
        "patch_type": "action_patch",
        "fields": {
            "file_name": "tool_args.file_name"
        },
        "missing_fields": ["file_name"]
    }
)
```

## 8. AgentState

Meaning:
- Runtime state of the orchestrator.

Example:

```python
AgentState(
    current_intent="read file",
    current_file="",
    missing_info="file_name",
    waiting_for_user=True,
    loop_count=1,
    retry_count=0,
    last_tool_name="read_file",
    last_tool_result=ToolResult(
        tool_name="read_file",
        content="",
        success=False,
        error_message="缺少文件路径，需要用户补充明确的 file_name。",
        error=ToolError(
            code=ToolErrorCode.TOOL_ARGUMENT_MISSING,
            category=PlatErrorCategory.USER_FIXABLE,
            message="请提供正确的文件路径名",
            field_issues=[
                FieldIssue(
                    field_name="file_name",
                    target_path="tool_args.file_name",
                    reason="missing",
                    required=True
                )
            ]
        )
    ),
    workflow_type="single_file_read",
    session_id="demo-session",
    turn_id=1,
    current_file_retry_count=0,
    resume_context=ResumeContext(
        workflow_type="single_file_read",
        missing_info="file_name",
        resume_kind="action_patch",
        repair_target=None,
        pending_action={
            "tool_name": "read_file",
            "tool_args": {
                "file_name": ""
            }
        },
        resume_patch={
            "patch_type": "action_patch",
            "fields": {
                "file_name": "tool_args.file_name"
            },
            "missing_fields": ["file_name"]
        }
    ),
    pending_files=[],
    completed_files=[],
    collected_contents={},
    trace_events=[]
)
```

## 9. resolved_fields

Meaning:
- Structured field values returned by the future resume resolver.

Single-field example:

```python
{
    "file_name": "README.md"
}
```

Multi-field example:

```python
{
    "start_date": "2026-04-01",
    "end_date": "2026-04-10"
}
```

## 10. patched_action

Meaning:
- The original pending action after applying resolved fields.

Example:

```python
{
    "tool_name": "read_file",
    "tool_args": {
        "file_name": "README.md"
    }
}
```

## 11. One Complete Recovery Flow Example

1. Model returns action:

```python
{
    "tool_name": "read_file",
    "tool_args": {
        "file_name": ""
    }
}
```

2. Tool validation/execution returns:

```python
ToolError(
    code=ToolErrorCode.TOOL_ARGUMENT_MISSING,
    category=PlatErrorCategory.USER_FIXABLE,
    message="请提供正确的文件路径名",
    field_issues=[
        FieldIssue(
            field_name="file_name",
            target_path="tool_args.file_name",
            reason="missing",
            required=True
        )
    ]
)
```

3. Recovery creates:

```python
RecoveryDecision(
    action=RecoveryAction.ASK_USER,
    reason="user_fixable",
    missing_fields=["file_name"],
    missing_info="file_name",
    user_message="请提供正确的文件路径名",
    resume_patch={
        "patch_type": "action_patch",
        "fields": {
            "file_name": "tool_args.file_name"
        },
        "missing_fields": ["file_name"]
    }
)
```

4. System saves:

```python
ResumeContext(
    workflow_type="single_file_read",
    missing_info="file_name",
    resume_kind="action_patch",
    pending_action={
        "tool_name": "read_file",
        "tool_args": {
            "file_name": ""
        }
    },
    resume_patch={
        "patch_type": "action_patch",
        "fields": {
            "file_name": "tool_args.file_name"
        },
        "missing_fields": ["file_name"]
    }
)
```

5. User补充后，resume resolver returns:

```python
{
    "file_name": "README.md"
}
```

6. Tool apply patch:

```python
{
    "tool_name": "read_file",
    "tool_args": {
        "file_name": "README.md"
    }
}
```

This final dict is the `patched_action`.
