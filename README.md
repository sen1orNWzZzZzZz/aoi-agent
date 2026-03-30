# Simple Agent Demo

这个目录里有一个适合练手的最小 agent 示例：[simple_agent.py](D:/AAAAA-sen1orN/project/agentDemo/simple_agent.py)。

## 先理解这 4 个部分

1. `输入`
   用户在命令行输入一句话。
2. `决策`
   `decide()` 判断这句话该直接回复，还是调用工具。
3. `工具`
   这里有 3 个工具：查时间、列文件、读文件。
4. `观察后输出`
   工具返回结果后，agent 再把结果组织成自然语言输出。

这就是最基础的 agent 闭环：

`用户问题 -> 判断是否调用工具 -> 执行工具 -> 根据结果回答`

## 运行方式

```powershell
python simple_agent.py
```

可以直接试：

```text
现在几点
看下文件
读取文件 demo.py
```

## 为什么先不用 LangChain

你现在的环境是 `Python 3.14`，而已安装的 `langchain-core` 会触发 `pydantic.v1` 兼容性 warning。对练习生来说，先把 agent 的基本结构跑通，比先套框架更重要。

建议顺序是：

1. 先看懂这个最小版本
2. 再把 `decide()` 改成调用真实大模型
3. 最后再考虑接入 LangChain 或其他 agent 框架

## 下一步该怎么升级

当你看懂这个文件后，可以按这个顺序升级：

1. 增加一个真实大模型接口，让模型决定是否调用工具
2. 给工具加参数校验和异常处理
3. 加入短期记忆，让 agent 记住上轮对话
4. 把工具注册改成更规范的结构
5. 再接入 LangChain、OpenAI Agents SDK 或 LangGraph
