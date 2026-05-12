# WorkflowAgentV2 流程图

## 主流程说明
下面这张图描述了 `workFlowAgentV2` 的主执行流程，重点体现：
- 模型负责输出 `Action` 和 `task_type`
- orchestrator 负责维护 `workflow_type` 和状态推进
- 多文件任务由程序顺序消费队列
- 总结类任务会在读取完成后进入最终总结阶段

## Mermaid
```mermaid
flowchart TD
    A[用户输入] --> B[调用模型生成 Action]
    B --> C{action_type}

    C -->|ask_user| D[向用户追问]
    D --> A

    C -->|respond/finish| E[返回结果给用户]

    C -->|call_tool| F{tool_name}

    F -->|list_files| G[执行 list_files]
    G --> H[生成 ToolResult]
    H --> I[写入 history]
    I --> B

    F -->|read_file 单文件| J[执行 read_file]
    J --> K[生成 ToolResult]
    K --> L[写入 history 和 state]
    L --> M{workflow_type}

    M -->|single_file_read| E
    M -->|single_file_summary| N[进入总结阶段]
    N --> B

    F -->|read_file 多文件| O[初始化 pending_files]
    O --> P[orchestrator 顺序消费队列]
    P --> Q[读取 current_file]
    Q --> R[更新 completed_files 和 collected_contents]
    R --> S{pending_files 是否为空}

    S -->|否| P
    S -->|是| T[进入最终总结阶段]
    T --> B
```

## 阶段理解
- `single_file_read`：读取完成即可直接返回结果。
- `single_file_summary`：读取完成后还需要进入总结阶段。
- `multi_file_summary`：所有文件读取完成后，基于 `collected_contents` 进入最终总结阶段。
