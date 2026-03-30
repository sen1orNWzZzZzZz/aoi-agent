from agent.orchestrator import run_turn
from agent.state import create_initial_state
from agent.memory import create_memory
from core.constants import WORKSPACE_ROOT


def main():
    history = create_memory()
    state = create_initial_state()

    print(f"File Agent 已启动，工作区: {WORKSPACE_ROOT}")
    print("输入 exit 或 quit 退出。")

    while True:
        user_input = input("你: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Agent: 已退出。")
            break

        if not user_input:
            continue

        reply, history, state = run_turn(user_input, history, state)
        state.retry_count = 0
        state.loop_count = 0
        print(f"Agent: {reply}")


if __name__ == "__main__":
    main()
