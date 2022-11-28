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
    SIM_ENTER_CYCLE = "SIM_ENTER_CYCLE"
    SIM_CHECK_EXECUTE = "SIM_CHECK_EXECUTE"
    SIM_START_EXECUTE = "SIM_START_EXECUTE"
    SIM_CONTINUE_EXECUTE = "SIM_CONTINUE_EXECUTE"
    SIM_DELAY_EXECUTE = "SIM_DELAY_EXECUTE"
    SIM_FINISH_EXECUTE = "SIM_FINISH_EXECUTE"
    FLW_START_EXECUTE = "FLW_START_EXECUTE"
    FLW_FINISH_EXECUTE = "FLW_FINISH_EXECUTE"
    SIM_MOVE_TO_MEMBUF = "FLW_MOVE_TO_MEMBUF"
    SIM_MEM_READ = "SIM_MEM_READ"
    SIM_MEM_READ_MISMATCH = "SIM_MEM_READ_MISMATCH"
    SIM_MOVE_TO_WRITERESULTBUF = "SIM_MOVE_TO_WRITERESULTBUF"
    SIM_WRITE_RESULT = "SIM_WRITE_RESULT"
    SIM_FREE_MEMLOC = "SIM_FREE_MEMLOC"
    SIM_RETRY_EXECUTE_INSTRUCTION = "SIM_RETRY_EXECUTE_INSTRUCTION"
    SIM_RETRY_EXECUTE_INSTRUCTION_NO_MEM = "SIM_RETRY_EXECUTE_INSTRUCTION_NO_MEM"
    SIM_RETRY_EXECUTE_INSTRUCTION_MEM = "SIM_RETRY_EXECUTE_INSTRUCTION_MEM"
    SIM_OUTOFORDER_COMMIT_STALL = "SIM_OUTOFORDER_COMMIT_STALL"
    SIM_COMMIT_SUCCESS = "SIM_COMMIT_SUCCESS"
    SIM_ALREADY_EXECUTING = "SIM_ALREADY_EXECUTING"
    SIM_DOES_NOT_USE_MEM = "SIM_DOES_NOT_USE_MEM"
    SIM_COMMIT_TOO_EARLY = "SIM_COMMIT_TOO_EARLY"
    SIM_LAST_EXECUTE_ATTEMPT_ERROR = "SIM_LAST_EXECUTE_ATTEMPT_ERROR"
    SIM_APPEND_RETRY_FIRST = "SIM_APPEND_RETRY_FIRST"
    SIM_CHECK_COMMIT = "SIM_CHECK_COMMIT"
class LogItem:
    def __init__(self, log_type: LogType, message: str):
        self.log_type = log_type
        self.message = message
        self.instr_id = None
    def print(self):
        print(f"[{self.log_type}] {self.message} (instr_id={self.instr_id})")

class Log:
    def __init__(self):
       self.items = []
       self.instructions = {}
    def add(self, log_type: LogType, message: str, assoc_instr = None):
        self.items.append(LogItem(log_type, message))
        if assoc_instr is not None:
            self.items[-1].instr_id = assoc_instr.instr_id
            self.instructions[assoc_instr.instr_id] = assoc_instr
    def print(self):
        for item in self.items:
            item.print()
    def print_id(self, instr_id: int):
        for item in self.items:
            if item.instr_id == instr_id:
                item.print()
    def print_type(self, *log_type: LogType):
        for item in self.items:
            if item.log_type in log_type:
                item.print()
    def count_instr(self):
        n = 0
        encountered_instr_ids = []
        for item in self.items:
            if item.instr_id not in encountered_instr_ids:
                n += 1
                encountered_instr_ids.append(item.instr_id)
        return n
    def list_instr_ids(self):
        instr_ids = []
        for item in self.items:
            if item.instr_id not in instr_ids and item.instr_id is not None:
                instr_ids.append(item.instr_id)
        return instr_ids
    def get_instr_by_id(self, instr_id: int):
        return self.instructions[instr_id]
    def print_table(self):

        output = ""
        pipeline_simulation_str = "Pipeline Simulation"
        dashbar = "-----------------------------------------------------------"

        #Pad the pipeline simulation string so that it is centered
        output += pipeline_simulation_str.center(len(dashbar))
        output += "\n"
        output += dashbar

        output += "\n"

        table_headers = ["Instruction", "Issues", "Executes", "Read", "Result", "Commits"]
        table_subbars = "--------------------- ------ -------- ------ ------ -------".split(" ")

        tp_str = ""
        pad_first_tp = len("--------------------- ------ -------- ")
        tp_str += " " * pad_first_tp
        tp_str += "Memory Writes"

        th_str = ""
        ts_str = ""
        for i in range(0,6):
            extra = 0
            if i > 0 and i < 5:
                extra = 1
            if i == 5:
                extra = 2
            th_str += table_headers[i].center(len(table_subbars[i])+extra, " ")
            ts_str += table_subbars[i]
            ts_str += " "

        output += tp_str
        output += "\n"
        output += th_str
        output += "\n"
        output += ts_str
        output += "\n"

        instr_ids = self.list_instr_ids()
        for instr_id in instr_ids:
            
            instr = self.get_instr_by_id(instr_id)
            
            memory_read_int = ""
            if instr.in_mem_at is not None:
                memory_read_int = str(instr.in_mem_at) if instr.in_mem_at != -1 else ""
            if instr.instruction_type.uses_memory == False:
                memory_read_int = ""
            issued_str = str(instr.issued_at) if instr.issued_at is not None else "?"
            execute_start_str = str(instr.execute_at) if instr.execute_at is not None else "?"
            execute_end_str = str(instr.finished_at) if instr.finished_at is not None else "?"
            memory_read_str = str(memory_read_int) if memory_read_int is not None else "?"
            writes_result_str = str(instr.wrote_at) if instr.wrote_at is not None else "?"
            commits_str = str(instr.committed_at) if instr.committed_at is not None else "?"

            this_line = f"{instr.instruction_type.name.ljust(6)} {','.join(instr.params).ljust(14)} {issued_str.rjust(6)} {execute_start_str.rjust(2)} - {execute_end_str.rjust(2)} {memory_read_str.rjust(6)} {writes_result_str.rjust(6)} {commits_str.rjust(7)}"
            output += this_line 
            output += "\n"
        print(output)