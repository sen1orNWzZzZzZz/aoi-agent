from agent.orchestrator import run_turn
from agent.state import create_initial_state
from agent.memory import create_memory
from core.constants import WORKSPACE_ROOT
from agent.trace import append_trace_log
import uuid
from pathlib import Path


def main():
    history = create_memory()
    state = create_initial_state()
    state.session_id = str(uuid.uuid4())
    print(f"File Agent 已启动，工作区: {WORKSPACE_ROOT}")
    print("输入 exit 或 quit 退出。")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / ("trace_readable["+state.session_id+"].log")

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
        append_trace_log(state.trace_events, log_file)
        state.trace_events=[]

        print(f"Agent: {reply}")


if __name__ == "__main__":
    main()
