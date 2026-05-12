from openai import OpenAI
from core.constants import api_key, base_url, model

print(f"base_url: {base_url}")
print(f"api_key 前8位: {api_key[:8] if api_key else '空'}")
print(f"model: {model}")

client = OpenAI(api_key=api_key, base_url=base_url, timeout=10)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "你好"}],
    )
    print(f"成功: {response.choices[0].message.content}")
except Exception as e:
    print(f"失败: {type(e).__name__}: {e}")
