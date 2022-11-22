from enum import Enum
class LogType(str, Enum):
    """Log type"""
    CONFIG_READ = "CONFIG_READ"
    TRACE_OPEN = "TRACE_OPEN"
    TRACE_READ_LINE = "TRACE_READ_LINE"
    TRACE_COMMAND_MATCH = "TRACE_COMMAND_MATCH"
    TRACE_COMMAND_PARAM_EXTRACT = "TRACE_COMMAND_PARAM_EXTRACT"
    TRACE_COMMAND_QUEUE_ADD = "TRACE_COMMAND_QUEUE_ADD"
    SIM_ISSUE_INSTRUCTION = "SIM_ISSUE_INSTRUCTION"
    SIM_READY_TO_EXECUTE = "SIM_READY_TO_EXECUTE"
    SIM_APPEND_EFF_ADDR_BUFFER = "SIM_APPEND_EFF_ADDR_BUFFER"
    FLW_START_EXECUTE = "FLW_START_EXECUTE"
    FLW_FINISH_EXECUTE = "FLW_FINISH_EXECUTE"
    SIM_MOVE_TO_MEMBUF = "FLW_MOVE_TO_MEMBUF"
    SIM_MEM_READ = "SIM_MEM_READ"
    SIM_MOVE_TO_WRITERESULTBUF = "SIM_MOVE_TO_WRITERESULTBUF"
    SIM_WRITE_RESULT = "SIM_WRITE_RESULT"
    SIM_FREE_MEMLOC = "SIM_FREE_MEMLOC"
class LogItem:
    def __init__(self, log_type: LogType, message: str):
        self.log_type = log_type
        self.message = message
    def print(self):
        print(f"[{self.log_type}] {self.message}")

class Log:
    def __init__(self):
       self.items = []
    def add(self, log_type: LogType, message: str):
        self.items.append(LogItem(log_type, message))
    def print(self):
        for item in self.items:
            item.print()
