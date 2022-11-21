from config import Config
from memloc import Memloc 
from tracer import Tracer
from instructiontypes import InstructionTypes, InstructionType, DefaultInstructionTypes
from log import Log, LogType
from instructions import Instruction
class Sim():

    def __init__(self, config: Config, trace: Tracer, instruction_types: InstructionTypes, log: Log):
        self.config = config
        self.trace = trace
        self.instruction_types = instruction_types
        self.log = log
        self.cycle = 0
        self.instruction_queue = []
        self.instruction_queue_index = 0
        
        self.eff_addr_buffer = []
        self.add_buffer = []
        self.mult_buffer = []
        self.ints_buffer = []
        self.reorder_buffer = []

        self.memlocs = {}

        print("About to check configs...")
        #Before we simulate, make sure we have values from config
        if self.config is None:
            raise Exception("No config provided")
        if self.trace is None:
            raise Exception("No trace provided")
        if config.buffers_eff_addr is None:
            raise Exception("No eff addr buffer size provided")
        if config.buffers_fp_adds is None:
            raise Exception("No fp adds buffer size provided")
        if config.buffers_fp_muls is None:
            raise Exception("No fp muls buffer size provided")
        if config.buffers_ints is None:
            raise Exception("No ints buffer size provided")
        if config.buffers_reorder is None:
            raise Exception("No reorder buffer size provided")
        if config.latencies_fp_add is None:
            raise Exception("No fp add latency provided")
        if config.latencies_fp_sub is None:
            raise Exception("No fp sub latency provided")
        if config.latencies_fp_mul is None:
            raise Exception("No fp mul latency provided")
        if config.latencies_fp_div is None:
            raise Exception("No fp div latency provided")
        
        print("Configs checked out")
        
        #Setup memloc objects for all instructions
        for inst in self.trace.instruction_queue:
            params = inst.params
            #What memory locations are used in this instruction?
            for param in params:
                #Does this parameter already exist in the memlocs dict?
                if param in self.memlocs:
                    memloc = self.memlocs[param]
                else:
                    memloc = Memloc(param)
                    self.memlocs[param] = memloc
                memloc.future_usedby.append(inst)
                inst.memlocs.append(memloc)
            self.instruction_queue.append(inst)

        #self.show_instruction_queue()

        self.show_memlocs()

    def show_instruction_queue(self):
        #Output the instruction queue and the associated memlocs
        for item in self.instruction_queue:
            print(item.instruction_type.name)
            memlocs_str = " ".join([str(memloc.identifier) for memloc in item.memlocs])
            print(f"\tMemlocs: {memlocs_str}")
    
    def show_memlocs(self):
        for key,val in self.memlocs.items():
            print(f"Memloc exists: {key}")
            print(f"\tFuture used by: n={len(val.future_usedby)}")

            if len(val.future_usedby) > 1:
                print("\t\tThis memloc is used by multiple instructions. It may cause a hazard.")