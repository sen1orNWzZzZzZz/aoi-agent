# AI 转型学习路线与求职计划

## 你的定位

- 当前背景：2 年 Java 后端开发
- 转型目标：AI 应用工程 / Agent 工程
- 求职目标岗位：
  - AI 应用工程师
  - Agent / LLM 工程师
  - 智能体平台 / AI 后端工程师

你的核心优势不是去卷算法训练，而是把模型接进业务系统，做成可运行、可恢复、可观测的工程系统。

---

## 总目标

把自己培养成：

**有后端工程基础，能独立完成 AI 应用与 Agent 系统设计、开发、调试和落地的工程师。**

求职时需要具备的表达能力：

- 能讲清楚模型负责什么，程序负责什么
- 能讲清楚 history / state / workflow / ask_user / resume
- 能讲清楚 trace、失败分流、工具调用、RAG、评测
- 能展示至少 2 个可运行、可讲解的 AI 项目

---

## 三阶段路线

### 第一阶段：收稳 Agent Core

时间：4 到 6 周

目标：

- 把 `file_agent_project` 做成最小可讲的 Workflow Agent Core

必须吃透的内容：

- history vs state
- task_type vs workflow_type
- ask_user / resume
- trace / 可观测性
- 失败分流
- 工具调用
- 结构化输出

阶段产出：

- 一个能运行的最小 Agent Core 项目
- 一份架构说明文档
- 一份可口述的项目讲稿

---

### 第二阶段：补齐 AI 应用工程核心能力

时间：8 到 12 周

目标：

- 从“会做 Agent Demo”升级到“能做 AI 应用系统”

需要补齐的 4 项能力：

1. RAG
   - 文档切分
   - embedding / 检索
   - chunk 策略
   - 召回与 grounding

2. Code Execution Tool
   - 工具执行边界
   - sandbox 思维
   - 参数结构化
   - 超时与异常处理

3. 评测与观测
   - trace 设计
   - case 驱动开发
   - 基本 eval 思维
   - 稳定性验证

4. 服务化
   - API 化
   - session 管理
   - 状态存储
   - 配置管理

阶段产出：

- 一个支持 RAG 的最小平台
- 一个支持 Code Tool 的最小平台
- 一套基础 case 与 trace 体系

---

### 第三阶段：做成作品集并准备求职

时间：6 到 8 周

目标：

- 打磨成能投递和面试的项目资产

至少准备两个项目：

1. Workflow Agent Core
   - 能讲状态机、resume、trace、失败分流、工具抽象

2. 一个业务型 AI 应用
   - 推荐方向：
     - 本地知识库问答 + 工具调用
     - 文档助手 / 代码助手 / 运维助手

要求：

- 有明确场景
- 有系统架构图
- 有 README
- 有可运行 demo
- 有 case 或评测说明
- 能口头讲清设计取舍

---

## 未来 6 个月学习路线

### 第 1 个月：收完 Agent Core

重点：

- 收稳 `file_agent_project`
- 完成 resume 语义闭环
- 统一失败分流
- 收稳 trace

阶段目标：

- `v2.2` 收口
- 进入 `v3.0 Code Execution Tool` 设计

---

### 第 2 个月：工具系统化

重点：

- 工具执行层抽象
- Code Execution Tool
- ToolResult 标准化

阶段目标：

- 项目不再只会文件工具
- 开始具备平台 core 的雏形

---

### 第 3 个月：RAG

重点：

- 向量检索
- 文档切分
- grounding
- 检索日志与失败处理

阶段目标：

- 平台支持本地知识库问答
- 能讲清“检索负责提供证据，模型负责生成”

---

### 第 4 个月：服务化与评测

重点：

- API 服务化
- session 管理
- trace 输出
- case / eval

阶段目标：

- 从脚本进化成系统

---

### 第 5 到 6 个月：作品集与面试

重点：

- 打磨 README
- 补架构图
- 准备项目讲稿
- 整理 AI 应用 / Agent 面试题

阶段目标：

- GitHub 可展示
- 简历可投递
- 可面试 AI 应用 / Agent 工程岗位

---

## 每周学习节奏

### 工作日

- 每天 1.5 到 2 小时
- 推荐分配：
  - 40 分钟：理论理解
  - 60 分钟：项目编码
  - 20 分钟：复盘记录

### 周末

- 每天 4 到 6 小时
- 用于：
  - 集中开发
  - case 测试
  - 文档整理
  - demo 打磨

---

## 学习优先级

### 必学

- Python 工程能力
- LLM API 调用
- prompt 结构化输出
- tool calling
- state / workflow / resume
- RAG
- trace / eval
- API 服务化

### 次优先

- MCP
- 多模型适配
- 简单前端展示

### 暂时不用深卷

- 模型训练
- 微调底层细节
- 数学推导型算法路线

---

## 求职策略

投递关键词：

- AI 应用工程师
- LLM 工程师
- Agent 工程师
- 智能体平台工程师
- AI 后端工程师
- RAG 工程师

简历定位：

**Java 后端背景 + Python/LLM/Agent 项目经验 + AI 工作流工程能力**

你的卖点不是“会调 API”，而是：

- 会做 Agent workflow
- 会做状态与恢复
- 会做 trace 与失败分流
- 会把 AI 能力变成工程系统

---

## 未来 30 天任务

### 第 1 周

- 收完 resume schema
- 改 prompt 支持 `Action.resume`
- 改 model 解析 resume
- 改 orchestrator 消费 resume

### 第 2 周

- 统一单文件 / 多文件失败分流
- 收稳 trace 事件
- 做 8 到 10 条 case

### 第 3 周

- 设计 Code Execution Tool
- 完成最小实现
- 接入 orchestrator

### 第 4 周

- 写项目文档
- 补架构图
- 准备项目讲稿
- 正式进入 `v3.0`

---

## 明天开始时的执行顺序

不要一上来学新概念，先把当前设计闭环。

明天建议顺序：

1. 复查 `core/schemas.py`
2. 改 `agent/prompt.py`，补 `Action.resume`
3. 改 `agent/model.py`，支持解析 `resume`
4. 改 `agent/orchestrator.py`，消费 `resume`

这个顺序对应：

- schema 是结构
- prompt 是模型输出约束
- model 是解析层
- orchestrator 是消费层

---

## 最终目标

你不是去转“懂一点 AI 的后端”，而是转成：

**懂工程、懂状态机、懂系统边界的 AI 应用工程师 / Agent 工程师。**

只要你未来 4 到 6 个月持续做两件事：

- 把 Agent Core 真正吃透
- 做出 2 个能讲清楚的 AI 项目

你是有现实机会找到相关工作的。

---

## 附：未来 12 周周计划表

### 第 1 周：收 resume 设计闭环

目标：

- 回到 `file_agent_project`
- 收完 resume 相关 schema、prompt、model、orchestrator 主链路设计

本周任务：

- 复查 `core/schemas.py`
- 完成 `Action.resume` 和 `ResumeContext` 的落地
- 修改 `agent/prompt.py`，让模型理解 resume 输出
- 修改 `agent/model.py`，支持 resume JSON 解析

本周产出：

- 一版能跑通 resume 结构的代码
- 一份你自己能讲明白的 resume 设计说明

---

### 第 2 周：收 ask_user / resume 主流程

目标：

- 让暂停恢复真正可用，不再只是表面继续

本周任务：

- 改 `agent/orchestrator.py` 的 `waiting_for_user` 分支
- 实现 `workflow_repair` 和 `action_patch` 的分流
- 多文件恢复时修 `current_file` 和 `pending_files[0]`
- 单文件缺参数时补 `pending_action`

本周产出：

- 一版真正闭环的 ask_user / resume 流程
- 3 到 5 条恢复场景 case

---

### 第 3 周：统一失败分流

目标：

- 单文件和多文件失败语义统一

本周任务：

- 统一 `user_fixable_error / retryable_error / fatal_error`
- 让错误分类决定状态转移
- 区分“错误语义一致”和“恢复对象不同”
- 收掉当前散落在 orchestrator 中的失败处理分支

本周产出：

- 一版统一失败分流语义
- 一份错误分类与恢复策略说明

---

### 第 4 周：收稳 trace 和 case

目标：

- 让 trace 能比较可信
- 用 case 验证当前 v2.2 是否收口

本周任务：

- 统一 trace 事件命名
- 尽量记录真实 `action_type`
- 补关键 case：
  - 单文件读取
  - 单文件总结
  - 多文件总结
  - ask_user / resume
  - 文件不存在
  - 模糊文件名

本周产出：

- 一份基础 case 清单
- 一版更可信的 trace 输出

---

### 第 5 周：开始 v3.0 Code Execution Tool 设计

目标：

- 从 File Agent 进入通用 Tool Agent Core

本周任务：

- 先做设计，不急着写代码
- 明确 Code Tool 的输入输出结构
- 思考：
  - 命令执行边界
  - sandbox 思路
  - timeout
  - 错误返回

本周产出：

- 一份 `v3.0 Code Execution Tool` 设计文档

---

### 第 6 周：实现最小 Code Execution Tool

目标：

- 做出最小可运行代码执行工具

本周任务：

- 抽工具执行入口
- 加 `execute_code` 或等价工具
- 标准化 `ToolResult`
- 接入 orchestrator

本周产出：

- 一个最小可运行的 Code Tool
- 相关成功 / 失败 case

---

### 第 7 周：工具调用系统化

目标：

- 不再让 orchestrator 直接堆工具分支

本周任务：

- 封装统一工具执行入口
- 收敛 `tool_name -> tool_result` 分发逻辑
- 让后续工具扩展更简单

本周产出：

- 一版更清晰的工具调用层

---

### 第 8 周：开始 RAG 设计

目标：

- 进入 AI 应用工程核心能力第二块

本周任务：

- 学习最小 RAG 链路
- 理解：
  - chunk
  - embedding
  - retrieval
  - grounding
- 设计你的 RAG Tool 最小版本

本周产出：

- 一份 RAG Tool 设计说明

---

### 第 9 周：实现最小 RAG Tool

目标：

- 让平台具备本地知识检索能力

本周任务：

- 完成最小索引与检索流程
- 把 RAG 作为工具接入 Agent Core
- 记录检索相关 trace

本周产出：

- 一个最小可用的 RAG Tool demo

---

### 第 10 周：服务化改造

目标：

- 从 CLI 迈向系统

本周任务：

- 设计 session 接口
- 设计 turn 请求与返回结构
- 选择简单服务框架
- 把核心流程 API 化

本周产出：

- 一个最小 API 服务版本

---

### 第 11 周：作品化打磨

目标：

- 让项目能展示、能讲解、能放进简历

本周任务：

- 补 README
- 画架构图
- 整理系统模块说明
- 准备 demo 场景

本周产出：

- 一版可展示项目主页
- 一版可用于面试的项目讲稿

---

### 第 12 周：面试准备与投递预热

目标：

- 把项目能力转成可面试表达

本周任务：

- 准备核心问题答案：
  - 为什么需要 workflow state
  - 为什么 ask_user 不是终态
  - 为什么模型不能直接掌控 workflow
  - RAG 的边界是什么
  - tool calling 和 orchestrator 的区别
- 整理简历项目描述
- 开始小范围投递或模拟面试

本周产出：

- 一版 AI 岗位简历
- 一版面试问答清单
