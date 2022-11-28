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
        self.execute_buffer = []
        self.memlocs = {}

        self.read_write_this_cycle = False

        self.most_recent_commit = None

        #print("About to check configs...")
        # Before we simulate, make sure we have values from config
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

        # Setup memloc objects for all instructions
        for inst in self.trace.instruction_queue:
            params = inst.params
            # What memory locations are used in this instruction?
            for param in params:
                # Does this parameter already exist in the memlocs dict?
                if param in self.memlocs:
                    memloc = self.memlocs[param]
                else:
                    #print(f"Creating new memloc for {param}")
                    memloc = Memloc(param)
                    self.memlocs[param] = memloc
                memloc.future_usedby.append(inst)
                inst.memlocs.append(memloc)
            self.instruction_queue.append(inst)

        # self.show_instruction_queue()

        # self.show_memlocs()

    def show_instruction_queue(self):
        # Output the instruction queue and the associated memlocs
        for item in self.instruction_queue:
            print(item.instruction_type.name)
            memlocs_str = " ".join([str(memloc.identifier)
                                   for memloc in item.memlocs])
            print(f"\tMemlocs: {memlocs_str}")

    def show_memlocs(self):
        for key, val in self.memlocs.items():
            print(f"Memloc exists: {key}")
            print(f"\tFuture used by: n={len(val.future_usedby)}")

            if len(val.future_usedby) > 1:
                print(
                    "\t\tThis memloc is used by multiple instructions. It may cause a hazard.")

    def append_eff_addr_buffer(self, instruction: Instruction):
        # Is there room in the eff addr buffer?
        if len(self.eff_addr_buffer) < self.config.buffers_eff_addr:
            self.eff_addr_buffer.append(instruction)
            return True
        else:
            return False

    def get_memloc(self, identifier):
        return self.memlocs[identifier]

    def simulate(self):
        print("Starting simulation...")
        self.log.add(LogType.SIM_ENTER_CYCLE, f"Starting cycle {self.cycle}")
        # Check buffers for things to execute, or in case we need to stall
        self.issue()
        self.execute()
        self.memread()
        self.writeresult()
        self.commit()
        self.cycle += 1

    def issue(self):

        if self.instruction_queue_index >= len(self.instruction_queue):
            # No more instructions to issue
            return False

        # Issue the instruction
        instruction = self.instruction_queue[self.instruction_queue_index]
        instruction.execute_at = self.cycle+1
        instruction.issued_at = self.cycle
        self.instruction_queue_index += 1
        self.execute_buffer.append(instruction)
        self.log.add(LogType.SIM_ISSUE_INSTRUCTION,
                     f"(Cycle {self.cycle}) Issued instruction {instruction.tostr()}", assoc_instr=instruction)
        return True

    def execute(self):
        is_mem_good = True
        self.read_write_this_cycle = False
        for instr in self.execute_buffer:
            if instr.execute_at > self.cycle:
                # We can't execute this instruction yet
                continue
            if self.read_write_this_cycle and self.read_write_this_cycle != instr:
                # We already read or wrote this cycle, so we can't do another
                instr.execute_at += 1
                self.log.add(LogType.SIM_DELAY_EXECUTE, f"(Cycle {self.cycle}) Delaying instruction {instr.tostr()} due to memory read/write", assoc_instr=instr)
                continue
            self.log.add(LogType.SIM_CHECK_EXECUTE,
                         f"(Cycle {self.cycle}) Checking instruction {instr.tostr()} for execution", assoc_instr=instr)
            for memloc in instr.memlocs:
                usedby_notme = []
                for usedby in memloc.used_by:
                    if usedby != instr:
                        usedby_notme.append(usedby)
                if len(usedby_notme) > 0:
                    self.log.add(
                        LogType.SIM_CHECK_EXECUTE, f"\tMemloc {memloc.identifier} is used by {len(usedby_notme)} other instructions. Cannot execute yet.", assoc_instr=instr)
                    is_mem_good = False
                    instr.execute_at += 1
                if memloc.data_available == False:
                    self.log.add(
                        LogType.SIM_CHECK_EXECUTE, f"\tMemloc {memloc.identifier} has no data available. Cannot execute yet.", assoc_instr=instr)
                    is_mem_good = False
                    instr.execute_at += 1

            # All memlocs are good to go
            if is_mem_good == True:

                instr.executing = True
                if instr.finished_at is None:
                    instr.finished_at = self.cycle + instr.instruction_type.latency - 1

                if instr.instruction_type.uses_memory == True:
                    self.read_write_this_cycle = instr

                self.log.add(
                    LogType.SIM_START_EXECUTE, f"(Cycle {self.cycle}) Starting Executing instruction {instr.tostr()}, should finish at {instr.finished_at}", assoc_instr=instr)
                for memloc in instr.memlocs:
                    memloc.executing = True
                    memloc.used_by.append(instr)
                if self.cycle > instr.execute_at and self.cycle < instr.finished_at:
                    self.log.add(LogType.SIM_CONTINUE_EXECUTE,
                                 f"(Cycle {self.cycle}) Executing instruction {instr.tostr()}", assoc_instr=instr)
                if self.cycle == instr.finished_at:
                    if instr.instruction_type.uses_memory == True:
                        self.read_write_this_cycle = False
                    self.log.add(LogType.SIM_FINISH_EXECUTE,
                                 f"(Cycle {self.cycle}) Finished Executing instruction {instr.tostr()}", assoc_instr=instr)
                    # for memloc in instr.memlocs:
                    #     memloc.executing = False
                    #     memloc.used_by = []
                    instr.executing = False
                    self.execute_buffer.remove(instr)
                    if instr.instruction_type.uses_memory == True:
                        self.mem_read_buffer.append(instr)
                    else:
                        instr.in_mem_at = self.cycle
                        instr.wrote_at = self.cycle+1
                        self.write_result_buffer.append(instr)
    
    def memread(self):
        if len(self.mem_read_buffer) > 0:
            instr = self.mem_read_buffer[0]
            if instr.finished_at == self.cycle-1:
                self.log.add(LogType.SIM_MEM_READ,
                             f"(Cycle {self.cycle}) Reading memory for instruction {instr.tostr()}", assoc_instr=instr)
                self.mem_read_buffer.remove(instr)
                instr.in_mem_at = self.cycle
                self.write_result_buffer.append(instr)

    def writeresult(self):
        if len(self.write_result_buffer) > 0:
            instr = self.write_result_buffer[0]
            if instr.in_mem_at == self.cycle-1:
                self.log.add(LogType.SIM_WRITE_RESULT,
                             f"(Cycle {self.cycle}) Writing result for instruction {instr.tostr()}", assoc_instr=instr)
                self.write_result_buffer.remove(instr)
                self.reorder_buffer.append(instr)
                instr.wrote_at = self.cycle
                for memloc in instr.memlocs:
                    self.log.add(LogType.SIM_FREE_MEMLOC, f"\tFreeing memloc {memloc.identifier}", assoc_instr=instr)
                    memloc.used_by = []
                    memloc.executing = False
                    memloc.data_available = True
                
    def commit(self):
        if len(self.reorder_buffer) > 0:
                self.log.add(LogType.SIM_CHECK_COMMIT,
                                f"(Cycle {self.cycle}) Checking about committing instructions")
                
                reorder_buffer_sorted = sorted(self.reorder_buffer, key=lambda x: x.issued_at)
                for i in range(len(reorder_buffer_sorted)):
                    if reorder_buffer_sorted[i].wrote_at == self.cycle:
                        #We cannot commit this instruction on this cycle
                        continue
                    #The line below in combination with >= 0 is the fix for the bug
                    if self.most_recent_commit == None:
                        self.most_recent_commit = reorder_buffer_sorted[0]

                    if reorder_buffer_sorted[i].issued_at >= self.most_recent_commit.issued_at:
                        self.log.add(LogType.SIM_CHECK_COMMIT,
                                f"\tInstruction {reorder_buffer_sorted[i].tostr()} is ready to commit. Issued at {reorder_buffer_sorted[i].issued_at}, most recent commit was at {self.most_recent_commit.issued_at}")
                        self.most_recent_commit = reorder_buffer_sorted[i]
                        reorder_buffer_sorted[i].committed_at = self.cycle
                        self.reorder_buffer.remove(reorder_buffer_sorted[i])
                        self.log.add(LogType.SIM_COMMIT_SUCCESS,
                                f"(Cycle {self.cycle}) Committed instruction {reorder_buffer_sorted[i].tostr()}")
                        break
