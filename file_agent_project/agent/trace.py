from dataclasses import dataclass

@dataclass
class TraceEvent:
    session_id:str
    turn_id:int
    source: str
    event_type: str
    message: str
    workflow_type: str

def create_trace_buffer():
    return []

def add_trace(trace_list: list[TraceEvent], trace: TraceEvent):
      trace_list.append(trace)

def format_trace(trace:TraceEvent):
     return f"[sessionId]:{trace.session_id}\n[turnId]:{trace.turn_id}\n[source]:{trace.source}\n[eventType]:{trace.event_type}\n[workflowType]: {trace.workflow_type} \n{trace.message}"


def append_trace_log(trace_list:list[TraceEvent], filePath:str):
    with open(filePath, "a", encoding="utf-8") as f:
        for trace in trace_list:
            f.write(format_trace(trace)+"\n")