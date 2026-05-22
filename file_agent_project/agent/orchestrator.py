from agent.memory import add_message, add_tool_result
from agent.model import get_model_action
from core.constants import MAX_LOOP
from core.schemas import AgentState, ToolResult,Action,ResumeContext,ToolError
from tool_layer.errors import PlatErrorCategory, ToolErrorCode
from agent.trace import TraceEvent,add_trace
from agent.state import set_default_state_workflow
from recovery.recovery_decision import create_recovery_decision,RecoveryAction
from common.dict.dict_consumer import get_nested_value,set_nested_value
from tool_layer.specs import ToolSpec, FieldIssue
from agent.decision import decide_next_step
from execute.execute_layer import call_execute


#消费工具调用结果
def consume_tool_result(tool_result:ToolResult)->str:
    if tool_result.success:
        return "continue"

# def consume_tool_result(state:AgentState, tool_result:ToolResult,history):
#     state.last_tool_name = tool_result.tool_name
#     state.last_tool_result = tool_result

#     observation = tool_result.content if tool_result.success else tool_result.error_message
#     add_tool_result(
#         history,
#         tool_result.tool_name,
#         observation,
#         tool_result.success
#     )

#     if tool_result.success:
#         return "continue_loop", None
    
#     if tool_result.error is not None:
#         recovery_decision =  create_recovery_decision(tool_error=tool_result.error)
#         if recovery_decision.action == RecoveryAction.ASK_USER:
#             # state.resume_context = build_resume_context(state, "action_patch",recovery_decision.missing_info,None, get_tool_action_template(action.tool_name),recovery_decision.resume_patch)
#             # state.missing_info = recovery_decision.missing_info
#             # # state.missing_info = recovery_decision.missing_info
#             # # state.resume_context.workflow_type = state.workflow_type
#             # # state.resume_context.missing_info = state.missing_info
#             # # state.resume_context.pending_action = recovery_decision.action
#             # # state.resume_context.resume_kind = "action_patch"
#             # # state.resume_context.resume_patch = recovery_decision.resume_patch
#             # state.waiting_for_user = True
#             return "ask_user", recovery_decision
#             #return recovery_decision.user_message, history, state
#         else:
#         #state.retry_count += 1
#             state = set_default_state_workflow(state)
#             return "error", recovery_decision
#     #return tool_result.error_message, history, state
#     else:
#         raise ValueError("consume tool result error")


def save_recovery_info(state, tool_name, resume_kind, recovery_decision):
      state.waiting_for_user = True
      state.missing_info = recovery_decision.missing_info
      state.resume_context = build_resume_context(
          state=state,
          resume_kind=resume_kind,
          missing_info=recovery_decision.missing_info,
          pending_action=get_tool_action_template(tool_name),
          resume_patch=recovery_decision.resume_patch
      )
      return state, recovery_decision.user_message

# #用来恢复现场
# def resume_from_context(state:AgentState, processed_field:dict)->dict:
#     resume_action = {}
#     resume_action["tool_name"] = state.resume_context.pending_action["tool_name"]
#     resume_action["tool_args"] = state.resume_context.pending_action["tool_args"]
#     #todo:补充恢复信息
#     for key in state.resume_context.resume_patch["fields"].keys():
#         set_nested_value(resume_action,
#                          state.resume_context.resume_patch["fields"][key],
#                          processed_field[key])
#         #路径
#     return resume_action


#工具现场恢复函数，后续改成工具注册中心，提供工具相关信息
def get_tool_action_template(tool_name: str) -> dict:
    if(tool_name=="read_file"):
        return {"tool_name":"read_file","tool_args":{"file_name": ""}}
    elif(tool_name=="list_files"):
        return {"tool_name":"list_files","tool_args":{"target_dir":""}}

#统一将action中的状态转移到state中
def action_to_state(state:AgentState, action:Action):
    #针对工作流特化
    # if action.task_type == "multi_file_summary":
        
    # elif action.task_type in ["single_file_summary","single_file_read"]:
    #     file_name = action.tool_args.get("file_name", "")
    #     state.current_file = file_name
    #     state.workflow_type=action.task_type
    # else:
    #     state.workflow_type="idle"
    # return state
    #先对模型返回的action进行合法化监测
    if(action.task_type in ["multi_file_summary","single_file_read","single_file_summary"]):
        state.workflow_type = action.task_type
    return state

def build_resume_context(
      state: AgentState,
      resume_kind: str,
      missing_info: str,
      failed_target: str | None = None,
      pending_action: dict | None = None,
      resume_patch: dict | None = None
  ) -> ResumeContext:
    return ResumeContext(workflow_type=state.workflow_type,
                         missing_info=missing_info,
                         resume_kind=resume_kind,
                         repair_target=failed_target,
                         pending_action=pending_action,
                         resume_patch=resume_patch)

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
# def _run_multi_file_step(history, state:AgentState):
#     if len(state.pending_files)==0:
#         return ToolResult("","",True, ""), history, state
#     else:     
#         state.current_file = state.pending_files[0]
#         add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id, 
#                                                      message=f"orchestrator正在消费文件:{state.current_file}",
#                                                      workflow_type=state.workflow_type,
#                                                      source="orchestrator",
#                                                      session_id=state.session_id,
#                                                      event_type="queue_consume"))
#         tool_result = read_file(state.current_file)
#         if tool_result.success:
#             state.collected_contents[state.current_file]=tool_result.content
#             state.pending_files.pop(0)
#             state.completed_files.append(state.current_file)
#             state.last_tool_name = "read_file"
#             state.last_tool_result = tool_result
#             state.current_file_retry_count = 0
#             add_tool_result(history, "read_file", tool_result.content, tool_result.success)
            
#         else:
#             state.last_tool_name = "read_file"
#             state.last_tool_result = tool_result
#             # state.resume_context=build_resume_context(state=state, resume_kind="workflow_repair", missing_info="file_name",failed_target=state.current_file)
#             add_tool_result(history, "read_file", tool_result.error_message, tool_result.success)
#     return tool_result, history, state



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

    while state.loop_count<MAX_LOOP:


        #decisionLayer根据用户输入做决定
        decision = decide_next_step(state=state, user_input=user_input, history=history)
        print(f"[ORCH] loop={state.loop_count}, next_action={decision.next_action}, tool_name={decision.tool_name}")
        if decision.record_message == True:
            add_message(history, "assistant", decision.assistant_message)

        if decision.next_action == "call_tool":
            tool_result = call_execute(decision.tool_name, decision.tool_args)

            # 无论成功失败，都记录到 history
            observation = tool_result.content if tool_result.success else tool_result.error_message
            add_tool_result(history, decision.tool_name, observation, tool_result.success)

            if not tool_result.success:
                return f"工具失败: {tool_result.error_message}", history, state

            user_input = ""
            state.loop_count+=1
            continue
        if decision.next_action in ("respond", "finish"):
            # respond: 普通回复，用户可能继续对话
            # finish: 任务结束，本轮对话终结
            # 当前行为相同，后续可按需拆分
            state.loop_count = 0
            return decision.assistant_message, history, state
        if decision.next_action == "ask_user":
            #如果按照这样的恢复
            state.waiting_for_user = True
            
            return decision.assistant_message, history, state
        
















    # #state.current_intent = _infer_intent(user_input)

    # add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id,
    #                                               event_type="turn_start",
    #                                               message="这轮对话开始",
    #                                               workflow_type=state.workflow_type,
    #                                               source="orchestrator",
    #                                               session_id=state.session_id))

    # while True:
    #     if state.retry_count > 3:
    #         add_message(history, "assistant", "超过最大重试次数，自动退出。")
    #         return "超过最大重试次数，自动退出。", history, state

    #     state.loop_count += 1
    #     if state.loop_count >= MAX_LOOP:
    #         add_message(history, "assistant", "超过最大循环次数，自动退出。")
    #         return "超过最大循环次数，自动退出。", history, state

        
        

    #     if state.waiting_for_user and state.resume_context is not None:#处理等待用户输入的情况,拼接上下文
    #             resume_calling = f"已获得用户输入，当前工作流为workflow_type:{state.resume_context.workflow_type};当前缺失信息为{state.resume_context.missing_info};当前用户输入为：{user_input}"
    #             # add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id, 
    #             #                                          event_type=action.action_type,
    #             #                                          message=action.message,
    #             #                                          workflow_type=state.workflow_type,
    #             #                                          source="model",
    #             #                                          session_id=state.session_id))
    #             #恢复现场
    #             if(state.resume_context.resume_kind=="action_patch"):
    #                 processed_field = {}#用来存放恢复信息，怎么获得todo，应该是要调用模型
    #                 processed_field = {
    #                     state.resume_context.missing_info: user_input
    #                 }
    #                 resume_action = resume_from_context(state, processed_field)
    #                 #Todo: 用resume_action来调用工具
    #                 resume_tool_result = execute_tool_call(resume_action["tool_name"], resume_action["tool_args"])
    #                 resume_tag, zwf = consume_tool_result(state, resume_tool_result, history)
    #                 if resume_tag == "continue_loop":
    #                     state.waiting_for_user = False
    #                     state.missing_info = ""
    #                     state.resume_context = None
    #                     continue
    #                 elif resume_tag == "ask_user":
    #                     state, msg = save_recovery_info(state, resume_action["tool_name"],"ask_user",zwf)
    #                     return msg,history,state
    #                 elif resume_tag=="error":
    #                     return "工具调用发生错误", history ,state
    #             # state.waiting_for_user = False
    #             # state.missing_info = ""
    #             # state.resume_context = None
    #     if len(state.pending_files)!=0:
    #         multi_tool_result, history, state = _run_multi_file_step(history=history, state=state)
            
    #         if multi_tool_result.success:
    #             continue
    #         else: 
    #             errorStr = classify_multi_file_error(multi_tool_result)
    #             if(errorStr=="user_fixable_error"):
    #                 state.current_file_retry_count = 0
    #                 state.waiting_for_user = True
    #                 state.missing_info = _infer_missing_info(state.workflow_type)
    #                 state.resume_context = build_resume_context(state=state, resume_kind="workflow_repair", missing_info="file_name",failed_target=state.current_file)
    #                 return f"文件{state.current_file}发生错误，请提供正确的路径或文件名", history, state
    #             elif(errorStr=="fatal_error"):
    #                 add_message(history, "assistant", state.last_tool_result.error_message)
    #                 state = set_default_state_workflow(state)
    #                 return state.last_tool_result.error_message, history, state
    #             elif(errorStr=="retryable_error"):
    #                 if state.current_file_retry_count<1:
    #                     state.current_file_retry_count = state.current_file_retry_count+1
    #                     continue
    #                 else:
    #                     errorMsg = state.last_tool_result.error_message
    #                     add_message(history, "assistant", errorMsg)
    #                     state = set_default_state_workflow(state)
    #                     return errorMsg, history, state
        
    #     elif "summary" in state.workflow_type:
            
    #         action = get_model_action(user_input="工作流完成，开始总结", history=history, state=state)
    #         add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id,
    #                                                     event_type=action.action_type,
    #                                                     message=action.message,
    #                                                     workflow_type=state.workflow_type,
    #                                                     source="model",
    #                                                     session_id=state.session_id))
    #     else:    
    #         action = get_model_action(user_input=user_input, history=history, state=state)
    #         add_trace(state.trace_events, TraceEvent(turn_id=state.turn_id, 
    #                                                     event_type=action.action_type,
    #                                                     message=action.message+"\n"+"tool_name:"+action.tool_name+"\ntool_args:"+str(action.tool_args),
    #                                                     workflow_type=state.workflow_type,
    #                                                     source="model",
    #                                                     session_id=state.session_id))
            

    #     #对action中的值进行统一赋值
    #     state = action_to_state(state=state, action=action)


    #     #消费action
    #     if action.action_type == "respond":
    #         add_message(history, "assistant", action.message)
    #         #state.workflow_type="idle"
    #         #state.collected_contents={}
    #         state = set_default_state_workflow(state)
    #         return action.message, history, state

    #     if action.action_type == "ask_user":
    #         state.waiting_for_user = True
    #         state.missing_info = _infer_missing_info(state.workflow_type)
    #         state.resume_context = build_resume_context(state=state, resume_kind="action_patch", missing_info=state.missing_info,pending_action=get_tool_action_template(state.last_tool_name))
    #         add_message(history, "assistant", action.message)
    #         return action.message, history, state

    #     if action.action_type == "finish":
    #         add_message(history, "assistant", action.message)
    #         #state.workflow_type="idle"
    #         #state.collected_contents={}
    #         state = set_default_state_workflow(state)
    #         return action.message, history, state

    #     if action.action_type != "call_tool":
    #         message = f"未知 action_type: {action.action_type}"
    #         #state.workflow_type="idle"
    #         add_message(history, "assistant", message)
    #         state = set_default_state_workflow(state)
    #         return message, history, state

    #     if action.message:
    #         add_message(history, "assistant", action.message)

    #     if action.tool_name == "list_files":
    #         # if action.tool_args.get("file_names"):
    #         #     state.pending_files = list(action.tool_args.get("file_names",[]))#初始化一个新的列表这样可以不依赖别的对象
    #         #     state.collected_contents = {}
    #         #     state.completed_files=[]
    #         #     state.current_file=""
    #         #     state.workflow_type=action.task_type
    #         #     continue
    #         tool_result = list_files(target_dir=action.tool_args.get("target_dir", ""))
    #     elif action.tool_name == "read_file":
    #         if state.workflow_type=="multi_file_summary":
    #             state.pending_files = list(action.tool_args.get("file_names",[]))#初始化一个新的列表这样可以不依赖别的对象
    #             state.collected_contents = {}
    #             state.completed_files=[]
    #             state.current_file=""
    #             state.workflow_type=action.task_type
    #             state.current_file_retry_count = 0
    #             continue
    #         else:
    #             tool_result = execute_tool_call(action.tool_name, action.tool_args)
                
    #     else:
    #         tool_result = _build_tool_error(
    #             action.tool_name,
    #             f"未知工具: {action.tool_name}",
    #         )
    #     next_step,recovery_info = consume_tool_result(state, tool_result, history)
    #     if next_step == "continue_loop":
    #         continue
    #     elif next_step =="ask_user":
    #         state, ret_msg = save_recovery_info(state, action.tool_name,"ask_user", recovery_info)
    #         return ret_msg,history,state
    #     elif next_step == "error":
    #         return recovery_info.user_message, history, state
    #     # state.last_tool_name = tool_result.tool_name
    #     # state.last_tool_result = tool_result

    #     # observation = tool_result.content if tool_result.success else tool_result.error_message
    #     # add_tool_result(
    #     #     history,
    #     #     tool_result.tool_name,
    #     #     observation,
    #     #     tool_result.success
    #     # )

    #     # if tool_result.success:
    #     #     continue
        
    #     # if tool_result.error is not None:
    #     #     recovery_decision =  create_recovery_decision(tool_error=tool_result.error)
    #     #     if recovery_decision.action == RecoveryAction.ASK_USER:
    #     #         state.resume_context = build_resume_context(state, "action_patch",recovery_decision.missing_info,None, get_tool_action_template(action.tool_name),recovery_decision.resume_patch)
    #     #         state.missing_info = recovery_decision.missing_info
    #     #         # state.missing_info = recovery_decision.missing_info
    #     #         # state.resume_context.workflow_type = state.workflow_type
    #     #         # state.resume_context.missing_info = state.missing_info
    #     #         # state.resume_context.pending_action = recovery_decision.action
    #     #         # state.resume_context.resume_kind = "action_patch"
    #     #         # state.resume_context.resume_patch = recovery_decision.resume_patch
    #     #         state.waiting_for_user = True
    #     #         return recovery_decision.user_message, history, state

    #     # state.retry_count += 1
    #     # state = set_default_state_workflow(state)
    #     # return tool_result.error_message, history, state
