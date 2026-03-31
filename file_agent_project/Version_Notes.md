# Version Notes

## v2
`v2` 的重点是把最小文件 Agent 升级成最小 Workflow Agent。

核心变化：
- 引入 `task_type` 和 `workflow_type`
- 支持 `single_file_read`
- 支持 `single_file_summary`
- 支持 `multi_file_summary`
- 引入 `pending_files / completed_files / collected_contents`
- 将多文件读取从模型记忆转为程序控制的队列推进

这个阶段的重点是：
- 模型负责识别任务
- orchestrator 负责控制流程
- 系统开始具备多步任务执行能力

## v2.1
`v2.1` 在 `v2` 的基础上，补充了最小 human-in-the-loop 恢复能力。

核心变化：
- 在 `AgentState` 中新增 `resume_context`
- 当模型返回 `ask_user` 时，系统保存恢复上下文
- 用户补充输入后，系统会优先尝试恢复原 workflow
- 用户补充不再完全被视作一个全新任务

这个阶段的重点是：
- 让 workflow 不只是能暂停
- 还要能在最小程度上恢复

## 当前状态
当前项目已经具备：
- 最小 Agent 闭环
- 最小 Workflow Agent
- 最小 human-in-the-loop 恢复能力

当前项目仍待加强：
- `ask_user` 后的恢复策略还不够完整
- 错误分类和恢复策略仍然较简化
- 缺少测试和可观测性
- 尚未服务化
