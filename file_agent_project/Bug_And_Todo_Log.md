# Bug And Todo Log

## 目的
这份文档用于记录 `file_agent_project` 当前阶段已经定位到的 bug、原因判断和后续待办，方便下次继续推进时快速恢复上下文。

## 当前项目阶段
- 当前主版本：`v2`
- 当前补强版本：`v2.1`
- 正在推进：`v2.2`

当前系统已经具备：
- 最小 Agent 闭环
- 最小 Workflow Agent
- 最小 `ask_user -> resume` 恢复能力
- 第一版 trace 结构和日志落盘能力

## 已定位的核心 Bug

### Bug 1：多文件任务可能退化成模型逐步主导，而不是 orchestrator 队列控制
现象：
- 用户明确给出多个文件时，模型没有一次性输出 `file_names`
- 模型先 `call_tool`，再 `call_tool`，最后直接 `respond`
- orchestrator 没有拿到足够强的证据证明自己在控制多文件队列

影响：
- 多文件 workflow 退化成“模型自己一步步读文件”的伪 workflow
- 程序控制权不够强
- trace 无法清晰证明多文件任务是由 orchestrator 推进的

原因判断：
- prompt / action 契约还不够硬
- orchestrator 对多文件中间态 `respond` 缺少防线

后续待办：
- 强化 prompt：当用户明确给出多个文件且目标是总结多个文件时，模型优先输出 `tool_args.file_names`
- orchestrator 增加保护：未完成的 `multi_file_summary` 中，不应允许中间 `respond` 直接作为最终回复返回

### Bug 2：多文件队列头失败后，系统会重复消费同一个文件直到超过最大重试次数
现象：
- trace 中同一个文件被反复记录为 `queue_consume`
- 比如 `agent_design_review` 一直停留在队列头
- 系统最后返回“超过最大重试次数，自动退出”

影响：
- workflow 卡死在队列头
- 系统进入无意义重试
- 用户体验差

原因判断：
- 当前设计是“失败不出队”
- 但 orchestrator 失败后没有做有效分流，而是继续 while 自动重试
- 导致同一个坏输入被反复消费

后续待办：
- 优先做最小止血版：多文件读取失败后，不再继续 silent retry 到死
- 后续升级为错误分类：
  - 可重试错误
  - 不可重试错误
  - 需要用户修正的错误

建议下一步实现顺序：
1. 最小止血：多文件失败先直接返回错误或进入 `ask_user`
2. 再做进阶版错误分类

### Bug 3：等待补充期间，系统仍然缺少“新任务打断旧任务”的清晰策略
现象：
- 用户在 `ask_user` 等待态输入新任务时
- 系统容易继续把输入当作旧任务补充
- 比如用户说“不总结了，先列出根目录文件”，系统仍然按总结任务理解

影响：
- human-in-the-loop 恢复能力不够完整
- 用户切换任务时体验不稳定

原因判断：
- 当前 `v2.1` 只实现了最小恢复
- 还没有设计“补充旧任务 / 切换新任务 / 取消旧任务”的分流逻辑

后续待办：
- 在 `v2.2` 中设计等待态输入分类：
  - supplement
  - switch_task
  - unclear

### Bug 4：模型仍可能猜文件名
现象：
- 用户说“帮我总结几个配置文件”
- 系统曾直接猜成 `config.yaml`

影响：
- 违反“不允许猜文件名”的约束
- 模型主导过强

原因判断：
- prompt 对“不明确时必须 ask_user”的约束还不够硬

后续待办：
- 强化 prompt 规则
- 后续配合 trace 观察类似猜测行为是否减少

## 当前 trace 相关状态

### 已完成
- 新增 `TraceEvent`
- 新增 `trace_events`
- 在 `app.py` 中为每次 session 生成 `session_id`
- 每轮 `run_turn()` 会递增 `turn_id`
- trace 会落盘到独立日志文件

### 当前 trace 已能观察到
- `turn_start`
- 模型返回的动作类型
- orchestrator 队列消费事件

### 当前 trace 仍需加强
- 事件命名统一性还可以继续优化：
  - `turn_start` -> `turn_started`
  - `queue_consume` -> `queue_consumed`
- 还缺少更强的关键证据事件：
  - `action_received`
  - `queue_initialized`
  - `tool_result`
  - `summary_phase_entered`

## 当前最推荐的下一步顺序
1. 先修复多文件失败后无限重试的问题
2. 再强化多文件任务的 prompt / action 契约
3. 再设计等待态下的任务切换策略
4. 再升级 trace 事件，让它更能证明 orchestrator 控队列

## 老师对当前项目状态的判断
这个项目已经不是简单 demo 了，已经开始进入真正的 Agent 工程问题区：
- workflow 控制权
- 恢复能力
- 队列推进
- 失败分流
- trace 证据链

当前最需要补的，不是再加新能力，而是把这些关键流程边界收紧。
