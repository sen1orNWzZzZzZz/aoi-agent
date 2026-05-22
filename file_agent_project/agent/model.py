import json

from openai import OpenAI

from agent.memory import get_recent_memory
from agent.prompt import SYSTEM_PROMPT
from core.constants import api_key, base_url, model
from core.schemas import Action
from tool_layer.registry import registry

def to_model_messages(memory):
    messages = []
    for record  in memory:
        if record["type"] == "message":
            messages.append({"role": record["role"],"content": record["content"],})
        elif record["type"] == "tool_result":
            messages.append({"role": "assistant","content": f"[tool:{record['tool_name']}] success={record['success']}\n{record['content']}"})
        else: 
            continue    
    return messages

def _extract_json_text(content: str) -> str:
    text = (content or "").strip()
    if text.startswith("```"):
        lines = [line for line in text.splitlines() if not line.startswith("```")]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end >= start:
        return text[start : end + 1]
    return text


def get_model_action(user_input, history, state):
    if not api_key:
        return Action(
            action_type="finish",
            tool_name="",
            tool_args={},
            message="缺少模型 API Key，请先设置 FILE_AGENT_API_KEY 或 DEEPSEEK_API_KEY。",
            finish_reason="missing_api_key",
        )

    client = OpenAI(api_key=api_key, base_url=base_url)

    current_input = (
        f"用户输入: {user_input}\n"
        f"当前状态:\n"
        f"current_file: {state.current_file}\n"
        f"missing_info: {state.missing_info}\n"
        f"waiting_for_user: {state.waiting_for_user}\n"
        f"loop_count: {state.loop_count}\n"
        f"collected_file_read_result: {state.collected_contents}\n"
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    specs = registry.get_all_spec()   # ← 用实例调用
    
    #工具启动并且开始格式化成 LLM 能看懂的文本
    tools_desc = []
    for spec in specs:
        tools_desc.append(
            f"工具名：{spec.name}\n"
            f"描述：{spec.description}\n"
            f"参数：{spec.params}\n"
            f"返回：{spec.returns}"
        )
    
    tools_text = "\n---\n".join(tools_desc)

    messages.append({"role":"system","content":"你有如下工具可供使用："+tools_text})
    messages.extend(to_model_messages(get_recent_memory(history, limit=6)))
    messages.append({"role": "user", "content": current_input})
    
    print(messages)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
            timeout=15,
        )
    except Exception:
        return Action(
            action_type="finish",
            tool_name="",
            tool_args={},
            message="模型调用失败，请检查网络、base_url 或 API Key 配置。",
            finish_reason="model_error",
        )

    try:
        content = response.choices[0].message.content
        data = json.loads(_extract_json_text(content))
        return Action(**data)
    except Exception:
        return Action(
            action_type="finish",
            tool_name="",
            tool_args={},
            message="模型返回结果解析失败，未拿到合法 JSON Action。",
            finish_reason="parse_error",
        )
