from core.constants import WORKSPACE_ROOT

def resolve_workpath(file_name: str)->str:
    return WORKSPACE_ROOT+'/n'+file_name