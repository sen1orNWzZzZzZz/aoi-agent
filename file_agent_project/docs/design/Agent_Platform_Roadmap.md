# Local AI Workflow Agent Platform Roadmap

## 项目定位

这个项目未来不再只是一个“文件总结 Agent”，而是要逐步演进成一个可扩展的本地 AI Workflow Agent Platform。

核心目标有三层：

1. 学习目标
- 理解 AI Agent 的最小工程闭环
- 理解 workflow、human-in-the-loop、trace、失败分流等底层机制
- 理解模型和程序的边界

2. 作品目标
- 形成可用于面试展示的工程作品集
- 证明自己不仅会调模型 API，还能做 Agent 工程系统

3. 职业目标
- 从 Java 后端开发转向 AI 应用 / Agent 工程方向
- 逐步补齐 Agent、RAG、MCP、工具执行等主流能力


## 总体架构

未来建议将项目收成一个 `Local AI Workflow Agent Platform`，按模块拆分为以下几层：

### 1. app / interface
- CLI 交互入口
- 后续可扩展 FastAPI / Web 界面
- 只负责接收用户输入、展示输出、触发 `run_turn`

### 2. orchestrator
- Agent 主控层
- 负责 `run_turn`
- 负责 workflow 状态推进
- 负责 ask_user / resume / failure routing

### 3. memory & state
- `history`
  - 给模型看的语义上下文
- `state`
  - 给程序做流程控制的结构化状态
- 核心字段包括：
  - `workflow_type`
  - `pending_files`
  - `completed_files`
  - `collected_contents`
  - `resume_context`
  - `current_file_retry_count`

### 4. model adapter
- 封装 `get_model_action`
- 管理 prompt 和 action 解析
- 让 orchestrator 不直接依赖某个具体模型实现

### 5. tool registry
- 统一管理工具调用
- 当前文件工具：
  - `read_file`
  - `list_files`
- 未来扩展：
  - `write_code`
  - `run_code`
  - `retrieve_docs`
  - `mcp_call`

### 6. observability
- `TraceEvent`
- trace buffer
- trace log file
- 后续可扩展：
  - eval
  - metrics
  - failure report

### 7. extensions
- `rag`
- `code_runner`
- `mcp_adapter`
- 作为扩展能力接入 `tool registry`


## 简化架构图

```text
User / CLI / API
        |
        v
   app/interface
        |
        v
   orchestrator
   |     |      |
   |     |      |
   v     v      v
state  model   tool registry
history adapter   |   |   |
                  |   |   |
               file  rag code/mcp
                  |
                  v
            ToolResult / Trace
```


## 当前版本定位

当前项目已经逐步从 File Agent 演进为最小 Workflow Agent Core。

目前核心能力包括：
- 单文件读取
- 单文件总结
- 多文件总结
- ask_user 后恢复原 workflow
- trace 记录执行过程
- 多文件失败分流的第一版实现

当前项目的核心价值不是“功能多”，而是：
- 模型负责语义识别
- 程序负责流程控制
- workflow 由 orchestrator 和 state 推进


## 版本路线

### v2.2
目标：收稳当前 File Agent Core

重点：
- workflow 主干跑通
- ask_user / resume 成立
- 多文件失败分流成立
- trace 基础可用

产出：
- 能演示的 CLI
- README / Version Notes
- 测试样例


### v2.3
目标：收边界和一致性

重点：
- 单文件 / 多文件失败策略统一
- trace 记录真实 action
- 明确多文件缺失文件时的正式策略
  - 部分成功返回
  - 或缺失即暂停 ask_user
- 文档和测试完善





### v3.0
目标：加 RAG Tool

重点：
- 文档 ingestion
- chunking
- embedding / retrieval
- citation
- 将检索结果作为工具接入 Agent

意义：
- Agent 开始具备知识增强能力


### v3.1
目标：加 MCP Adapter

重点：
- 接入现成 MCP server
- 实现最小自定义 MCP server
- 通过 `mcp_call` 接回 Agent

意义：
- Agent 开始具备标准化扩展能力

### v3.2
目标：加 Code Execution Tool

重点：
- 生成小段代码
- 写入临时文件
- 执行代码
- 收集 stdout / stderr
- 把执行结果返回给模型继续决策

意义：
- Agent 从“文件处理”升级成“可执行任务 Agent”

## 8 周开发路线时间表

### 第 1 周
- 收稳 `v2.2`
- 修 workflow / failure / trace 关键问题
- 确保核心路径稳定

### 第 2 周
- 收 `v2.3`
- 补 README、Version Notes、测试记录
- 做一套面试演示脚本

### 第 3 周
- 设计 `code_runner` 模块
- 定义 `write_code / run_code` 工具接口
- 支持最小 Python 脚本执行

### 第 4 周
- 把 Code Execution Tool 接入 orchestrator
- 跑通“生成代码 -> 执行 -> 返回结果”

### 第 5 周
- 开始 RAG 能力建设
- 实现文档 ingestion、chunking、embedding

### 第 6 周
- 实现 retrieval + citation
- 把 RAG 作为工具接入 Agent

### 第 7 周
- 学习 MCP 的使用方式
- 接入一个现成 MCP server
- 设计 `mcp_call` 适配层

### 第 8 周
- 实现一个最小自定义 MCP server
- 接回 Agent
- 整理成最终作品叙事


## 项目之间的叙事主线

未来应该把项目能力串成一条清晰路线：

### Agent Core
解决“怎么控制流程”
- workflow
- state
- tool calling
- human-in-the-loop
- trace

### RAG
解决“怎么接知识”
- retrieval
- citation
- grounding
- evaluation

### MCP
解决“怎么接工具和上下文”
- protocol
- integration
- interoperability

### Code Execution
解决“怎么执行任务并验证结果”
- 代码生成
- 工具执行
- 输出反馈
- 二次决策

一句话总结：

这个项目未来要解决的是 AI 应用系统的三个核心问题：
- 控制
- 知识
- 连接

并进一步补上：
- 执行


## 当前最优先事项

现在不要立刻把所有能力一起接进去。

当前最合理的顺序是：

1. 先收 File Agent Core
2. 再加 Code Execution Tool
3. 再加 RAG Tool
4. 最后加 MCP

也就是说，当前最优先的不是继续无限扩功能，而是把当前项目先收成一个稳定的 `Agent Core`。


## 面试价值

未来这个项目可以作为“Java 后端转 AI 应用 / Agent 工程”的核心作品。

可展示的点包括：
- 最小 Agent 闭环
- 最小 Workflow Agent
- history / state 分层
- task_type / workflow_type 分工
- ask_user / resume
- trace / observability
- 失败分流与状态清理
- 工具执行与扩展设计
