from instructiontypes import InstructionTypes, InstructionType, DefaultInstructionTypes
class Instruction:
    def __init__(self, instruction_type: InstructionType, params: list):
        self.instruction_type = instruction_type
        self.params = params
        self.memlocs = []
    def print(self):
        print(f"[{self.instruction_type.instruction_class}] {self.instruction_type.name} {self.params}")