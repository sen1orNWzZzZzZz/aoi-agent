# File Agent 面试准备

适用场景：
- AI 应用工程 / Agent 工程方向面试
- 介绍当前 `file_agent_project`
- 回答 Agent 基础概念题
- 从当前项目延伸到 Workflow Agent

---

## 1. 项目一句话介绍

我实现了一个本地文件 Agent，围绕 `orchestrator` 组织多轮闭环：模型先输出结构化 `Action`，系统按 `Action` 调用 `list_files`、`read_file` 等工具，再将 `ToolResult` 作为 observation 回灌模型，结合 `state` 和 `memory` 完成 `respond`、`ask_user`、`finish` 等流程推进。

---

## 2. 项目背景与目标

### 2.1 这个项目在做什么

这是一个最小本地文件 Agent，主要能力包括：
- 列出目录文件
- 读取指定文件
- 总结文件内容
- 文件名缺失时 ask_user 补问
- 管理 state / history
- 工具调用后再次决策，形成最小 Agent 闭环

### 2.2 我为什么做这个项目

这个项目的目标不是做一个“万能智能体”，而是用一个受控场景把 Agent 最重要的工程骨架跑通：
- Prompt
- Tool Calling
- State
- Memory
- Orchestrator
- ToolResult
- 闭环控制

---

## 3. 项目结构介绍

核心模块：
- `app.py`：程序入口，负责输入输出
- `agent/orchestrator.py`：流程调度中心
- `agent/model.py`：模型适配层，负责把上下文转成 Action
- `agent/memory.py`：上下文记录
- `agent/state.py`：当前任务状态
- `agent/prompt.py`：系统提示词协议
- `tools/list_files.py`：列目录工具
- `tools/read_file.py`：读文件工具
- `core/schemas.py`：Action / ToolResult / AgentState 数据结构
- `core/constants.py`：配置和常量

---

## 4. 运行链路表达

### 4.1 最小链路

用户输入 -> app.py -> orchestrator.py -> model.py -> Action -> tool -> ToolResult -> 再回 model.py -> 最终回复

### 4.2 我怎么解释这是一个 Agent，而不是脚本

因为它不是按固定脚本顺序调用工具，而是围绕：

`模型决策 -> 工具执行 -> ToolResult 回灌 -> 再次决策`

形成了最小闭环。

系统里有：
- `orchestrator` 负责流程推进
- `state` 负责结构化状态控制
- `memory` 负责上下文记录
- `loop_count / retry_count` 负责失控保护
- 工作区路径控制负责访问边界

所以它已经不是单次工具脚本，而是一个具备最小自治能力和流程控制能力的专用 Agent。

---

## 5. 核心设计点

### 5.1 为什么需要 Orchestrator

`orchestrator` 负责流程推进，不负责具体工具实现，也不负责模型接口细节。

它主要做这些事情：
- 记录用户输入
- 更新当前 intent
- 调模型获取 Action
- 分发工具调用
- 回写 ToolResult
- 控制 ask_user / respond / finish
- 控制 loop 和 retry

一句话：

`orchestrator 是 Agent 的流程控制层。`

### 5.2 为什么 ToolResult.success 不等于任务完成

因为 `ToolResult.success=True` 只表示这次工具执行成功，说明 observation 拿到了。

但用户任务是否完成，要看模型基于 observation 后是否已经能形成最终回答。

例如：
- 读文件成功，不等于总结任务完成
- 读完一个文件成功，不等于多文件任务完成

所以：

`Tool success != Task finished`

### 5.3 为什么要有 ask_user

因为 Agent 不应该乱猜参数。

当文件名或目录路径不明确时，正确做法不是凭空猜，而是：
- 标记当前流程需要补信息
- 进入 `waiting_for_user`
- 设置 `missing_info`
- 等用户补充后再继续

这说明系统不仅会“回答”，还会“暂停并恢复流程”。

### 5.4 为什么 history 和 state 不能混为一谈

`history` 主要是语义上下文，给模型参考。

`state` 是流程控制上下文，给系统做确定性判断。

例如这些信息更适合放在 state：
- `waiting_for_user`
- `missing_info`
- `retry_count`
- `loop_count`
- `last_tool_result`

一句话：

`history 给模型看，state 给程序控。`

### 5.5 为什么升级 memory 结构

最开始 memory 只是：

```python
{"role": "...", "content": "..."}
```

后来升级成：
- `message`
- `tool_result`

原因不是为了复杂，而是因为 Agent 历史里不只有对话消息，还有工具 observation。

如果把工具结果也伪装成普通 assistant message，会混淆：
- 助手发言
- 外部工具结果

所以内部 memory 需要更结构化，发给模型之前再做适配。

### 5.6 为什么要有 to_model_messages

因为：

`内部 memory 结构 != 外部模型接口格式`

内部 memory 是为了系统设计服务的，目的是让数据更清晰、更可控。

而聊天模型接口通常只接受：

```python
{"role": "...", "content": "..."}
```

所以需要 `to_model_messages()` 做适配层，把内部 record 转成模型可消费的格式。

### 5.7 为什么不能只靠模型自己记流程

如果完全依赖模型自己记当前做到哪一步，会有这些风险：
- 重复执行
- 漏掉步骤
- 顺序混乱
- 失败后无法恢复

所以工程上更稳的方式是：

`模型负责语义决策，orchestrator + state 负责流程控制。`

---

## 6. 常见面试题回答模板

### 6.1 什么是 Action

`Action` 是模型输出的结构化决策，用来告诉 orchestrator 下一步该做什么。

例如：
- `respond`
- `ask_user`
- `finish`
- `call_tool`

一句话：

`Action 是模型对“下一步动作”的决策结果。`

### 6.2 什么是 ToolResult

`ToolResult` 是工具实际执行后的返回结果，表示这次调用是否成功、返回了什么、错误是什么。

一句话：

`ToolResult 是环境对工具执行的反馈。`

### 6.3 Action 和 ToolResult 的区别

`Action` 是模型的决策，表示下一步要做什么；`ToolResult` 是工具执行后的反馈，表示这一步做完后得到了什么。

前者更像计划，后者更像 observation。

### 6.4 为什么这个项目已经像 Agent，而不是简单脚本

因为它不只是固定顺序执行函数，而是围绕：

`决策 -> 执行 -> observation -> 再决策`

形成最小闭环。

同时它还有：
- state 控制
- memory 上下文
- ask_user 补问
- 边界控制
- loop / retry 兜底

所以它已经具备了最小 Agent 的关键特征。

### 6.5 为什么要做 loop_count / retry_count

因为 Agent 不是普通同步函数，它可能在模型异常或工具失败时进入反复尝试。

如果没有 loop 和 retry 限制，系统可能：
- 无限循环
- token 消耗失控
- 延迟飙升
- 无法稳定退出

所以它们本质上是失控保护机制。

### 6.6 State、Memory、RAG 的区别

`State`：
- 面向流程控制
- 记录当前任务推进状态

`Memory`：
- 面向上下文维护
- 记录对话和工具 observation

`RAG`：
- 面向外部知识增强
- 解决模型知识不足，不等于会话记忆

一句话：

`State 管流程，Memory 管上下文，RAG 管外部知识。`

---

## 7. 这个项目目前的优点

### 7.1 已完成的工程点

- 最小闭环已经形成
- ask_user 机制已经落地
- ToolResult 已回灌模型
- history / state 边界已开始分清
- memory 已从单一 message 升级成多类型 record
- 配置开始从硬编码迁到 yaml
- 工具有工作区边界控制

### 7.2 这个项目能体现什么能力

- 能设计最小 Agent 架构
- 能做工具调用闭环
- 能管理状态与上下文
- 能做结构化输出协议
- 能做最小工程化改造

---

## 8. 项目当前不足

### 8.1 还没有完全做好的点

- 多文件任务还没有正式做成任务队列
- 缺少系统化 eval
- 缺少测试样例集
- config loader 还可以继续清理
- API key 目前为了测试放在 yaml 中，不适合正式仓库

### 8.2 我下一步怎么升级

我会优先往 Workflow Agent 方向演进，而不是盲目加更多工具。

下一步最合理的是：
- 在 state 中增加 `pending_files / completed_files`
- 支持多文件读取和多文件总结
- 让 orchestrator 控制任务队列推进
- 模型负责语义理解和最终总结

这样项目会从“单步闭环 Agent”进一步升级成“专用 Workflow Agent”。

---

## 9. Workflow Agent 延伸表达

### 9.1 什么是 Workflow Agent

Workflow Agent 不是让模型完全自由发挥，而是：
- 流程骨架先定好
- 模型在部分节点做判断或生成
- 工具和状态由系统控制

一句话：

`Workflow Agent = Agent 能力 + 工作流编排`

### 9.2 为什么多文件任务更适合 Workflow

因为“读取多个文件 -> 汇总 -> 输出”属于：
- 步骤固定
- 可枚举
- 可程序化

这种任务更适合：

`orchestrator + state 维护任务队列`

而不是完全靠模型自己记住执行顺序。

### 9.3 如果面试官问你为什么不全交给模型

可以这样回答：

如果完全靠模型自己记任务顺序，会有重复执行、漏步骤、顺序混乱、失败后难恢复的问题。

所以更稳的做法是：
- 模型负责意图理解、计划建议、最终生成
- orchestrator 负责执行编排和状态推进

---

## 10. 一段完整项目介绍话术

可以直接背这段：

我做了一个本地文件 Agent，目标是把 Agent 最核心的工程骨架跑通。系统入口在 `app.py`，流程调度由 `orchestrator` 负责，模型层输出结构化 `Action`，工具层负责 `list_files` 和 `read_file`，工具执行后的 `ToolResult` 会回灌模型形成最小闭环。项目里我重点做了 `state` 和 `memory` 的区分，让 `state` 管流程、`memory` 管上下文，同时实现了 ask_user、retry/loop 控制、工作区边界限制，以及内部 memory 到模型 messages 的适配层。下一步我准备把它升级成支持多文件任务队列的 Workflow Agent。

---

## 11. 面试前复习重点

优先复习这些问题：
- 为什么 ToolResult.success 不等于任务完成
- history 和 state 的区别
- Action 和 ToolResult 的区别
- 为什么要有 ask_user
- 为什么 memory 要升级成多类型 record
- 为什么需要 to_model_messages
- 为什么 workflow 更适合多文件任务
- 这个项目为什么已经开始像 Agent，而不是简单脚本

---

## 12. 一句话记忆卡片

- `Tool success != Task finished`
- `history 给模型看，state 给程序控`
- `Action 是决策，ToolResult 是反馈`
- `Memory 管上下文，State 管流程，RAG 管外部知识`
- `内部结构 != 外部模型接口格式`
- `模型负责语义决策，orchestrator 负责流程控制`
- `Workflow Agent 更强调可控执行，而不是完全自由决策`
