from instructiontypes import InstructionTypes, InstructionType, DefaultInstructionTypes
class Instruction:
    def __init__(self, instruction_type: InstructionType, params: list):
        self.instruction_type = instruction_type
        self.params = params
        self.memlocs = []
        
        self.issued = None
        self.executing = False
        self.in_mem_buffer = False
        self.in_writeback_buffer = False
        self.in_reorder_buffer = False

        self.execute_at = None
        self.finished_at = None
        self.in_mem_at = None
        self.in_writeback_buffer_at = None
        self.in_reorder_buffer_at = None
        self.last_execute_attempt = None

        self.wrote_at = None
    def print(self):
        print(f"[{self.instruction_type.instruction_class}] {self.instruction_type.name} {self.params}")
    def tostr(self):
        return f"[{self.instruction_type.instruction_class}] {self.instruction_type.name} {self.params}"