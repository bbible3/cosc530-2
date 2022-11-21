from instructiontypes import InstructionTypes, InstructionType, DefaultInstructionTypes
from log import Log, LogType
from instructions import Instruction
class Tracer:
    def __init__(self, filename, log=None, instruction_types=None):
        self.filename = filename
        self.lines = []
        self.log = log
        self.instruction_types = instruction_types
        self.instruction_queue = []
        try:
            with open(filename, "r") as f:
                self.lines = f.readlines()
        except:
            print(f"Error: Could not open file {filename}")
            exit(1)
        if log is not None:
            self.log.add(LogType.TRACE_OPEN, f"Opened trace file {filename}")
            #How many lines did we read?
            self.log.add(LogType.TRACE_OPEN, f"Read {len(self.lines)} lines")

    def process(self):
        if len(self.lines) == 0:
            raise Exception("No lines to process")
            return
        #Read all lines in the trace.dat file

        for line in self.lines:
            #Split by spaces
            split = line.split(" ")
            #Remove the newline character
            split[-1] = split[-1].replace("\n", "")
            #Get the first element which is the instruction type
            command_text = split[0]
            #Find the instruction type in the instruction types
            command_type = self.instruction_types.find(command_text)

            params_subsection = None
            command_params = []
            
            if command_type is None:
                raise Exception(f"Unknown command {command_text}")
            else:
                #Log it
                if self.log is not None:
                    self.log.add(LogType.TRACE_COMMAND_MATCH, f"Matched command {command_text} to {command_type.name}")
                #For handling formatting spaces
                for section in split[1:]:
                    if section == "":
                        continue
                    else:
                        params_subsection = section

                if params_subsection is not None:
                    #Split by commas
                    command_params = params_subsection.split(",")
                    #This should be equivalent to command_type.num_params
                    if len(command_params) != command_type.num_params:
                        raise Exception(f"Command {command_text} ({command_type.name}) has {len(command_params)} parameters but should have {command_type.num_params}")
                    else:
                        #Log it
                        if self.log is not None:
                            self.log.add(LogType.TRACE_COMMAND_PARAM_EXTRACT, f"Extracted parameters. Command {command_text} has {len(command_params)} parameters")
                        #Create an Instruction to add to the queue
                        new_instruction = Instruction(command_type, command_params)
                        self.instruction_queue.append(new_instruction)
                        if self.log is not None:
                            self.log.add(LogType.TRACE_COMMAND_QUEUE_ADD, f"Added instruction {command_text} to queue")

        