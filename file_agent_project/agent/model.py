import json

from openai import OpenAI

from agent.memory import get_recent_memory
from agent.prompt import SYSTEM_PROMPT
from core.constants import api_key, base_url, model
from core.schemas import Action

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
        f"current_intent: {state.current_intent}\n"
        f"current_file: {state.current_file}\n"
        f"missing_info: {state.missing_info}\n"
        f"waiting_for_user: {state.waiting_for_user}\n"
        f"loop_count: {state.loop_count}\n"
        f"retry_count: {state.retry_count}\n"
        f"last_tool_name: {state.last_tool_name}\n"
        f"last_tool_result_success: {state.last_tool_result.success}\n"
        f"last_tool_result: {state.last_tool_result.content}\n"
        f"last_tool_error: {state.last_tool_result.error_message}\n"
        f"collected_file_read_result: {state.collected_contents}\n"
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(to_model_messages(get_recent_memory(history, limit=6)))
    messages.append({"role": "user", "content": current_input})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
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
