#用来恢复现场
from common.dict.dict_consumer import set_nested_value
from core.schemas import AgentState, ResumeContext


def resume_from_context(resume_context:ResumeContext, processed_field:dict)->dict:
    resume_action = {}
    resume_action["tool_name"] = resume_context.pending_action["tool_name"]
    resume_action["tool_args"] = resume_context.pending_action["tool_args"]
    #todo:补充恢复信息
    for key in resume_context.resume_patch["fields"].keys():
        set_nested_value(resume_action,
                         resume_context.resume_patch["fields"][key],
                         processed_field[key])
        #路径
    #ToDo:工作流的还没恢复
    return resume_action