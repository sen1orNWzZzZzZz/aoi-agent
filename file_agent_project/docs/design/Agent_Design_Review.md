# File Agent 学习复盘

> 目标：把这次从 0 开始设计和实现本地文件 Agent 的过程记录下来，包含设计思路、犯过的错、错误代码、修正代码、以及每一步真正学到的工程原则。

---

## 1. 项目目标

我们这次做的是一个最小可运行的本地文件 Agent。

第一版目标能力：
- 列出当前目录文件
- 读取指定文件
- 总结指定文件
- 缺少文件名时 ask_user
- 使用 history / state 维护多轮上下文
- 使用 OpenAI-compatible 模型服务做决策
- 使用工具调用 + 结果回传模型形成最小 Agent 闭环

项目目录：
- `file_agent_project/`

核心模块：
- `core/schemas.py`
- `agent/state.py`
- `agent/memory.py`
- `tools/list_files.py`
- `tools/read_file.py`
- `agent/prompt.py`
- `agent/model.py`
- `agent/orchestrator.py`
- `app.py`

---

## 2. 我们先学会了什么是 Agent

在真正写代码前，先明确了 Agent 不是“会调用工具的大模型”这么简单。

最重要的闭环：

`用户输入 -> 模型决策 -> 调工具 -> 工具返回结果 -> 再次决策 -> 最终回复`

关键概念：
- Prompt：行为规则，不只是角色设定
- Tool：让模型能动手
- State：当前任务走到哪一步
- Memory：保存会话历史和可复用信息
- Orchestrator：总调度中心
- Action：当前这一步要做什么
- ToolResult：工具这次执行得怎么样

---

## 3. 项目结构是怎么一步步设计出来的

### 3.1 最初的模块拆分

先把项目拆成：
- 输入层
- 工具层
- 调度层
- 记忆层
- 模型层

后来进一步工程化成：
- `app.py`：程序入口和输入输出
- `orchestrator.py`：总调度、规则控制、异常处理、流程推进
- `prompt.py`：系统提示词
- `state.py`：当前任务状态
- `memory.py`：会话历史
- `model.py`：模型调用与 Action 解析
- `tools/`：外部动作执行
- `schemas.py`：Action / ToolResult / AgentState 数据结构
- `constants.py`：配置和常量

### 3.2 最小工具集是怎么确定的

一开始想做 3 个工具：
- 列文件
- 读文件
- 总结文件

后来经过分析发现：
- “列文件”和“读文件”是真正的工具能力
- “总结”更像模型能力，不应该一开始就包装成工具

最后第一版定为：
- `list_files`
- `read_file`

而“总结文件”的流程是：
- 先调用 `read_file`
- 再把工具结果交回模型，让模型生成总结

这一步非常关键，因为它决定了 Agent 更像“工具脚本”还是“闭环系统”。

---

## 4. 数据结构是怎么设计出来的

### 4.1 最终定下来的核心结构

#### `Action`

```python
@dataclass
class Action:
    action_type: str
    tool_name: str
    tool_args: dict
    message: str
    finish_reason: str
```

#### `ToolResult`

```python
@dataclass
class ToolResult:
    tool_name: str
    content: str
    success: bool
    error_message: str
```

#### `AgentState`

```python
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
```

---

## 5. 我犯过的典型错误和修正

下面这部分是最值得反复看的，因为这些坑几乎都是 Agent 初学者会踩的。

### 5.1 错误一：把“函数本身”和“函数调用结果”混了

这是最早最重要的坑。

错误理解：
- 以为存一个工具时，直接把函数执行掉也行

错误代码模式：

```python
handler = get_time()
```

正确理解：
- `get_time` 是函数本身
- `get_time()` 是执行结果
- Agent 需要先注册工具，后续按需调用

正确代码模式：

```python
handler = get_time
```

学到的原则：

`不带括号是函数本身，带括号是立刻执行。`

---

### 5.2 错误二：Action 和 State 分不清

一开始容易把“这一步要做什么”和“当前系统是什么状态”混在一起。

后来理清：
- `Action`：当前这一步要执行的动作
- `State`：当前任务执行到什么位置了

一句话记忆：

- `Action` 决定下一步做什么
- `State` 记录当前已经走到哪

---

### 5.3 错误三：ToolResult 字段设计错位

最初错误设计里，把 `ToolResult` 写成了这种方向：

错误代码：

```python
@dataclass
class ToolResult:
    tool_name: str
    discribe: str
    success: bool
    error_message: bool
```

问题：
- `discribe` 拼错
- 工具结果不该存“描述”，而应该存“返回内容”
- `error_message` 应该是字符串，不是布尔值

修正后：

```python
@dataclass
class ToolResult:
    tool_name: str
    content: str
    success: bool
    error_message: str
```

学到的原则：

`工具结果要稳定返回结构，不要在成功和失败时随便变字段。`

---

### 5.4 错误四：Action 的 `tool_args` 写成字符串

错误代码：

```python
@dataclass
class Action:
    action_type: str
    tool_name: str
    tool_args: str
    message: str
    finish_reason: str
```

问题：
- 工具参数本质上是键值对，不是一个字符串
- 后面 `read_file` 要传 `{"file_name": "demo.py"}` 这种结构

修正后：

```python
@dataclass
class Action:
    action_type: str
    tool_name: str
    tool_args: dict
    message: str
    finish_reason: str
```

学到的原则：

`结构化输出必须和业务使用方式一致。`

---

### 5.5 错误五：以为 memory 一定要很复杂

一开始会觉得 memory 很高级，可能要上数据库、向量库、复杂结构。

但第一版项目里，其实只需要：
- 用列表保存最近几轮会话
- 每条记录是 `role + content`

最终实现：

```python
def create_memory():
    return []


def add_memory(memory, role, content):
    memory.append({"role": role, "content": content})


def get_recent_memory(memory, limit=3):
    return memory[-limit:]
```

学到的原则：

`第一版先跑通最小闭环，别一开始就把简单问题做复杂。`

---

### 5.6 错误六：工具返回结构不完整

在 `list_files.py` 的早期版本里，出现过这些错误：
- `"\n".join(files)` 写了但没用上
- 成功时 `content` 传的是列表，不是字符串
- 成功时漏了 `error_message`
- 失败时 `error_message=e`，直接把异常对象塞进去

错误代码模式：

```python
files = os.listdir('.')
"\n".join(files)
return ToolResult(tool_name="list_files", success=True, content=files)
```

和：

```python
except Exception as e:
    return ToolResult(tool_name="list_files", success=False, error_message=e)
```

修正后：

```python
def list_files():
    try:
        files = os.listdir('.')
        files = "\n".join(files)
        return ToolResult(
            tool_name="list_files",
            success=True,
            content=files,
            error_message=""
        )
    except Exception as e:
        return ToolResult(
            tool_name="list_files",
            success=False,
            error_message=str(e),
            content=""
        )
```

学到的原则：

`成功和失败都要返回完整 ToolResult，只是值不同。`

---

### 5.7 错误七：`read_file` 忘了做空参数检查

一开始 `read_file(file_name)` 只做了：
- 路径是否存在
- 是否是目录

但没有先检查 `file_name` 是否为空。

后来修正为：

```python
def read_file(file_name):
    if not file_name:
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="缺少正确的文件路径"
        )
```

然后再检查：
- `os.path.exists(file_name)`
- `os.path.isdir(file_name)`
- `open(file_name, "r", encoding="utf-8")`

学到的原则：

`参数合法性检查永远比真正执行更早。`

---

### 5.8 错误八：Prompt 只写角色，不写协议

最开始 prompt 很容易只写：
- 你是谁
- 你能做什么

但这远远不够。

真正让模型稳定返回 `Action` 的关键是补上：
- 只能返回 JSON
- 不允许额外解释
- 所有字段必须都返回
- `respond / ask_user / finish` 时 `tool_name=""`、`tool_args={}`
- 总结前必须先读文件
- 不允许乱猜文件名

学到的原则：

`Prompt 在 Agent 里不是文案，而是协议和控制逻辑。`

---

### 5.9 错误九：`messages` 组装方式完全错了

这是接模型时最典型的坑。

错误写法：

```python
message = SYSTEM_PROMPT + history + user_input
response = client.chat.completions.create(
    model=model,
    messages=[message],
    stream=False
)
```

问题：
- `history` 是列表，不能直接字符串拼接
- `messages` 需要的是消息对象列表，不是一个拼好的大字符串

修正思路：

```python
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
messages.extend(history)
messages.append({"role": "user", "content": current_input})
```

其中 `current_input` 里还加入了关键状态字段：
- `current_intent`
- `current_file`
- `missing_info`
- `waiting_for_user`
- `loop_count`
- `retry_count`
- `last_tool_name`
- `last_tool_result`

学到的原则：

`OpenAI-compatible 的 messages 是结构化消息列表，不是拼接大字符串。`

---

### 5.10 错误十：把响应对象直接 `json.loads`

错误代码：

```python
data = json.loads(response)
action = Action(**data)
```

问题：
- `response` 是 SDK 返回对象，不是 JSON 字符串

修正后：

```python
content = response.choices[0].message.content
data = json.loads(content)
action = Action(**data)
```

学到的原则：

`response 对象 != 模型返回文本 != 解析后的 JSON。`

---

### 5.11 错误十一：异常时返回 `1`

这是模型层一个典型类型错误。

错误代码：

```python
except Exception as e:
    print("模型调用错误" + str(e))
    return 1
```

问题：
- `get_model_action()` 的职责是始终返回 `Action`
- 返回整数会让上层 orchestrator 直接炸掉

修正后：

```python
return Action(
    action_type="finish",
    tool_name="",
    tool_args={},
    message="模型调用失败",
    finish_reason="model_error"
)
```

并且对两类异常都做了兜底：
- 模型接口调用失败
- 模型返回结果 JSON 解析失败

学到的原则：

`函数的返回类型要稳定，异常分支也不能乱返回。`

---

### 5.12 错误十二：在 orchestrator 里不知道 `respond` 分支要干嘛

一开始写到这里时，会卡在：

```python
if action.action_type == "respond":
    state.
```

为什么会卡？
- 误以为每个分支都必须修改 state

后来理清：
- `respond` 的核心不是改 state，而是：
  - 把消息写进 history
  - 返回给 app.py

正确代码模式：

```python
if action.action_type == "respond":
    add_memory(history, "assistant", action.message)
    return action.message, history, state
```

学到的原则：

`不是每个 action 都必须改 state。respond 的核心是产出回复。`

---

### 5.13 错误十三：以为 state 要在 orchestrator 里初始化

后来理清：
- `state` 不是每轮重建
- `state = create_initial_state()` 只应该在程序启动时做一次
- `orchestrator` 只负责更新已有 state

正确调用链：

```python
history = create_memory()
state = create_initial_state()

reply, history, state = run_turn(user_input, history, state)
```

学到的原则：

`app.py 负责初始化 state，orchestrator 负责推进 state。`

---

### 5.14 错误十四：`call_tool` 里把函数本身塞进了 state

这是前面“函数本身 vs 执行结果”又一次在项目里真实重现。

错误代码：

```python
state.last_tool_result = list_files
```

问题：
- 存进去的是函数，不是工具执行结果

修正后：

```python
tool_result = list_files()
state.last_tool_result = tool_result
```

学到的原则：

`工具调用一定要接返回值，再更新 state。`

---

### 5.15 错误十五：`call_tool` 调完工具后不返回任何结果

一开始写 `call_tool` 时，做了：
- 调工具
- 更新 state

但没做：
- 成功/失败后给用户返回什么

后来补成：

```python
if tool_result.success:
    add_memory(history, "assistant", tool_result.content)
    return tool_result.content, history, state
else:
    state.retry_count += 1
    add_memory(history, "assistant", tool_result.error_message)
    return tool_result.error_message, history, state
```

学到的原则：

`工具层不是终点，orchestrator 必须把工具结果接回主流程。`

---

### 5.16 错误十六：总结文件时直接把原文返回给用户

这是整个项目里最重要的一次行为级 bug。

问题表现：
- 用户输入：`总结 demo.py`
- 系统先正确调用 `read_file`
- 但工具成功后直接 `return tool_result.content`
- 所以用户拿到的是全文，而不是总结

错误逻辑：

```python
if tool_result.success:
    add_memory(history, "assistant", tool_result.content)
    return tool_result.content, history, state
```

为什么这是错的？
- 因为“读取文件”和“总结文件”不是一回事
- 工具只负责拿数据，不负责完成最终任务
- 应该让模型在拿到 observation 之后再次决策

修正后思路：

```python
if tool_result.success:
    follow_action = get_model_action(
        user_input=user_input,
        history=history,
        state=state,
    )
    if follow_action.action_type in {"respond", "finish"}:
        add_memory(history, "assistant", follow_action.message)
        return follow_action.message, history, state
```

如果 follow_action 没有给出最终回复，再退回原始工具结果作为兜底。

学到的原则：

`会调工具，不等于会做 Agent；工具成功后再次决策，才开始像真正的 Agent。`

---

## 6. 当前项目里已经成功的代码骨架

### 6.1 `state.py`

```python
from core.schemas import AgentState, ToolResult


def create_initial_state():
    empty_result = ToolResult(
        tool_name="",
        content="",
        success=False,
        error_message=""
    )
    return AgentState(
        current_intent="",
        current_file="",
        missing_info="",
        waiting_for_user=False,
        loop_count=0,
        retry_count=0,
        last_tool_name="",
        last_tool_result=empty_result
    )


def reset_state():
    return create_initial_state()
```

### 6.2 `memory.py`

```python
def create_memory():
    return []


def add_memory(memory, role, content):
    memory.append({"role": role, "content": content})


def get_recent_memory(memory, limit=3):
    return memory[-limit:]
```

### 6.3 `list_files.py`

```python
import os
from core.schemas import ToolResult


def list_files():
    try:
        files = os.listdir('.')
        files = "\n".join(files)
        return ToolResult(
            tool_name="list_files",
            success=True,
            content=files,
            error_message=""
        )
    except Exception as e:
        return ToolResult(
            tool_name="list_files",
            success=False,
            error_message=str(e),
            content=""
        )
```

### 6.4 `read_file.py`

```python
import os
from core.schemas import ToolResult


def read_file(file_name):
    if not file_name:
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="缺少正确的文件路径"
        )

    if not os.path.exists(file_name):
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="文件路径不存在"
        )

    if os.path.isdir(file_name):
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="目标是目录，不是文件"
        )

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            file_content = file.read()
        return ToolResult(
            tool_name="read_file",
            content=file_content,
            success=True,
            error_message=""
        )
    except Exception as e:
        return ToolResult(
            tool_name="read_file",
            content="",
            success=False,
            error_message="打开文件时发生错误: " + str(e)
        )
```

### 6.5 `model.py` 核心思路

```python
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
messages.extend(history)
messages.append({"role": "user", "content": current_input})

response = client.chat.completions.create(
    model=model,
    messages=messages,
    stream=False
)

content = response.choices[0].message.content
data = json.loads(content)
action = Action(**data)
```

异常时统一返回 `Action(action_type="finish", ...)`。

### 6.6 `app.py` 最小调用链

```python
history = create_memory()
state = create_initial_state()

while True:
    user_input = input("你：").strip()
    reply, history, state = run_turn(user_input, history, state)
    print(f"Agent：{reply}")
```

---

## 7. 这次项目里最重要的 10 条经验

1. 先设计数据结构，再写流程代码
2. `Action`、`State`、`ToolResult` 必须分清
3. 工具返回结构一定要稳定
4. Prompt 在 Agent 里是协议和规则，不只是角色文案
5. OpenAI-compatible 的 `messages` 必须是结构化消息列表
6. 模型调用失败和 JSON 解析失败都要兜底
7. `app.py` 初始化 state，orchestrator 更新 state
8. `call_tool` 的核心不是调工具，而是把工具结果接回主流程
9. 总结任务不能等于读文件任务
10. 真正的 Agent 关键在于：`tool -> observe -> re-decide`

---

## 8. 当前项目还可以继续改进的地方

1. `loop_count / retry_count` 真正生效
2. `ask_user` 不要硬编码 `file_name`
3. 未知 `tool_name` 的兜底更规范
4. API key 改成环境变量
5. Prompt 进一步压缩和稳定化
6. `history` 和 `state` 的写入策略进一步优化
7. 对很长的文件内容做截断或摘要，降低 token 成本
8. 对模型返回非 JSON 的情况做更好的容错

---

## 9. 最后一条总结

这次最重要的收获不是“写了多少 Python”，而是：

`你已经从“理解 Agent 概念”进入到了“会搭一个最小 Agent 系统”的阶段。`

尤其是这句一定要记住：

`会调工具，不等于会做 Agent；工具成功后再次决策，才开始像真正的 Agent。`
