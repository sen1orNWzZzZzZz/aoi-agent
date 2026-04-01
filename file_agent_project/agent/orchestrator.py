from agent.memory import add_message, add_tool_result
from agent.model import get_model_action
from core.constants import MAX_LOOP
from core.schemas import AgentState, ToolResult
from tools.list_files import list_files
from tools.read_file import read_file
from agent.trace import TraceEvent,add_trace
from agent.state import set_default_state_workflow


#识别文件识别错误
def classify_multi_file_error(tool_result: ToolResult):
    #三个返回值（暂时）：user_fixable_error retryable_error fatal_error
    key_words_fixable_error = ["不存在","路径","目录","不是文件"]
    key_words_retryable_error = ['']
    key_words_fatal_error = ["UTF-8","utf-8","编码","encode"]
    if any(word in tool_result.error_message for word in key_words_fixable_error):
        return "user_fixable_error"
    if any(word in tool_result.error_message for word in key_words_fatal_error):
        return "fatal_error"
    return "retryable_error"


#消费待处理文件
def _run_multi_file_step(history, state:AgentState):
    if len(state.pending_files)==0:
        return ToolResult("","",True, ""), history, state
    else:     
        state.current_file = state.pending_files[0]
        add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id, 
                                                     message=f"orchestrator正在消费文件:{state.current_file}",
                                                     workflow_type=state.workflow_type,
                                                     source="orchestrator",
                                                     session_id=state.session_id,
                                                     event_type="queue_consume"))
        tool_result = read_file(state.current_file)
        if tool_result.success:
            state.collected_contents[state.current_file]=tool_result.content
            state.pending_files.pop(0)
            state.completed_files.append(state.current_file)
            state.last_tool_name = "read_file"
            state.last_tool_result = tool_result
            state.current_file_retry_count = 0
            add_tool_result(history, "read_file", tool_result.content, tool_result.success)
            
        else:
            state.last_tool_name = "read_file"
            state.last_tool_result = tool_result
            add_tool_result(history, "read_file", tool_result.error_message, tool_result.success)
    return tool_result, history, state



# def _infer_intent(user_input: str) -> str:
#     lowered = user_input.lower()
#     if "总结" in user_input or "summary" in lowered or "summarize" in lowered:
#         return "summarize_file"
#     if "读取" in user_input or "打开" in user_input or "read" in lowered:
#         return "read_file"
#     if "列出" in user_input or "list" in lowered:
#         return "list_files"
#     return "general"

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
    state.loop_count=0
    state.turn_id= state.turn_id+1
    add_message(history, "user", user_input)
    #state.current_intent = _infer_intent(user_input)

    add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id,
                                                  event_type="turn_start",
                                                  message="这轮对话开始",
                                                  workflow_type=state.workflow_type,
                                                  source="orchestrator",
                                                  session_id=state.session_id))

    while True:
        if state.retry_count > 3:
            add_message(history, "assistant", "超过最大重试次数，自动退出。")
            return "超过最大重试次数，自动退出。", history, state

        state.loop_count += 1
        if state.loop_count >= MAX_LOOP:
            add_message(history, "assistant", "超过最大循环次数，自动退出。")
            return "超过最大循环次数，自动退出。", history, state

        
        

        if state.waiting_for_user:#处理等待用户输入的情况,拼接上下文
                resume_calling = f"已获得用户输入，当前工作流为workflow_type:{state.resume_context['workflow_type']};当前缺失信息为{state.resume_context['missing_info']};当前用户输入为：{user_input}"
                action = get_model_action(resume_calling, history,state)
                add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id, 
                                                         event_type=action.action_type,
                                                         message=action.message,
                                                         workflow_type=state.workflow_type,
                                                         source="model",
                                                         session_id=state.session_id))
                state.waiting_for_user = False
                state.missing_info = ""
                state.resume_context = {}
        elif len(state.pending_files)!=0:
            multi_tool_result, history, state = _run_multi_file_step(history=history, state=state)
            
            if multi_tool_result.success:
                continue
            else: 
                errorStr = classify_multi_file_error(multi_tool_result)
                if(errorStr=="user_fixable_error"):
                    state.current_file_retry_count = 0
                    state.waiting_for_user = True
                    state.missing_info = _infer_missing_info(state.workflow_type)
                    state.resume_context = {"workflow_type": state.workflow_type, "missing_info": state.missing_info}
                    add_message(history, "assistant", f"文件{state.current_file}发生错误，请提供正确的路径或文件名")
                    return f"文件{state.current_file}发生错误，请提供正确的路径或文件名", history, state
                elif(errorStr=="fatal_error"):
                    add_message(history, "assistant", state.last_tool_result.error_message)
                    state = set_default_state_workflow(state)
                    return state.last_tool_result.error_message, history, state
                elif(errorStr=="retryable_error"):
                    if state.current_file_retry_count<1:
                        state.current_file_retry_count = state.current_file_retry_count+1
                        continue
                    else:
                        errorMsg = state.last_tool_result.error_message
                        add_message(history, "assistant", errorMsg)
                        state = set_default_state_workflow(state)
                        return errorMsg, history, state
        
        elif "summary" in state.workflow_type:
            state.current_file_retry_count=0
            action = get_model_action(user_input="工作流完成，开始总结", history=history, state=state)
            add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id,
                                                        event_type=action.action_type,
                                                        message=action.message,
                                                        workflow_type=state.workflow_type,
                                                        source="model",
                                                        session_id=state.session_id))
        else:    
            action = get_model_action(user_input=user_input, history=history, state=state)
            add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id, 
                                                        event_type=action.action_type,
                                                        message=action.message+"\n"+"tool_name:"+action.tool_name+"\ntool_args:"+str(action.tool_args),
                                                        workflow_type=state.workflow_type,
                                                        source="model",
                                                        session_id=state.session_id))
        #state.workflow_type = action.task_type
        if action.action_type == "respond":
            add_message(history, "assistant", action.message)
            state.workflow_type="idle"
            state.collected_contents={}
            state = set_default_state_workflow(state)
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
            state.collected_contents={}
            state = set_default_state_workflow(state)
            return action.message, history, state

        if action.action_type != "call_tool":
            message = f"未知 action_type: {action.action_type}"
            state.workflow_type="idle"
            add_message(history, "assistant", message)
            state = set_default_state_workflow(state)
            return message, history, state

        if action.message:
            add_message(history, "assistant", action.message)

        if action.tool_name == "list_files":
            # if action.tool_args.get("file_names"):
            #     state.pending_files = list(action.tool_args.get("file_names",[]))#初始化一个新的列表这样可以不依赖别的对象
            #     state.collected_contents = {}
            #     state.completed_files=[]
            #     state.current_file=""
            #     state.workflow_type=action.task_type
            #     continue
            tool_result = list_files(target_dir=action.tool_args.get("target_dir", ""))
        elif action.tool_name == "read_file":
            if action.tool_args.get("file_names"):
                state.pending_files = list(action.tool_args.get("file_names",[]))#初始化一个新的列表这样可以不依赖别的对象
                state.collected_contents = {}
                state.completed_files=[]
                state.current_file=""
                state.workflow_type=action.task_type
                state.current_file_retry_count = 0
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
        state = set_default_state_workflow(state)
        return tool_result.error_message, history, state
