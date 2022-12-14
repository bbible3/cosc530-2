from enum import Enum
class InstructionClass(str, Enum):
    DATA_TRANSFERS = "DATA_TRANSFERS"
    ARITHMETIC = "ARITHMETIC"
    CONTROL = "CONTROL"
    FLOATING_POINT = "FLOATING_POINT"
class InstructionType:
    def __init__(self, instruction_class: InstructionClass, name: str, description="No Description", num_params:int=-1, uses_memory:bool=False, latency:int=1):
        self.instruction_class = instruction_class
        self.name = name
        self.description = ""
        self.num_params = num_params
        self.uses_memory = uses_memory
        self.latency = latency
    def print(self):
        print(f"[{self.instruction_class}] {self.name}")

class InstructionTypes:
    def __init__(self):
        self.types = []
    def add(self, instruction_class: InstructionClass, name: str, description="No Description", num_params:int=-1, uses_memory=False, latency:int=1):
        self.types.append(InstructionType(instruction_class, name, description=description, num_params=num_params, uses_memory=uses_memory, latency=latency))
    def find(self, name: str):
        for type in self.types:
            if type.name == name:
                return type
        return None
    def print(self):
        print("Instruction Types:")
        for type in self.types:
            type.print()
class DefaultInstructionTypes:
    def default_instruction_types(config=None):
        
        if config is not None:
            instruction_types = InstructionTypes()
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "lw", description="Load Word", num_params=2, uses_memory=True, latency=1)
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "flw", description="Floating Point Load Word", num_params=2, uses_memory=True, latency=1)
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "sw", description="Store Word", uses_memory=True, num_params=2, latency=1)
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "fsw", description="Floating Point Store Word", num_params=2, uses_memory=True, latency=1)
            instruction_types.add(InstructionClass.ARITHMETIC, "add", description="Add", num_params=3)
            instruction_types.add(InstructionClass.ARITHMETIC, "sub", description="Subtract", num_params=3)
            instruction_types.add(InstructionClass.CONTROL, "beq", description="Branch if Equal", num_params=3)
            instruction_types.add(InstructionClass.CONTROL, "bne", description="Branch if Not Equal", num_params=3)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fadd.s", description="Floating Point Add Single", num_params=3, latency=config.latencies_fp_add)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fsub.s", description="Floating Point Subtract Single", num_params=3, latency=config.latencies_fp_sub)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fmul.s", description="Floating Point Multiply Single", num_params=3, latency=config.latencies_fp_mul)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fdiv.s", description="Floating Point Divide Single", num_params=3, latency=config.latencies_fp_div)
        else:
            instruction_types = InstructionTypes()
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "lw", description="Load Word", num_params=2, uses_memory=True, latency=1)
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "flw", description="Floating Point Load Word", num_params=2, uses_memory=True, latency=1)
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "sw", description="Store Word", uses_memory=True, num_params=2, latency=1)
            instruction_types.add(InstructionClass.DATA_TRANSFERS, "fsw", description="Floating Point Store Word", num_params=2, uses_memory=True, latency=1)
            instruction_types.add(InstructionClass.ARITHMETIC, "add", description="Add", num_params=3)
            instruction_types.add(InstructionClass.ARITHMETIC, "sub", description="Subtract", num_params=3)
            instruction_types.add(InstructionClass.CONTROL, "beq", description="Branch if Equal", num_params=3)
            instruction_types.add(InstructionClass.CONTROL, "bne", description="Branch if Not Equal", num_params=3)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fadd.s", description="Floating Point Add Single", num_params=3, latency=2)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fsub.s", description="Floating Point Subtract Single", num_params=3, latency=2)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fmul.s", description="Floating Point Multiply Single", num_params=3, latency=5)
            instruction_types.add(InstructionClass.FLOATING_POINT, "fdiv.s", description="Floating Point Divide Single", num_params=3, latency=10)
      
        return instruction_types
            