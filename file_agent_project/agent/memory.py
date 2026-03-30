# user_record = {
#     "type": "message",
#     "role": "user",
#     "content": "default content" 
# }
# tool_record = {
#     "tool_name": "default_tool_name",
#     "tool_result" :"default_tool_result",
#     "success": True,
#     "content" : "default_content"
# }
# assistant_recore = {                  
#     "type": "message",
#     "role": "assistant",
#     "content": "default content" 
# }


def create_memory():
    return []

def add_message(memory, role, content):
    memory.append({"role": role, "content": content, "type": "message"})

def add_tool_result(memory: list, tool_name, content, success):
    memory.append({"type":"tool_result","tool_name":tool_name,"content":content,"success":success})

def get_recent_memory(memory, limit=3):
    return memory[-limit:]