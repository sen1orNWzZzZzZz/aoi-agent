from agent.memory import add_message, add_tool_result
from agent.model import get_model_action
from core.constants import MAX_LOOP
from core.schemas import AgentState, ToolResult
from tools.list_files import list_files
from tools.read_file import read_file

def _run_multi_file_step(history, state:AgentState):
    if len(state.pending_files)==0:
        return ToolResult("","",True, ""), history, state
    else:     
        state.current_file = state.pending_files[0]
        tool_result = read_file(state.current_file)
        if tool_result.success:
            state.collected_contents[state.current_file]=tool_result.content
            state.pending_files.pop(0)
            state.completed_files.append(state.current_file)
            state.last_tool_name = "read_file"
            state.last_tool_result = tool_result
            add_tool_result(history, "read_file", tool_result.content, tool_result.success)
        else:
            state.last_tool_name = "read_file"
            state.last_tool_result = tool_result
            add_tool_result(history, "read_file", tool_result.error_message, tool_result.success)
    return tool_result, history, state





def _infer_intent(user_input: str) -> str:
    lowered = user_input.lower()
    if "总结" in user_input or "summary" in lowered or "summarize" in lowered:
        return "summarize_file"
    if "读取" in user_input or "打开" in user_input or "read" in lowered:
        return "read_file"
    if "列出" in user_input or "list" in lowered:
        return "list_files"
    return "general"

def _infer_missing_info(intent: str)->str :
    if intent=="list_files":
        return "target_dir"
    elif intent in {"single_file_read","multi_file_summary", "single_file_summary"}:
        return "file_name"
    else:
        return "user_input"
def _build_tool_error(tool_name: str, message: str) -> ToolResult:
    return ToolResult(
        tool_name=tool_name,
        content="",
        success=False,
        error_message=message,
    )


def run_turn(user_input, history, state: AgentState):
    add_message(history, "user", user_input)
    #state.current_intent = _infer_intent(user_input)

    while True:
        if state.retry_count > 3:
            add_message(history, "assistant", "超过最大重试次数，自动退出。")
            return "超过最大重试次数，自动退出。", history, state

        state.loop_count += 1
        if state.loop_count >= MAX_LOOP:
            add_message(history, "assistant", "超过最大循环次数，自动退出。")
            return "超过最大循环次数，自动退出。", history, state

        

        
        if len(state.pending_files)!=0:
            multi_tool_result, history, state = _run_multi_file_step(history=history, state=state)
            if multi_tool_result.success:
                continue
            else: 
                state.retry_count=state.retry_count+1
        else : 
            if state.waiting_for_user:#处理等待用户输入的情况,拼接上下文
                resume_calling = f"已获得用户输入，当前工作流为workflow_type:{state.resume_context['workflow_type']};当前缺失信息为{state.resume_context['missing_info']};当前用户输入为：{user_input}"
                action = get_model_action(resume_calling, history,state)
                state.waiting_for_user = False
                state.missing_info = ""
                state.resume_context = {}
            else:

                if "summary" in state.workflow_type:
                    action = get_model_action(user_input="工作流完成，开始总结", history=history, state=state)
                else:    
                    action = get_model_action(user_input=user_input, history=history, state=state)
            #state.workflow_type = action.task_type
            if action.action_type == "respond":
                add_message(history, "assistant", action.message)
                state.workflow_type="idle"
                return action.message, history, state

            if action.action_type == "ask_user":
                state.waiting_for_user = True
                state.missing_info = _infer_missing_info(state.workflow_type)
                state.resume_context = {"workflow_type": state.workflow_type, "missing_info": state.missing_info}
                add_message(history, "assistant", action.message)
                return action.message, history, state

            if action.action_type == "finish":
                add_message(history, "assistant", action.message)
                state.workflow_type="idle"
                return action.message, history, state

            if action.action_type != "call_tool":
                message = f"未知 action_type: {action.action_type}"
                state.workflow_type="idle"
                add_message(history, "assistant", message)
                return message, history, state

            if action.message:
                add_message(history, "assistant", action.message)

            if action.tool_name == "list_files":
                tool_result = list_files(target_dir=action.tool_args.get("target_dir", ""))
            elif action.tool_name == "read_file":
                if action.tool_args.get("file_names"):
                    state.pending_files = list(action.tool_args.get("file_names",[]))#初始化一个新的列表这样可以不依赖别的对象
                    state.collected_contents = {}
                    state.completed_files=[]
                    state.current_file=""
                    state.workflow_type=action.task_type
                    continue
                else:
                    file_name = action.tool_args.get("file_name", "")
                    tool_result = read_file(file_name=file_name)
                    state.current_file = file_name
                    state.workflow_type=action.task_type
            else:
                tool_result = _build_tool_error(
                    action.tool_name,
                    f"未知工具: {action.tool_name}",
                )

            state.last_tool_name = tool_result.tool_name
            state.last_tool_result = tool_result

            observation = tool_result.content if tool_result.success else tool_result.error_message
            add_tool_result(
                history,
                tool_result.tool_name,
                observation,
                tool_result.success
            )

            if tool_result.success:
                continue

            state.retry_count += 1
            return tool_result.error_message, history, state
