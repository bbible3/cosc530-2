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
        self.cycle = 1
        self.instruction_queue = []
        self.instruction_queue_index = 0
        
        self.eff_addr_buffer = []
        self.add_buffer = []
        self.mult_buffer = []
        self.ints_buffer = []
        self.reorder_buffer = []
        self.mem_read_buffer = []
        self.write_result_buffer = []

        self.memlocs = {}

        #print("About to check configs...")
        #Before we simulate, make sure we have values from config
        if self.config is None:
            raise Exception("No config provided")
        if self.trace is None:
            raise Exception("No trace provided")
        if self.config.buffers_eff_addr is None:
            raise Exception("No eff addr buffer size provided")
        if self.config.buffers_fp_adds is None:
            raise Exception("No fp adds buffer size provided")
        if self.config.buffers_fp_muls is None:
            raise Exception("No fp muls buffer size provided")
        if self.config.buffers_ints is None:
            raise Exception("No ints buffer size provided")
        if self.config.buffers_reorder is None:
            raise Exception("No reorder buffer size provided")
        if self.config.latencies_fp_add is None:
            raise Exception("No fp add latency provided")
        if self.config.latencies_fp_sub is None:
            raise Exception("No fp sub latency provided")
        if self.config.latencies_fp_mul is None:
            raise Exception("No fp mul latency provided")
        if self.config.latencies_fp_div is None:
            raise Exception("No fp div latency provided")
        
        #print("Configs checked out")
        
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

        #self.show_memlocs()

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
    
    def append_eff_addr_buffer(self, instruction: Instruction):
        #Is there room in the eff addr buffer?
        if len(self.eff_addr_buffer) < self.config.buffers_eff_addr:
            self.eff_addr_buffer.append(instruction)
            return True
        else:
            return False


    def simulate(self):
        print("Starting simulation...")

        #Check buffers for things to execute, or in case we need to stall
        self.docycle_checkbuffers()
        self.docycle_issue()
        self.docycle_finishexecute()
        self.docycle_commit()

       

    def docycle_commit(self):
        #Todo: implement other types of instructions, in-order commits, error checking, etc
        pass

    def docycle_writeback(self):
        for instruction in self.write_result_buffer:
            if instruction.in_writeback_buffer_at == self.cycle:
                self.log.add(LogType.SIM_WRITE_RESULT, f"Instruction in write result buffer finished writing at cycle {self.cycle} ~~~ {instruction.tostr()}")
                instruction.in_writeback_buffer = False
                self.write_result_buffer.remove(instruction)
                
                #We can free up the memlocs used by this instruction
                for memloc in instruction.memlocs:
                    self.log.add(LogType.SIM_FREE_MEMLOC, f"Freeing memloc {memloc.identifier} at cycle {self.cycle}")
                    memloc.used_by = None
                    memloc.using = False

                #Add to reorder buffer
                instruction.in_reorder_buffer = True
                instruction.in_reorder_buffer_at = self.cycle+1

                self.reorder_buffer.append(instruction)
    def docycle_membuffer(self):
        for instruction in self.mem_read_buffer:
            #Need to implement checking to ensure there is not already a read in progress
            if 1==1:
                if instruction.in_mem_at == self.cycle:
                    self.log.add(LogType.MEM_READ, f"Instruction in mem buffer started reading at cycle {self.cycle}, should finish at {instruction.in_mem_at} ~~~ {instruction.tostr()}")
                    #Need to error check here to ensure that we do not move two instructions to write result stage at the same time. Implement later
                    if 1==1:
                        instruction.in_writeback_buffer_at = self.cycle + 1
                        instruction.in_mem_buffer = False
                        self.mem_read_buffer.remove(instruction)
                        instruction.in_writeback_buffer = True
                        self.write_result_buffer.append(instruction)
                        self.log.add(LogType.SIM_MOVE_TO_WRITERESULTBUF, f"Instruction in mem buffer moved to write result buffer at cycle {self.cycle} ~~~ {instruction.tostr()}")



    def docycle_finishexecute(self):
        for instruction in self.eff_addr_buffer:
            if instruction.finished_at == self.cycle:
                instruction.executing = False
                instruction.in_mem_buffer = True
                self.log.add(LogType.FLW_FINISH_EXECUTE, f"Instruction in eff addr buffer finished executing at cycle {self.cycle} ~~~ {instruction.tostr()}")
                self.eff_addr_buffer.remove(instruction)

                #Need to do error checking here to ensure that we do not move two instructions to memory stage at the same time
                if 1==1:
                    instruction.in_mem_at = self.cycle+1
                    self.mem_read_buffer.append(instruction)
                    self.log.add(LogType.SIM_MOVE_TO_MEMBUF, f"Instruction in eff addr buffer moved to mem buffer at cycle {self.cycle} ~~~ {instruction.tostr()}")

    def docycle_checkbuffers(self):
        #Check buffers for things to execute, or in case we need to stall
        #Check eff addr buffer
        for instruction in self.eff_addr_buffer:
            if instruction.execute_at == self.cycle:
                instruction.executing = True
                instruction.finished_at = self.cycle + (self.config.latencies_flw-1)
                #generalise log here
                self.log.add(LogType.FLW_START_EXECUTE, f"Instruction in eff addr buffer started executing at cycle {self.cycle}, should finish at {instruction.finished_at} ~~~ {instruction.tostr()}")

    def docycle_issue(self):
        
        #If we have instructions in the instruction queue, try to issue them
        if self.instruction_queue_index < len(self.instruction_queue):
            #If we have room in the reorder buffer, issue the instruction
            if len(self.reorder_buffer) < self.config.buffers_reorder:
                
                inst = self.instruction_queue[self.instruction_queue_index]
                #Ensure the instruction is valid
                if inst is None:
                    raise Exception(f"Tried to issue instruction on cycle {self.instruction_queue_index}, but instruction is None")
                if inst.instruction_type is None:
                    raise Exception(f"Tried to issue instruction on cycle {self.instruction_queue_index}, but instruction type is None")
                if inst.memlocs is None:
                    raise Exception(f"Tried to issue instruction on cycle {self.instruction_queue_index}, but instruction memlocs is None")
                if inst.issued is not None:
                    raise Exception(f"Tried to issue instruction on cycle {self.instruction_queue_index}, but instruction has already been issued")
                
                #Issue the instruction
                inst.issued = self.cycle
                self.log.add(LogType.SIM_ISSUE_INSTRUCTION, f"Cycle {self.cycle}: Issuing cycle at IQI {self.instruction_queue_index} ~~~ {inst.tostr()}")

                #Is the memory location used by this instruction avaialble?
                for memloc in inst.memlocs:
                    if memloc.using is True:
                        self.log.add(LogType.SIM_ISSUE_INSTRUCTION, f"Hazard: Memloc {memloc.identifier} is not available")
                        #The memory location is not available, so we can't issue this instruction
                        break
                else:
                    #The memory location is available, so we can issue this instruction
                    self.log.add(LogType.SIM_READY_TO_EXECUTE, f"Memloc is available, so we can execute on the next cycle")
                    #Mark the memory location as unavailable
                    for memloc in inst.memlocs:
                        memloc.using = True
                        memloc.usedby = inst
                    
                    #A load instruction will need to be issued to the eff addr buffer
                    if inst.instruction_type.name == "flw":
                        self.log.add(LogType.SIM_APPEND_EFF_ADDR_BUFFER, f"Attempting to add to effective address buffer")
                        #Add to the effective address buffer
                        append_res = self.append_eff_addr_buffer(inst)
                        if append_res is True:
                            self.log.add(LogType.SIM_APPEND_EFF_ADDR_BUFFER, f"Added to effective address buffer")
                            inst.execute_at = self.cycle + 1
                        else:
                            #We should implement code to ensure that we are not loading or storing in this cycle
                            raise Exception(f"Could not add to effective address buffer")

                #Add the instruction to the reorder buffer
                self.reorder_buffer.append(inst)
                self.instruction_queue_index += 1
                self.cycle += 1
                return True
