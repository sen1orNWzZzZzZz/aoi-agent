from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


BASE_DIR = Path(__file__).resolve().parent


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable[[str], str]


def get_time(_: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间是 {now}"


def list_files(_: str) -> str:
    entries = sorted(path.name for path in BASE_DIR.iterdir())
    if not entries:
        return "当前目录没有文件。"
    return "当前目录文件如下：\n" + "\n".join(f"- {name}" for name in entries)


def read_file(argument: str) -> str:
    target = argument.strip()
    if not target:
        return "请提供文件名，例如：读取文件 demo.py"

    path = (BASE_DIR / target).resolve()
    if BASE_DIR not in path.parents and path != BASE_DIR:
        return "只能读取当前项目目录内的文件。"
    if not path.exists():
        return f"文件不存在：{target}"
    if path.is_dir():
        return f"{target} 是目录，不是文件。"

    content = path.read_text(encoding="utf-8", errors="replace")
    preview = "\n".join(content.splitlines()[:20])
    return f"文件预览：{target}\n{preview}"


class SimpleAgent:
    def __init__(self) -> None:
        self.tools = {
            "get_time": Tool("get_time", "查询当前时间", get_time),
            "list_files": Tool("list_files", "列出当前目录文件", list_files),
            "read_file": Tool("read_file", "读取指定文件内容", read_file),
        }
        self.history: list[tuple[str, str]] = []

    def decide(self, user_input: str) -> tuple[str, str]:
        text = user_input.strip()
        lowered = text.lower()

        if any(word in text for word in ("时间", "几点", "日期")) or "time" in lowered:
            return "get_time", ""
        if text.startswith("读取文件"):
            return "read_file", text.replace("读取文件", "", 1).strip()
        if text.startswith("查看文件"):
            return "read_file", text.replace("查看文件", "", 1).strip()
        if any(word in text for word in ("看下文件", "看看文件", "列出文件", "目录", "ls", "看下这里的文件")):
            return "list_files", ""

        return "respond", text

    def respond(self, user_input: str) -> str:
        action, argument = self.decide(user_input)

        if action == "respond":
            answer = (
                "我现在是一个最小示例 agent，还没有接入真实大模型。\n"
                "我能演示 3 个核心能力：查时间、列目录、读文件。\n"
                "你可以试试：\n"
                "- 现在几点\n"
                "- 看下文件\n"
                "- 读取文件 demo.py"
            )
        else:
            tool = self.tools[action]
            observation = tool.handler(argument)
            answer = (
                f"决策：调用工具 `{tool.name}`\n"
                f"工具说明：{tool.description}\n"
                f"观察结果：\n{observation}"
            )

        self.history.append((user_input, answer))
        return answer


def main() -> None:
    agent = SimpleAgent()
    print("Simple Agent 已启动。输入 exit 退出。")
    print("可试命令：现在几点 / 看下文件 / 读取文件 demo.py")

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Agent：已退出。")
            break
        if not user_input:
            continue
        print(f"Agent：\n{agent.respond(user_input)}")


if __name__ == "__main__":
    main()
